import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pandas as pd
import pytest
from microsoft.connectors.api import MicrosoftResponse, MSGraphAPI
from openai import RateLimitError

from sepp import sepp_main as mut
from sepp.commons import (
    Results,
)
from sepp.exceptions import (
    EmailFromBuchhaltung,
    NoAttachmentFoundError,
    NoBuchhaltungsNummerFoundError,
    NoPDForXLSXError,
    UnauthorizedUser,
)
from sepp.scripts.mailing_script import Email
from sepp.settings import FAILED_ID


@pytest.fixture
def dummy_response() -> MicrosoftResponse:
    """Fixture to provide a dummy response for testing."""
    return MicrosoftResponse(
        success=True, value=["dummy_value"], info="Dummy response for testing"
    )


@pytest.fixture
def fake_msgraph(monkeypatch: Mock) -> Mock:
    return Mock(spec=MSGraphAPI)


@pytest.fixture
def fake_logger(monkeypatch: Mock) -> Mock:
    fake = Mock()
    monkeypatch.setattr(mut, "logger", fake)
    return fake


@pytest.fixture
def fake_send_error(monkeypatch: Mock) -> Mock:
    fake = Mock()
    monkeypatch.setattr(mut, "send_error_email", fake)
    return fake


@pytest.fixture
def fake_send_failed_email(monkeypatch: Mock) -> Mock:
    fake = Mock()
    monkeypatch.setattr(mut, "send_failed_email", fake)
    return fake


@pytest.fixture
def pdf_path(tmp_path: Path) -> Path:
    p = tmp_path / "test.pdf"
    p.write_bytes(b"%PDF-1.4 dummy")
    return p


@pytest.fixture
def fake_sleep(monkeypatch: Mock) -> Mock:
    fake = Mock()
    monkeypatch.setattr(mut.time, "sleep", fake)
    return fake


@pytest.fixture
def fake_move_to_failed_folder(monkeypatch: Mock) -> Mock:
    fake = Mock()
    monkeypatch.setattr(mut, "move_failed_mail", fake)
    return fake


def test_fetch_unread_emails_success(
    monkeypatch: Mock, dummy_response: MicrosoftResponse
) -> None:
    # Arrange: replace msgraph.get_unread_emails with a stub that returns dummy_response
    fake_msgraph = Mock(get_unread_emails=Mock(return_value=dummy_response))

    # Act
    result = mut.fetch_unread_emails(fake_msgraph)

    # Assert
    assert result is dummy_response
    fake_msgraph.get_unread_emails.assert_called_once_with()


def test_fetch_unread_emails_exception(
    monkeypatch: Mock,
    fake_logger: Mock,
    fake_send_error: Mock,
    caplog: Mock,
) -> None:
    # Arrange: make get_unread_emails raise
    error = Exception("boom")

    fake_msgraph = Mock(get_unread_emails=Mock(side_effect=error))

    caplog.set_level("ERROR", logger=mut.__name__)
    # Act
    result = mut.fetch_unread_emails(fake_msgraph)

    # Assert: returned MicrosoftResponse has the fallback “empty” payload
    assert isinstance(result, MicrosoftResponse)
    assert result.success is True
    assert result.value == []
    assert result.info == "Unexpected error fetching unread emails"

    # logger.exception should be called with that same message
    fake_logger.exception.assert_called_once_with(
        "Unexpected error fetching unread emails"
    )

    # send_error_email gets the msgraph instance and the error message
    fake_send_error.assert_called_once_with(
        fake_msgraph, "Unexpected error fetching unread emails"
    )


def test_ms_graph_response_unsuccessful(
    fake_logger: Mock,
    fake_msgraph: Mock,
    fake_send_error: Mock,
    caplog: Mock,
) -> None:
    # Arrange
    response_unccessful = MicrosoftResponse(
        success=False, value=[], info="Error occurred"
    )

    # Act
    result = mut.ms_graph_response_unsuccessful(fake_msgraph, response_unccessful)

    # Assert
    error_msg = f"Failed to retrieve emails from sepp@kolibrain.de via the msgraph API: {response_unccessful.info}"

    assert result is True
    fake_logger.error.assert_called_once_with(error_msg)
    fake_send_error.assert_called_once_with(fake_msgraph, error_msg)

    caplog.set_level("ERROR", logger=mut.__name__)
    response_successful = MicrosoftResponse(
        success=True, value=["email1", "email2"], info="Success"
    )

    result = mut.ms_graph_response_unsuccessful(fake_msgraph, response_successful)
    assert result is False


def test_wrap_email() -> None:
    email = {
        "id": "123",
        "subject": "Test Subject",
        "sender": {"emailAddress": {"address": "test_address"}},
        "sentDateTime": "test_date",
        "internetMessageId": "test_message_id",
        "body": {"content": "Test Body"},
        "hasAttachments": True,
    }

    email_obj = mut.wrap_email(email)
    assert isinstance(email_obj, Email)
    assert email_obj.message_id == "123"
    assert email_obj.subject == "Test Subject"
    assert email_obj.sender == "test_address"
    assert email_obj.sent_date == "test_date"
    assert email_obj.unique_id == "test_message_id"
    assert email_obj.content == "Test Body"
    assert email_obj.has_attachment is True


def test_wrap_email_with_missing_fields() -> None:
    email = {
        "id": "123",
        "sender": {"emailAddress": {"address": "test_address"}},
        "sentDateTime": "test_date",
        "internetMessageId": "test_message_id",
        "body": {"content": "Test Body"},
        # Missing 'subject', and 'hasAttachments' fields
    }

    email_obj = mut.wrap_email(email)
    assert isinstance(email_obj, Email)
    assert email_obj.message_id == "123"
    assert email_obj.subject == "<KEIN BETREFF>"
    assert email_obj.sender == "test_address"
    assert email_obj.sent_date == "test_date"
    assert email_obj.unique_id == "test_message_id"
    assert email_obj.content == "Test Body"
    assert email_obj.has_attachment == []


def test_save_llm_response_to_json(tmp_path: Path, fake_logger: Mock) -> None:
    # Arrange
    file_name = "sample.pdf"
    llm_response = {"foo": "bar", "score": 0.88}
    raw_text = "This is the extracted PDF text."
    saving_path = tmp_path  # pytest provides a temp directory

    # Enable INFO-level logging capture

    # Act
    mut.save_llm_response_to_json(file_name, llm_response, raw_text, saving_path)

    # The function appends "_llm_response.json" to the stem of file_name
    expected_filename = "sample_llm_response.json"
    expected_path = saving_path / expected_filename

    # Assert file was created
    assert expected_path.exists(), (
        f"Expected JSON file at {expected_path} but none found."
    )

    # Assert file contents
    content = expected_path.read_text(encoding="utf-8")
    data = json.loads(content)
    assert data["file_name"] == file_name
    assert data["model_output"] == llm_response
    assert data["raw_text"] == raw_text

    # Assert logging message
    fake_logger.info.assert_called_once_with(
        "Saving LLM response to JSON file: %s", expected_filename
    )


def test_handle_emails_without_attachments(
    fake_msgraph: Mock, fake_logger: Mock, fake_send_failed_email: Mock
) -> None:
    email = Email(
        has_attachment=False,
    )
    exception = NoAttachmentFoundError("No attachment found in the email.")
    mut.handle_emails_without_attachments(fake_msgraph, email, exception)
    fake_logger.exception.assert_called_once_with(
        "%s. Customer will be notified. Email is marked as read", exception
    )
    fake_send_failed_email.assert_called_once_with(
        ms_graph=fake_msgraph,
        email=email,
        explanation=(
            "\n Ursache: Ich konnte für diese Mail leider keinen Anhang (.pdf oder .xlsx) finden. "
            "Bitte überprüft die Mail nochmal"
        ),
    )
    fake_msgraph.mark_email_as_read.assert_called_once_with(email.message_id)


def test_handle_not_authorized_users(fake_msgraph: Mock, fake_logger: Mock) -> None:
    email = Email(
        sender="123",
    )
    exception = UnauthorizedUser("User is not authorized.")
    mut.handle_not_authorized_users(fake_msgraph, email, exception)
    fake_logger.exception.assert_called_once_with(
        "%s. Email sender will be notified. Email is marked as read", exception
    )
    fake_msgraph.send_email.assert_called_once_with(
        ["123"],
        "Nutzer nicht registriert",
        """Sehr geehrte Damen und Herren,
                        \nSie sind nicht also Nutzer für diesen Dienst zugelassen.
                        \nIch habe meinen Administrator informiert und dieser wird sich in Kürze mit Ihnen in Verbindung setzen.
                        \nMit freundlichen Grüßen,\nSEPP
                        """,
    )
    fake_msgraph.mark_email_as_read.assert_called_once_with(email.message_id)


def test_handle_no_pdf_xlxs_error(
    fake_msgraph: Mock, fake_logger: Mock, fake_send_failed_email: Mock
) -> None:
    email = Email()
    exception = NoPDForXLSXError("No PD found for XLSX attachment.")
    error_message = (
        "\n Ursache: Ich konnte für diese Mail leider keinen Anhang (.pdf oder .xlsx) finden. "
        "Bitte überprüft die Mail nochmal"
    )
    mut.handle_no_pdf_xlsx_error(fake_msgraph, email, exception)
    fake_logger.exception.assert_called_once_with(
        "%s. Customer will be notified. Email is marked as read", exception
    )
    fake_send_failed_email.assert_called_once_with(
        ms_graph=fake_msgraph,
        email=email,
        explanation=error_message,
    )
    fake_msgraph.mark_email_as_read.assert_called_once_with(email.message_id)


def test_unexpected_error_handler(
    fake_msgraph: Mock,
    fake_logger: Mock,
    fake_send_error: Mock,
    fake_send_failed_email: Mock,
) -> None:
    email = Email()
    exception = Exception("Unexpected error occurred.")

    error_msg = f"Unexpected error processing email {email.info}: {exception}\nEmail is marked as read and moved to 'FAILED' folder"
    message_to_customer = f"SEPP konnte leider nicht die PDF von der Email gesendet von {email.sender} am {email.sent_date} mit dem Betreff {email.subject} verarbeiten."
    mut.unexpected_error_handler(fake_msgraph, email, exception)

    fake_logger.exception.assert_called_once_with(
        "%s. Customer and admins will be notified. Email is marked as read and moved to 'FAILED' folder",
        error_msg,
    )
    fake_send_error.assert_called_once_with(
        ms_graph=fake_msgraph,
        error_msg=error_msg,
    )
    fake_send_failed_email.assert_called_once_with(
        ms_graph=fake_msgraph,
        email=email,
        explanation=message_to_customer,
    )
    fake_msgraph.mark_email_as_read.assert_called_once_with(email.message_id)
    fake_msgraph.move_email.assert_called_once_with(
        email.message_id, destination_folder=FAILED_ID
    )


def test_update_soloplan_with_buchhaltungsnummer(
    fake_logger: Mock, fake_send_error: Mock, fake_msgraph: Mock
) -> None:
    contacts: list[tuple[str, str]] = []
    fake_soloplan = Mock()

    # Test with empty contacts
    mut.update_soloplan_with_buchhaltungsnummer(fake_msgraph, contacts, fake_soloplan)

    fake_logger.info.assert_called_once_with("No new Buchhaltungsnummer found.")

    contacts = [("foo", "123")]

    mut.update_soloplan_with_buchhaltungsnummer(fake_msgraph, contacts, fake_soloplan)
    # Assert soloplan.update_buchhaltungsnummer was called with the correct parameters
    fake_soloplan.update_Buchhaltungsnummer_Soloplan.assert_called_once_with(
        "foo", "123"
    )

    erroneous_contacts: list[str] = [("foo")]
    mut.update_soloplan_with_buchhaltungsnummer(
        fake_msgraph, erroneous_contacts, fake_soloplan
    )
    fake_logger.exception.assert_called_once_with(
        "Error updating Soloplan with Buchhaltungsnummer"
    )
    fake_send_error.assert_called_once_with(
        ms_graph=fake_msgraph,
        error_msg="Error updating Soloplan with Buchhaltungsnummer: Contact tuple in new contacts list must have exactly 2 elements",
    )


def test_write_results_to_csv_exists(tmp_path: Path) -> None:
    results = Results(
        id="1",
        email_subject="N/A",
        sent_on="N/A",
        sender="N/A",
        attachment=False,
        llm_status="N/A",
        client="N/A",
        found_in="N/A",
        order_id="N/A",
        new_contacts=[],
        transport_order_number="N/A",
        order_already_exists=False,
        time_attachment_found="N/A",
        time_of_llm_response="N/A",
        time_soloplan_booked="N/A",
        oppel_info_mail="N/A",
        error_mail="N/A",
    )

    (tmp_path / "results.csv").touch()  # Create an empty file for testing
    csv_file = tmp_path / "results.csv"

    mut.write_results_to_csv(results, csv_file)

    assert (tmp_path / "results.csv").exists()

    results_df = pd.read_csv(tmp_path / "results.csv")
    assert not results_df.empty
    assert results_df.shape[0] == 1  # One row for the single result
    assert results_df.columns.tolist() == [
        "id",
        "email_subject",
        "sent_on",
        "sender",
        "attachment",
        "llm_status",
        "client",
        "found_in",
        "order_id",
        "new_contacts",
        "transport_order_number",
        "order_already_exists",
        "time_attachment_found",
        "time_of_llm_response",
        "time_soloplan_booked",
        "oppel_info_mail",
        "error_mail",
    ]

    mut.write_results_to_csv(results, csv_file)
    assert results_df.shape[0] == 1  # Same id should not create a new row


def test_write_results_to_csv_new(tmp_path: Path) -> None:
    results = Results(
        id="1",
        email_subject="N/A",
        sent_on="N/A",
        sender="N/A",
        attachment=False,
        llm_status="N/A",
        client="N/A",
        found_in="N/A",
        order_id="N/A",
        new_contacts=[],
        transport_order_number="N/A",
        order_already_exists=False,
        time_attachment_found="N/A",
        time_of_llm_response="N/A",
        time_soloplan_booked="N/A",
        oppel_info_mail="N/A",
        error_mail="N/A",
    )

    csv_file = tmp_path

    mut.write_results_to_csv(results, csv_file)

    assert (tmp_path / "sepp-dokumentation.csv").exists()
    results_df = pd.read_csv(tmp_path / "sepp-dokumentation.csv")
    assert not results_df.empty
    assert results_df.shape[0] == 1  # One row for the single result


def test_notify_buchhaltung(monkeypatch: Mock, fake_msgraph: Mock) -> None:
    contacts_list = [
        ("123456", "1412345"),
    ]
    pdf_path = Path("dummy.pdf")
    fake_send_email_to_buchhaltung = Mock()
    monkeypatch.setattr(
        mut, "send_email_to_buchhaltung", fake_send_email_to_buchhaltung
    )
    mut.notify_buchhaltung(fake_msgraph, contacts_list, pdf_path)
    fake_send_email_to_buchhaltung.assert_called_once_with(
        ms_graph=fake_msgraph,
        businesscontact=contacts_list,
        pdf_path=pdf_path,
    )

    fake_send_email_to_buchhaltung.reset_mock()
    empty_list: list = []
    mut.notify_buchhaltung(fake_msgraph, empty_list, pdf_path)
    fake_send_email_to_buchhaltung.assert_not_called()


def test_extract_information_from_pdf_success(
    monkeypatch: Mock,
    fake_msgraph: Mock,
    fake_logger: Mock,
    pdf_path: Path,
    fake_sleep: Mock,
) -> None:
    email = Email()
    results = Results()
    # Arrange: make get_llm_response return immediately
    expected = ({"client": {"name": "test_name"}, "order_id": "123"}, "raw text")
    get_mock = Mock(return_value=expected)
    monkeypatch.setattr(mut, "get_llm_response", get_mock)

    fake_sleep()
    # Act
    out = mut.extract_information_from_pdf(
        fake_msgraph,
        email,
        pdf_path,
        results,
        saving_path=pdf_path.parent,
    )

    # Assert
    assert out == expected
    get_mock.assert_called_once_with(pdf_path=pdf_path)
    fake_logger.exception.assert_not_called()
    assert results.llm_status == "Success"
    assert results.client == "test_name"
    assert results.order_id == "123"

    assert Path(pdf_path.parent / "test_llm_response.json").exists()

    with Path(pdf_path.parent / "test_llm_response.json").open(encoding="utf-8") as f:
        data = json.load(f)
    assert data == {
        "file_name": pdf_path.name,
        "model_output": {
            "client": {"name": "test_name"},
            "order_id": "123",
        },
        "raw_text": "raw text",
    }


def test_extract_information_from_pdf_429_then_success(
    monkeypatch: Mock,
    fake_msgraph: Mock,
    pdf_path: Path,
    fake_logger: Mock,
    fake_send_error: Mock,
) -> None:
    email = Email()
    results = Results()
    # Arrange: first call raises a 429 error, second call returns a good response
    err429 = RateLimitError(
        message="Error code 429: quota exceeded",
        response=Mock(status_code=429),
        body={"error": {"message": "out of tokens"}},
    )
    success = ({"result": "after retry"}, "raw after")

    get_mock = Mock(side_effect=[err429, success])
    monkeypatch.setattr(mut, "get_llm_response", get_mock)

    sleep_mock = Mock()
    monkeypatch.setattr(mut.time, "sleep", sleep_mock)
    # Act
    out = mut.extract_information_from_pdf(
        fake_msgraph, email, pdf_path, results, saving_path=pdf_path.parent
    )

    # Assert return value
    assert out == success

    # Should have retried exactly once
    expected_count = 2
    assert get_mock.call_count == expected_count
    get_mock.assert_any_call(pdf_path=pdf_path)

    # logger.exception called once with the 429 specific message
    fake_logger.exception.assert_called_once_with(
        "Error processing PDF with LLM (429 - out of tokens)"
    )

    # send_error_email called once with the “out of money” message
    fake_send_error.assert_called_once_with(
        ms_graph=fake_msgraph,
        error_msg="Hilfe, dem SEPP ist das Geld für ChatGPT ausgegangen!",
    )

    # time.sleep called once with the module SLEEP_INTERVAL
    sleep_mock.assert_called_once_with(300)


def test_extract_information_from_pdf_other_exception(
    monkeypatch: Mock,
    pdf_path: Path,
    fake_msgraph: Mock,
    fake_logger: Mock,
    fake_send_error: Mock,
    fake_send_failed_email: Mock,
) -> None:
    email = Email(sent_date="2023-10-01T12:00:00Z")
    results = Results()
    # Arrange: get_llm_response always raises some other error
    err = Exception("something bad")
    get_mock = Mock(side_effect=err)
    monkeypatch.setattr(mut, "get_llm_response", get_mock)

    sleep_mock = Mock()
    monkeypatch.setattr(mut.time, "sleep", sleep_mock)

    # Act
    out = mut.extract_information_from_pdf(
        fake_msgraph, email, pdf_path, results, saving_path=pdf_path.parent
    )

    # Assert we got the ({}, "") fallback
    assert out == ({}, "")

    # Only one attempt
    get_mock.assert_called_once_with(pdf_path=pdf_path)

    # logger.exception called once with the generic error
    fake_logger.exception.assert_called_once_with(
        "Unexpected error processing PDF with LLM"
    )

    # send_error_email called with a message containing the exception and filename
    error_msg = (
        f"Unexpected error processing PDF with LLM: {pdf_path.name} from {email.info}"
    )
    msg_to_customer = f"SEPP konnte leider nicht Informationen aus der PDF von der Email gesendet von {email.sender} am {email.sent_date} mit dem Betreff {email.subject} extrahieren."
    fake_send_error.assert_called_once_with(
        ms_graph=fake_msgraph,
        error_msg=error_msg,
        path_to_folder=pdf_path.parent,
    )
    fake_send_failed_email.assert_called_once_with(
        ms_graph=fake_msgraph,
        email=email,
        explanation=msg_to_customer,
        pdf_path=pdf_path,
    )

    # We should NOT sleep on non-429 errors
    sleep_mock.assert_not_called()


def test_process_email_to_order_success(
    monkeypatch: Mock,
    fake_msgraph: Mock,
    pdf_path: Path,
) -> None:
    email = Email(unique_id="<ABC-DEF@kolibrain.de>")
    results = Results()

    expected_results_id = (
        email.unique_id.split("@")[0].replace("<", "").replace(">", "")
    )

    fake_process_email = Mock(return_value=(pdf_path))
    monkeypatch.setattr(
        mut, "process_email_and_retrieve_transport_order", fake_process_email
    )
    # Act
    transport_order_pdf = mut.process_email_to_order(
        ms_graph=fake_msgraph,
        email=email,
        contacts_with_new_buchhaltungsnummer=[],
        email_processing_results=results,
        saving_path=pdf_path,
    )
    assert results.id == expected_results_id
    assert results.email_subject == email.subject
    assert results.sent_on == email.sent_date
    assert results.sender == email.sender

    assert transport_order_pdf == pdf_path


def test_process_email_to_order_unautorized(
    monkeypatch: Mock,
    fake_msgraph: Mock,
    pdf_path: Path,
) -> None:
    email = Email()
    results = Results()

    fake_process_email = Mock(
        side_effect=UnauthorizedUser("User not authorized"),
    )
    monkeypatch.setattr(
        mut, "process_email_and_retrieve_transport_order", fake_process_email
    )
    # Act
    handle_not_authorized_users = Mock()
    monkeypatch.setattr(mut, "handle_not_authorized_users", handle_not_authorized_users)

    result = mut.process_email_to_order(
        ms_graph=fake_msgraph,
        email=email,
        contacts_with_new_buchhaltungsnummer=[],
        email_processing_results=results,
        saving_path=pdf_path,
    )
    # Assert
    assert result is None
    handle_not_authorized_users.assert_called_once_with(
        fake_msgraph, email, fake_process_email.side_effect
    )


def test_process_email_to_order_no_attachment(
    monkeypatch: Mock,
    fake_msgraph: Mock,
    pdf_path: Path,
) -> None:
    email = Email()
    results = Results()

    fake_process_email = Mock(
        side_effect=NoAttachmentFoundError("No attachment found"),
    )
    monkeypatch.setattr(
        mut, "process_email_and_retrieve_transport_order", fake_process_email
    )
    # Act
    handle_emails_without_attachments = Mock()
    monkeypatch.setattr(
        mut, "handle_emails_without_attachments", handle_emails_without_attachments
    )

    result = mut.process_email_to_order(
        ms_graph=fake_msgraph,
        email=email,
        contacts_with_new_buchhaltungsnummer=[],
        email_processing_results=results,
        saving_path=pdf_path,
    )
    # Assert
    assert result is None
    handle_emails_without_attachments.assert_called_once_with(
        fake_msgraph, email, fake_process_email.side_effect
    )


def test_process_email_to_order_no_buchhaltungsnummer(
    monkeypatch: Mock,
    fake_msgraph: Mock,
    fake_send_error: Mock,
    pdf_path: Path,
) -> None:
    email = Email()
    results = Results()
    e = "No Buchhaltungsnummer found"
    fake_process_email = Mock(
        side_effect=NoBuchhaltungsNummerFoundError(e),
    )
    monkeypatch.setattr(
        mut, "process_email_and_retrieve_transport_order", fake_process_email
    )

    result = mut.process_email_to_order(
        ms_graph=fake_msgraph,
        email=email,
        contacts_with_new_buchhaltungsnummer=[],
        email_processing_results=results,
        saving_path=pdf_path,
    )
    # Assert
    assert result is None
    fake_send_error.assert_called_once_with(
        ms_graph=fake_msgraph,
        error_msg=f"Error processing email {email.info}: {e}.",
    )
    fake_msgraph.mark_email_as_read.assert_called_once_with(email.message_id)


def test_process_email_to_order_no_valid_attachment(
    monkeypatch: Mock,
    fake_msgraph: Mock,
    pdf_path: Path,
) -> None:
    email = Email()
    results = Results()
    e = f"No valid .pdf or .xlsx attachments found in email: {email.info}"
    fake_process_email = Mock(
        side_effect=NoPDForXLSXError(e),
    )
    monkeypatch.setattr(
        mut, "process_email_and_retrieve_transport_order", fake_process_email
    )

    fake_handle_no_pdf_xlsx_error = Mock()
    monkeypatch.setattr(mut, "handle_no_pdf_xlsx_error", fake_handle_no_pdf_xlsx_error)

    result = mut.process_email_to_order(
        ms_graph=fake_msgraph,
        email=email,
        contacts_with_new_buchhaltungsnummer=[],
        email_processing_results=results,
        saving_path=pdf_path,
    )
    # Assert
    assert result is None
    fake_handle_no_pdf_xlsx_error.assert_called_once_with(
        fake_msgraph, email, fake_process_email.side_effect
    )


def test_process_email_to_order_other_exception(
    monkeypatch: Mock,
    fake_msgraph: Mock,
    pdf_path: Path,
) -> None:
    email = Email()
    results = Results()
    e = "Some other error occurred"
    fake_process_email = Mock(
        side_effect=Exception(e),
    )
    monkeypatch.setattr(
        mut, "process_email_and_retrieve_transport_order", fake_process_email
    )

    fake_unexpected_error_handler = Mock()
    monkeypatch.setattr(mut, "unexpected_error_handler", fake_unexpected_error_handler)

    result = mut.process_email_to_order(
        ms_graph=fake_msgraph,
        email=email,
        contacts_with_new_buchhaltungsnummer=[],
        email_processing_results=results,
        saving_path=pdf_path,
    )
    # Assert
    assert result is None
    fake_unexpected_error_handler.assert_called_once_with(
        fake_msgraph, email, fake_process_email.side_effect
    )


def test_process_email_to_order_email_from_buchhaltung(
    monkeypatch: Mock,
    fake_msgraph: Mock,
    pdf_path: Path,
    fake_logger: Mock,
) -> None:
    fake_process_email_and_retrieve_transport_order = Mock(
        side_effect=EmailFromBuchhaltung("Email is from Buchhaltung.")
    )
    monkeypatch.setattr(
        mut,
        "process_email_and_retrieve_transport_order",
        fake_process_email_and_retrieve_transport_order,
    )

    email = Email()
    result = mut.process_email_to_order(
        ms_graph=fake_msgraph,
        email=email,
        contacts_with_new_buchhaltungsnummer=[],
        email_processing_results=Results(),
        saving_path=pdf_path,
    )
    fake_logger.exception.assert_called_with(
        msg=fake_process_email_and_retrieve_transport_order.side_effect
    )
    fake_msgraph.mark_email_as_read.assert_called_once_with(email.message_id)
    assert result is None


def test_creates_csv_when_missing(tmp_path: Path, monkeypatch: Mock) -> None:
    # Arrange: point BASE_DIR at a temp dir
    monkeypatch.setattr(mut, "BASE_DIR", tmp_path)
    csv_path = tmp_path / "soloplan_retries_df.csv"

    # Precondition: file does not exist
    assert not csv_path.exists()

    # Act
    mut.create_retries_csv()

    # Assert: file now exists
    assert csv_path.exists(), "CSV file should be created when missing"

    # Read and inspect
    test_df = pd.read_csv(csv_path, parse_dates=["last_retry"])
    # It should be empty, but have the correct columns
    assert list(test_df.columns) == ["unique_email_id", "retries", "last_retry"]
    assert test_df.empty, "DataFrame should have zero rows"


def test_does_nothing_if_csv_already_exists(tmp_path: Path, monkeypatch: Mock) -> None:
    # Arrange
    monkeypatch.setattr(mut, "BASE_DIR", tmp_path)
    csv_path = tmp_path / "soloplan_retries_df.csv"

    # Create an existing file with one row
    existing = pd.DataFrame(
        {
            "unique_email_id": ["foo"],
            "retries": [3],
            "last_retry": [pd.Timestamp("2025-06-19T12:00:00")],
        }
    )
    existing.to_csv(csv_path, index=False)

    # Act
    mut.create_retries_csv()

    # Assert: file still exists and content unchanged
    df_after = pd.read_csv(csv_path, parse_dates=["last_retry"])
    pd.testing.assert_frame_equal(df_after, existing)


def test_email_cannot_be_retried_no_retries(
    tmp_path: Path,
    monkeypatch: Mock,
    fake_msgraph: Mock,
    fake_logger: Mock,
    pdf_path: Mock,
) -> None:
    # Arrange: point BASE_DIR at a temp dir
    monkeypatch.setattr(mut, "BASE_DIR", tmp_path)
    csv_path = tmp_path / "soloplan_retries_df.csv"

    # Precondition: file does not exist
    assert not csv_path.exists()

    existing = pd.DataFrame(
        {
            "unique_email_id": ["foo"],
            "retries": [1],
            "last_retry": [
                pd.Timestamp("2025-06-19T12:00:00", tz=ZoneInfo("Europe/Berlin"))
            ],
        }
    )

    existing.to_csv(csv_path, index=False)

    email = Email(unique_id="bar")

    result = mut.email_cannot_be_retried(email, fake_msgraph, pdf_file_path=pdf_path)
    fake_logger.info.assert_called_once_with(
        "Email has not been retried before.  Proceeding with processing...",
    )
    assert result is False


def test_email_cannot_be_retried_too_many_retries(
    tmp_path: Path,
    monkeypatch: Mock,
    fake_msgraph: Mock,
    fake_logger: Mock,
    pdf_path: Mock,
    fake_send_error: Mock,
    fake_send_failed_email: Mock,
    fake_move_to_failed_folder: Mock,
) -> None:
    # Arrange: point BASE_DIR at a temp dir
    monkeypatch.setattr(mut, "BASE_DIR", tmp_path)
    csv_path = tmp_path / "soloplan_retries_df.csv"

    # Precondition: file does not exist
    assert not csv_path.exists()

    existing = pd.DataFrame(
        {
            "unique_email_id": ["foo"],
            "retries": [mut.MAX_EMAIL_RETRIES + 1],
            "last_retry": [
                pd.Timestamp("2025-06-19T12:00:00", tz=ZoneInfo("Europe/Berlin"))
            ],
        }
    )

    existing.to_csv(csv_path, index=False)

    email = Email(unique_id="foo")

    result = mut.email_cannot_be_retried(email, fake_msgraph, pdf_file_path=pdf_path)
    fake_logger.warning.assert_called_once_with(
        "Email has reached the maximum number of retries.\n"
        "Marking email as read and moving to 'FAILED' folder.\n"
        "Sending error email to admins and failed email to customer.",
    )
    fake_msgraph.mark_email_as_read.assert_called_once_with(email.message_id)
    fake_move_to_failed_folder.assert_called_once_with(fake_msgraph, email)
    message_to_customer = "SEPP konnte den Auftrag leider nicht anlegen, da Soloplan CarLo einen Fehler zurückgegeben hat"
    fake_send_failed_email.assert_called_once_with(
        ms_graph=fake_msgraph,
        email=email,
        explanation=message_to_customer,
        pdf_path=pdf_path,
    )
    message_to_admins = (
        f"{email.info} could not be processed because of consistent Soloplan 'Search and creation' errors.\n"
        "It has reached the maximum number of retries and has been moved to the failed folder."
    )
    fake_send_error.assert_called_once_with(
        fake_msgraph,
        message_to_admins,
    )

    assert result is True


def test_email_cannot_be_retried_too_early(
    fake_logger: Mock, monkeypatch: Mock, tmp_path: Path, pdf_path: Mock
) -> None:
    monkeypatch.setattr(mut, "BASE_DIR", tmp_path)
    csv_path = tmp_path / "soloplan_retries_df.csv"

    # Precondition: file does not exist
    assert not csv_path.exists()

    existing = pd.DataFrame(
        {
            "unique_email_id": ["foo"],
            "retries": [mut.MAX_EMAIL_RETRIES - 1],
            "last_retry": [datetime.now(tz=ZoneInfo("Europe/Berlin"))],
        }
    )

    existing.to_csv(csv_path, index=False)

    email = Email(unique_id="foo")

    result = mut.email_cannot_be_retried(email, fake_msgraph, pdf_file_path=pdf_path)
    fake_logger.info.assert_called_once_with(
        "Email has already been retried recently. Skipping further processing.",
    )
    assert result is True


def test_email_cannot_be_retried_retry(
    fake_logger: Mock, monkeypatch: Mock, tmp_path: Path, pdf_path: Mock
) -> None:
    monkeypatch.setattr(mut, "BASE_DIR", tmp_path)
    csv_path = tmp_path / "soloplan_retries_df.csv"

    # Precondition: file does not exist
    assert not csv_path.exists()

    existing = pd.DataFrame(
        {
            "unique_email_id": ["foo"],
            "retries": [mut.MAX_EMAIL_RETRIES - 1],
            "last_retry": [
                pd.Timestamp("2025-06-19T12:00:00", tz=ZoneInfo("Europe/Berlin"))
            ],
        }
    )

    existing.to_csv(csv_path, index=False)

    email = Email(unique_id="foo")

    result = mut.email_cannot_be_retried(email, fake_msgraph, pdf_file_path=pdf_path)
    fake_logger.info.assert_called_once_with(
        "Email has been retried before but more than %d minutes ago. Proceeding with processing...",
        mut.MINS_BEFORE_RETRY,
    )
    assert result is False
