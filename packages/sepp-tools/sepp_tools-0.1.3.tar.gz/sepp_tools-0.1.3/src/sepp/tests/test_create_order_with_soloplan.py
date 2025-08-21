import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pandas as pd
import pytest
from microsoft.connectors.api import MSGraphAPI
from soloplan import SoloplanAPI
from soloplan.connectors.api import SoloplanResponse

import sepp.create_order_with_soloplan as mut
from sepp.commons import Results
from sepp.scripts.mailing_script import Email
from sepp.settings import BASE_DIR, ERLEDIGT_ID, FAILED_ID


@pytest.fixture
def fake_msgraph() -> Mock:
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
def fake_send_generic_email(monkeypatch: Mock) -> Mock:
    fake = Mock()
    monkeypatch.setattr(mut, "send_generic_email", fake)
    return fake


@pytest.fixture
def pdf_path(tmp_path: Path) -> Path:
    p = tmp_path / "test.pdf"
    p.write_bytes(b"%PDF-1.4 dummy")
    return p


@pytest.fixture
def results() -> Results:
    return Results()


@pytest.fixture
def email() -> Email:
    return Email()


test_llm_response = {"order_details": "Test order details"}
raw_pdf_text = "Raw text extracted from PDF"


@pytest.fixture
def fake_soloplan() -> Mock:
    return Mock(spec=SoloplanAPI)


with Path(f"{BASE_DIR}/src/sepp/tests/test_data/soloplan_order.json").open() as f:
    example_soloplan_order = json.load(f)

with Path(
    f"{BASE_DIR}/src/sepp/tests/test_data/soloplan_response_value.json"
).open() as f:
    example_soloplan_response_value = json.load(f)


def test_create_order_with_soloplan_success(
    fake_msgraph: Mock,
    tmp_path: Path,
    pdf_path: Mock,
    results: Results,
    email: Email,
    fake_soloplan: Mock,
) -> None:
    fake_soloplan.create_order.return_value = (
        SoloplanResponse(
            success=True,
            value=example_soloplan_response_value,
            info="Order created successfully.",
        ),
        example_soloplan_order,
        [("John Doe", "12345")],
        "CSV",
    )

    response_data, business_contacts_new = mut.create_order_with_soloplan(
        llm_response=test_llm_response,
        raw_pdf_text=raw_pdf_text,
        ms_graph=fake_msgraph,
        email=email,
        pdf_file_path=pdf_path,
        saving_path=tmp_path,
        soloplan=fake_soloplan,
        results=results,
        is_test=True,
    )
    assert response_data == {"Number": "181355", "ExternalNumber": "1144340"}
    assert business_contacts_new == [("John Doe", "12345")]

    assert results.found_in == "CSV"
    assert results.new_contacts == [("John Doe", "12345")]
    assert results.transport_order_number == "181355"

    assert Path(tmp_path / "test_soloplan_order.json").exists()


def test_create_order_with_soloplan_search_and_creation_error(
    tmp_path: Path,
    pdf_path: Mock,
    fake_msgraph: Mock,
    fake_logger: Mock,
    fake_send_error: Mock,
    monkeypatch: Mock,
    results: Results,
    email: Email,
) -> None:
    fake_soloplan = Mock(spec=SoloplanAPI)

    fake_soloplan.create_order.side_effect = ValueError(
        "both search and creation failed"
    )
    fake_update_retries_log = Mock()
    monkeypatch.setattr(mut, "update_retries_log", fake_update_retries_log)

    fake_date_time = Mock(spec=datetime)
    fake_date_time.now.return_value = datetime(
        2023, 10, 1, 12, 0, tzinfo=ZoneInfo("Europe/Berlin")
    )
    monkeypatch.setattr(mut, "datetime", fake_date_time)

    (
        response_data,
        business_contacts_new,
    ) = mut.create_order_with_soloplan(
        llm_response=test_llm_response,
        raw_pdf_text=raw_pdf_text,
        ms_graph=fake_msgraph,
        email=email,
        pdf_file_path=pdf_path,
        saving_path=tmp_path,
        soloplan=fake_soloplan,
        results=results,
        is_test=True,
    )

    error_msg = (
        f"Soloplan API has raised the 'Search and Creation' error while processing an {email.info}.\n"
        "The retries log for this email will be updated with the current time and the email will be retried in 2 minutes. The client is not notified at this point."
    )
    fake_logger.warning.assert_called_with(error_msg)

    fake_send_error.assert_called_once_with(
        ms_graph=fake_msgraph, error_msg=error_msg, path_to_folder=tmp_path
    )

    fake_update_retries_log.assert_called_once_with(
        unique_email_id=email.unique_id,
        last_retry=fake_date_time.now.return_value,
    )

    assert response_data == {}
    assert business_contacts_new == []


def test_create_order_with_soloplan_unknown_error(
    pdf_path: Mock,
    tmp_path: Path,
    fake_msgraph: Mock,
    fake_logger: Mock,
    fake_send_error: Mock,
    fake_send_failed_email: Mock,
    results: Results,
    email: Email,
) -> None:
    fake_soloplan = Mock(spec=SoloplanAPI)

    e = "some unknown error occurred"
    fake_soloplan.create_order.side_effect = Exception(e)

    (
        response_data,
        business_contacts_new,
    ) = mut.create_order_with_soloplan(
        llm_response=test_llm_response,
        raw_pdf_text=raw_pdf_text,
        ms_graph=fake_msgraph,
        email=email,
        pdf_file_path=pdf_path,
        saving_path=tmp_path,
        soloplan=fake_soloplan,
        results=results,
        is_test=True,
    )

    error_msg = (
        f"Soloplan API has raised an unexpected error while processing an {email.info}\n"
        f"Error: {e}\n"
        "Email will be marked as read, moved to the 'Failed' folder and the client will be notified."
    )
    message_to_customer = "SEPP konnte den Auftrag leider nicht anlegen, da Soloplan CarLo einen Fehler zurückgegeben hat"
    fake_logger.exception.assert_called_with(error_msg)

    fake_send_error.assert_called_once_with(
        ms_graph=fake_msgraph,
        error_msg=f"{error_msg}:\n{e}",
        path_to_folder=tmp_path,
    )

    fake_send_failed_email.assert_called_once_with(
        ms_graph=fake_msgraph,
        email=email,
        explanation=message_to_customer,
        pdf_path=pdf_path,
    )

    fake_msgraph.mark_email_as_read.assert_called_once_with(email.message_id)
    fake_msgraph.move_email.assert_called_once_with(
        email.message_id, destination_folder=FAILED_ID
    )

    assert response_data == {}
    assert business_contacts_new == []


def test_create_order_with_soloplan_order_already_exists(
    pdf_path: Mock,
    tmp_path: Path,
    fake_msgraph: Mock,
    fake_logger: Mock,
    fake_send_generic_email: Mock,
    results: Results,
    email: Email,
) -> None:
    fake_soloplan = Mock(spec=SoloplanAPI)

    fake_soloplan.create_order.return_value = (
        SoloplanResponse(
            success=False,
            value={
                "order_id": "12345",
                "status": "created",
            },
            info="as it already exists in Soloplan",
        ),
        {"order": "12345"},
        [],
        "test",
    )

    response_data, business_contacts_new = mut.create_order_with_soloplan(
        llm_response=test_llm_response,
        raw_pdf_text=raw_pdf_text,
        ms_graph=fake_msgraph,
        email=email,
        pdf_file_path=pdf_path,
        saving_path=tmp_path,
        soloplan=fake_soloplan,
        results=results,
        is_test=False,
    )
    order_number = test_llm_response.get("order_id", "")
    message = f"Der Auftrag {order_number} von {email.info}konnte nicht erneut angelegt werden, da er bereits existiert."
    fake_logger.info.assert_called_with("Order already exists in Soloplan")

    fake_msgraph.mark_email_as_read.assert_called_once_with(email.message_id)
    fake_send_generic_email.assert_called_once_with(
        ms_graph=fake_msgraph,
        primary_recipient=email.sender,
        message=message,
        bcc_list=["shlychkov@kolibrain.de"],
        subject=f"Auftrag {order_number} bereits existiert",
    )
    fake_msgraph.move_email.assert_called_once_with(
        email.message_id, destination_folder=ERLEDIGT_ID
    )

    assert response_data == {}
    assert business_contacts_new == []


def test_create_order_with_soloplan_not_success(
    pdf_path: Mock,
    tmp_path: Path,
    fake_msgraph: Mock,
    fake_logger: Mock,
    fake_send_error: Mock,
    fake_send_failed_email: Mock,
    results: Results,
    email: Email,
) -> None:
    fake_soloplan = Mock(spec=SoloplanAPI)

    response_within_api = SoloplanResponse(
        success=False,
        value={
            "order_id": "12345",
            "status": "created",
        },
        info="some error occurred",
    )

    fake_soloplan.create_order.return_value = (
        response_within_api,
        {"order": "12345"},
        [],
        "test",
    )

    response_data, business_contacts_new = mut.create_order_with_soloplan(
        llm_response=test_llm_response,
        raw_pdf_text=raw_pdf_text,
        ms_graph=fake_msgraph,
        email=email,
        pdf_file_path=pdf_path,
        saving_path=tmp_path,
        soloplan=fake_soloplan,
        results=results,
        is_test=False,
    )

    error_msg = (
        f"Soloplan returned a response but the model was unsuccessful: {response_within_api.info}\n"
        f"while processing an {email.info}.\n"
        "The email will be mark as read, moved to the 'Failed' folder and the client will be notified."
    )
    fake_logger.error.assert_called_with(error_msg)

    fake_msgraph.mark_email_as_read.assert_called_once_with(email.message_id)
    fake_send_error.assert_called_once_with(
        ms_graph=fake_msgraph,
        error_msg=error_msg,
        path_to_folder=tmp_path,
    )
    fake_msgraph.move_email.assert_called_once_with(
        email.message_id, destination_folder=FAILED_ID
    )
    fake_send_failed_email.assert_called_once_with(
        ms_graph=fake_msgraph,
        email=email,
        explanation="SEPP konnte leider den Auftrag leider nicht anlegen, da Soloplan CarLo einen Fehler zurückgegeben hat",
        pdf_path=pdf_path,
    )

    assert response_data == {}
    assert business_contacts_new == []


def test_save_json_with_soloplan_results(tmp_path: Path) -> None:
    # Arrange
    saving_dir = tmp_path / "out"
    saving_dir.mkdir()
    soloplan_resp = SoloplanResponse(
        success=True, value={"orderId": "XYZ", "status": "created"}, info="irrelevant"
    )
    order_json = {"foo": [1, 2, 3], "bar": "baz"}
    file_name = "invoice123.pdf"

    # Act
    mut.save_json_with_soloplan_results(
        soloplan_response=soloplan_resp,
        order_json=order_json,
        file_name=file_name,
        saving_path=saving_dir,
    )

    # Assert: JSONL file exists with expected name
    expected_file = saving_dir / "invoice123_soloplan_order.json"
    assert expected_file.exists(), f"{expected_file} was not created"

    # Read and parse
    content = expected_file.read_text()
    # Should be valid JSON plus a trailing newline
    assert content.endswith("\n")
    data = json.loads(content)

    # Check required keys
    assert "date" in data
    assert data["soloplan_success"] is True
    assert data["soloplan_response"] == soloplan_resp.value
    assert data["order_json"] == order_json

    # Date format DD.MM.YYYY HH:MM
    assert re.match(r"^\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}$", data["date"])


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # normal case with two entries
        (
            SoloplanResponse(
                success=True,
                value={
                    "dataSets": [
                        {
                            "defaultFilterValues": [
                                {"key": "foo", "value": 123},
                                {"key": "bar", "value": "baz"},
                            ]
                        }
                    ]
                },
            ),
            {"foo": 123, "bar": "baz"},
        ),
        # empty defaultFilterValues => empty dict
        (
            SoloplanResponse(
                success=True, value={"dataSets": [{"defaultFilterValues": []}]}
            ),
            {},
        ),
        # no dataSets at all => empty dict
        (
            SoloplanResponse(success=True, value={"dataSets": []}),
            {},
        ),
    ],
)
def test_get_soloplan_response_data_success(
    value: SoloplanResponse, expected: dict
) -> None:
    soloplan_response = value
    result = mut.get_soloplan_response_data(soloplan_response)
    assert result == expected


@pytest.mark.parametrize(
    ("value", "expected_call_msg"),
    [
        # missing dataSets key → KeyError
        ({}, "Error extracting data from Soloplan response"),
        # dataSets exists but empty → IndexError
        ({"dataSets": []}, "Error extracting data from Soloplan response"),
    ],
)
def test_get_soloplan_response_data_key_or_index_error(
    value: dict, fake_logger: Mock, expected_call_msg: str
) -> None:
    resp = SoloplanResponse(success=True, value=value, info="")
    out = mut.get_soloplan_response_data(resp)
    assert out == {}
    # Should log the KeyError/IndexError path
    fake_logger.exception.assert_called_once_with(expected_call_msg)


def test_get_soloplan_response_data_unexpected_error(fake_logger: Mock) -> None:
    # Arrange: value is None → TypeError when indexing
    resp = SoloplanResponse(success=True, value=None, info="")
    out = mut.get_soloplan_response_data(resp)
    assert out == {}
    # Should log the unexpected-error path
    fake_logger.exception.assert_called_once_with(
        "Unexpected error while extracting data from Soloplan response"
    )


def test_update_retries_log_new(tmp_path: Path, monkeypatch: Mock) -> None:
    # Arrange: point BASE_DIR at a temp dir
    monkeypatch.setattr(mut, "BASE_DIR", tmp_path)

    unique_id = "user123"
    first_retry = datetime(2025, 6, 20, 14, 30, tzinfo=ZoneInfo("Europe/Berlin"))

    # Act
    mut.update_retries_log(unique_id, first_retry)

    # Assert
    csv_path = tmp_path / "soloplan_retries_df.csv"
    assert csv_path.exists(), "CSV log file should be created when missing"

    test_df = pd.read_csv(csv_path, parse_dates=["last_retry"])
    assert len(test_df) == 1
    row = test_df.iloc[0]
    assert row["unique_email_id"] == unique_id
    assert row["retries"] == 1
    # `.to_pydatetime()` needed because pandas may use numpy datetime64
    assert row["last_retry"].to_pydatetime() == first_retry


def test_update_retries_log_increments_retries_and_updates_last_retry(
    tmp_path: Path, monkeypatch: Mock
) -> None:
    # Arrange
    monkeypatch.setattr(mut, "BASE_DIR", tmp_path)

    unique_id = "user123"
    first_retry = datetime(2025, 6, 20, 14, 30, tzinfo=ZoneInfo("Europe/Berlin"))
    mut.update_retries_log(unique_id, first_retry)

    # Act: call again with a later timestamp
    second_retry = first_retry + timedelta(hours=2)
    mut.update_retries_log(unique_id, second_retry)

    # Assert
    expected_retries = 2
    csv_path = tmp_path / "soloplan_retries_df.csv"
    test_df = pd.read_csv(csv_path, parse_dates=["last_retry"])
    assert len(test_df) == 1, "Should still have exactly one row for the same ID"
    row = test_df.iloc[0]
    assert row["unique_email_id"] == unique_id
    assert row["retries"] == expected_retries, "Retries count should have incremented"
    assert row["last_retry"].to_pydatetime() == second_retry


def test_multiple_unique_ids(tmp_path: Path, monkeypatch: Mock) -> None:
    # Arrange
    monkeypatch.setattr(mut, "BASE_DIR", tmp_path)
    id1 = "a@x.com"
    id2 = "b@y.com"
    t1 = datetime(2025, 6, 20, 10, 0, tzinfo=ZoneInfo("Europe/Berlin"))
    t2 = datetime(2025, 6, 20, 11, 0, tzinfo=ZoneInfo("Europe/Berlin"))

    # Act
    mut.update_retries_log(id1, t1)
    mut.update_retries_log(id2, t2)

    # Assert
    csv_path = tmp_path / "soloplan_retries_df.csv"
    test_df = pd.read_csv(csv_path, parse_dates=["last_retry"])
    expected_len = 2
    assert len(test_df) == expected_len
    # Check each row
    d = {r["unique_email_id"]: r for _, r in test_df.iterrows()}
    assert d[id1]["retries"] == 1
    assert d[id1]["last_retry"].to_pydatetime() == t1
    assert d[id2]["retries"] == 1
    assert d[id2]["last_retry"].to_pydatetime() == t2
