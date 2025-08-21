import csv
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pytest
from microsoft.connectors.api import MicrosoftResponse, MSGraphAPI

import sepp.scripts.mailing_script as mut
from sepp.settings import FAILED_ID


def read_bytes(file_path: Path) -> bytes:
    """Reads the content of a file and returns it as bytes."""
    with file_path.open("rb") as file:
        return file.read()


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
def pdf_path(tmp_path: Path) -> Path:
    p = tmp_path / "test.pdf"
    p.write_bytes(b"%PDF-1.4 dummy")
    return p


email = mut.Email()


def test_move_failed_mail(fake_msgraph: Mock, fake_logger: Mock) -> None:
    mut.move_failed_mail(fake_msgraph, email)

    fake_msgraph.mark_email_as_read.assert_called_once_with(email.message_id)
    fake_msgraph.move_email.assert_called_once_with(
        email.message_id, destination_folder=FAILED_ID
    )
    fake_logger.info.assert_called_once_with(
        "Moved email from %s sent on %s with subject '%s' to folder 'FAILED'",
        email.sender,
        email.sent_date,
        email.subject,
    )


def test_send_success_email(fake_msgraph: Mock, monkeypatch: Mock) -> None:
    date_time = datetime.now(tz=ZoneInfo("Europe/Berlin"))
    fake_date_time = Mock(spec=datetime)
    fake_date_time.now.return_value = date_time
    date = date_time.strftime("%d-%m-%Y").split(" ")[0]
    time = date_time.strftime("%H:%M").split(" ")[0]
    monkeypatch.setattr(mut, "datetime", fake_date_time)
    client_name = "Test Client"
    transport_order_number = "12345"
    external_number = "54321"
    message = f"""Hallo Oppel-Team,
    \nich habe den Transportauftrag von {client_name} mit der Nummer {transport_order_number} und der Externen Nummer {external_number} am {date} um {time} erfasst.
    \nLiebe Grüße\nSEPP
    """

    mut.send_success_email(
        ms_graph=fake_msgraph,
        primary_recipient="john@mail.de",
        client_name=client_name,
        transport_order_number=transport_order_number,
        external_number=external_number,
    )

    fake_msgraph.send_email.assert_called_once_with(
        recipient_list=["john@mail.de"],
        subject=f"Sepp - Automatisch erstellter Transportauftrag von {client_name} (Nr. {transport_order_number})",
        message=message,
        bcc_list=["al-khazrage@kolibrain.de", "shlychkov@kolibrain.de"],
    )


def test_send_failed_email(
    fake_msgraph: Mock,
    monkeypatch: Mock,
    pdf_path: Path,
    fake_logger: Mock,
    fake_send_error: Mock,
    email: mut.Email = email,  # noqa: PT028
) -> None:
    recepient_list = [email.sender]
    bcc_list = ["al-khazrage@kolibrain.de", "shlychkov@kolibrain.de"]

    (date, time) = ("01-01-2023", "12:00")
    monkeypatch.setattr(mut, "germany_date_time", Mock(return_value=(date, time)))

    explanation = "This is a test explanation"

    subject = "SEPP Fehlermeldung"
    message_content = f"""Hallo Oppel-Team,
    \nich konnte den Transportauftrag, der mir am {date} um {time} mit dem Betreff <{email.subject}> zugeschickt wurde, leider nicht verarbeiten.
    {explanation}
    \nIhr findet den Transportauftrag den ich nicht verarbeiten konnte im Anhang an diese Mail.
    \nLiebe Grüße\nSEPP
    """

    message = mut.send_failed_email(
        ms_graph=fake_msgraph,
        email=email,
        explanation=explanation,
        pdf_path=None,
    )

    fake_msgraph.send_email.assert_called_once_with(
        recipient_list=recepient_list,
        subject=subject,
        message=message_content,
        bcc_list=bcc_list,
    )
    fake_msgraph.reset_mock()

    message = mut.send_failed_email(
        ms_graph=fake_msgraph,
        email=email,
        explanation=explanation,
        pdf_path=pdf_path,
    )

    fake_msgraph.send_email_with_attachment.assert_called_once_with(
        recipient_list=recepient_list,
        subject=subject,
        message=message_content,
        bcc_list=bcc_list,
        attachment_path=pdf_path.as_posix(),
    )

    fake_msgraph.send_email = Mock(
        return_value=MicrosoftResponse(
            success=False,
            value={},
            info="some error occurred",
        )
    )
    message = mut.send_failed_email(
        ms_graph=fake_msgraph,
        email=email,
        explanation=explanation,
        pdf_path=None,
    )

    assert isinstance(message, MicrosoftResponse)

    error_msg = f"ATTENTION - IMMEDIATE ACTION REQUIRED: The {email.info} was not processed successfully AND we failed to send an error message to the sender of the mail."
    fake_logger.error.assert_any_call(
        error_msg
    )  # have to check via the message and not the call count because of downstream effects
    fake_send_error.assert_called_once_with(
        ms_graph=fake_msgraph,
        error_msg=error_msg,
    )


@pytest.fixture(autouse=True)
def isolate_base_dir(tmp_path: Path, monkeypatch: Mock) -> Path:
    """Redirect BASE_DIR to tmp_path for each test."""
    monkeypatch.setattr(mut, "BASE_DIR", tmp_path)
    return tmp_path


def test_send_error_email_attaches_latest_log(
    tmp_path: Path, fake_msgraph: Mock
) -> None:
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    log1 = logs_dir / "log1.log"
    log2 = logs_dir / "log2.log"

    log1.write_text("first")
    time.sleep(0.01)
    log2.write_text("second")

    error_msg = "Test error occurred"
    recipient_list = [
        "al-khazrage@kolibrain.de",
        "guemues@kolibrain.de",
        "shlychkov@kolibrain.de",
    ]

    mut.send_error_email(ms_graph=fake_msgraph, error_msg=error_msg)

    fake_msgraph.send_email_with_attachments.assert_called_once_with(
        recipient_list=recipient_list,
        subject="SEPP ERROR",
        message=error_msg + "\n\n",
        attachment_paths=[log2.as_posix()],
    )


def test_send_error_email_with_folder_and_cleanup(
    tmp_path: Path, monkeypatch: Mock, fake_msgraph: Mock, fake_logger: Mock
) -> None:
    # 1) Setup logs dir + a single .log
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    log = logs_dir / "only.log"
    log.write_text("logdata")

    # 2) Create a folder to zip
    folder = tmp_path / "myfolder"
    folder.mkdir()
    (folder / "file.txt").write_text("content")

    # 3) Stub NamedTemporaryFile in your module to yield a dummy context manager
    temp_name = str(tmp_path / "temp123.zip")

    class DummyTemp:
        def __init__(self, name: str) -> None:
            self.name = name

        def __enter__(self) -> "DummyTemp":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
            pass

    monkeypatch.setattr(
        mut,
        "tempfile",
        Mock(NamedTemporaryFile=lambda *a, **k: DummyTemp(temp_name)),
    )

    # 4) Stub make_archive in your module and create the fake archive file
    archive_path = str(tmp_path / "myarchive.zip")
    # Create the file so unlink succeeds
    Path(archive_path).write_bytes(b"")
    monkeypatch.setattr(
        mut,
        "shutil",
        Mock(make_archive=lambda base_name, fmt, root_dir, base_dir: archive_path),
    )

    error_msg = "Another error"
    recipient_list = [
        "al-khazrage@kolibrain.de",
        "guemues@kolibrain.de",
        "shlychkov@kolibrain.de",
    ]

    # Act
    mut.send_error_email(
        ms_graph=fake_msgraph,
        error_msg=error_msg,
        include_log=True,
        path_to_folder=folder,
    )

    # Verify attachments: log first, then archive
    fake_msgraph.send_email_with_attachments.assert_called_once_with(
        recipient_list=recipient_list,
        subject="SEPP ERROR",
        message=error_msg + "\n\n",
        attachment_paths=[log.as_posix(), archive_path],
    )

    # After sending, the archive file should have been deleted
    assert not Path(archive_path).exists()

    # And logger.info should have been called with the two-arg signature
    fake_logger.info.assert_any_call("Cleaned up temporary file: %s", archive_path)


def test_send_error_email_failure_logs_error(
    fake_msgraph: Mock, fake_logger: Mock
) -> None:
    # No logs or folder
    # Simulate failure
    fake_msgraph.send_email_with_attachments.return_value = MicrosoftResponse(
        value={}, success=False
    )

    mut.send_error_email(ms_graph=fake_msgraph, error_msg="Critical fail")

    fake_logger.error.assert_called_once_with(
        "Failed to send error message to al-khazrage@kolibrain.de and guemues@kolibrain.de"
    )


def test_send_email_to_buchhaltung(
    fake_msgraph: Mock, pdf_path: Path, fake_logger: Mock, monkeypatch: Mock
) -> None:
    businesscontact = [
        (
            {
                "name": "Test Company",
                "street": "Test Street",
                "houseNumber": "123",
                "zip": "12345",
                "city": "Test City",
            },
            123,
        )
    ]

    fake_write_csv = Mock(return_value=Path("test_buchhaltung.csv"))
    monkeypatch.setattr(mut, "write_csv_for_buchhaltung", fake_write_csv)

    message_content = """
            Sehr geehrte Damen und Herren,

            ich konnte den folgenden Geschäftspartner nicht in CarLo finden:

            Test Company
            Test Street 123
            12345 Test City

            Um ihn neu anlegen zu können brauche ich eine neue Geschäftspartnernummer.
            Bitte senden Sie diese Nummer also Antwort auf diese Nachricht.

            WICHTIG: Bitte nur die Nummer ohne weiteren Text oder Anhang senden.

            Liebe Grüße und vielen Dank
            SEPP
            """

    mut.send_email_to_buchhaltung(
        ms_graph=fake_msgraph,
        businesscontact=businesscontact,
        pdf_path=pdf_path,
    )

    fake_msgraph.send_email_with_attachments.assert_called_once_with(
        recipient_list=["fibu@spedition-oppel.de"],
        subject="Neuer Geschäftspartner (123)",
        message=message_content,
        attachment_paths=[pdf_path.as_posix(), Path("test_buchhaltung.csv").as_posix()],
        bcc_list=["al-khazrage@kolibrain.de"],
    )

    fake_msgraph.send_email_with_attachments = Mock(
        return_value=MicrosoftResponse(
            success=False,
            value={},
            info="some error occurred",
        )
    )
    mut.send_email_to_buchhaltung(
        ms_graph=fake_msgraph,
        businesscontact=businesscontact,
        pdf_path=pdf_path,
    )

    fake_logger.error.assert_called_once_with("Failed to send mail to Buchhaltung.")


def test_fetch_mail_attachments(
    fake_msgraph: Mock,
    fake_logger: Mock,
    email: mut.Email = email,  # noqa: PT028
) -> None:
    fake_msgraph.get_attachments.return_value = MicrosoftResponse(
        success=True,
        value={
            "name": "test.pdf",
            "content": "%PDF-1.4 dummy",
        },
    )

    attachments = mut.fetch_mail_attachments(fake_msgraph, email, attachment_type="pdf")
    fake_msgraph.get_attachments.assert_called_once_with(email.message_id, type="pdf")

    assert attachments["name"] == "test.pdf"
    assert attachments["content"] == "%PDF-1.4 dummy"

    fake_msgraph.get_attachments.return_value = MicrosoftResponse(
        success=False,
        value={
            "name": "test.pdf",
            "content": "%PDF-1.4 dummy",
        },
    )
    attachments = mut.fetch_mail_attachments(fake_msgraph, email, attachment_type="pdf")
    fake_logger.error.assert_called_once_with(
        "Failed to load attachments for %s via msgraph API", email.info
    )
    assert attachments == {}


@pytest.fixture
def setup_tmp_csv(tmp_path: Path, monkeypatch: Mock) -> tuple[list[list[str]], Path]:
    # Prepare a fake stammdaten CSV
    stammdat_csv = tmp_path / "stamm.csv"
    header_rows = [
        ["col1", "col2", "col3"],
        ["val1", "val2", "val3"],
        ["extra", "row", "here"],  # beyond the first two, should be ignored
    ]
    with stammdat_csv.open("w", newline="", encoding="windows-1252") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerows(header_rows)

    # Monkeypatch the module constants
    monkeypatch.setattr(mut, "STAMM_DATA_CSV", stammdat_csv)
    out_dir = tmp_path / "transport_orders_imgs"
    monkeypatch.setattr(mut, "OUTPUT_CSV_DIR", out_dir)

    return header_rows[:2], out_dir


def test_write_csv_for_buchhaltung_creates_output_dir_and_file(
    setup_tmp_csv: tuple[list[list[str]], Path],
) -> None:
    header_rows, out_dir = setup_tmp_csv
    name = "KundeX"
    street = "Hauptstr."
    house_number = "5A"
    zip_code = "12345"
    city = "Teststadt"

    # precondition: output dir does not exist
    assert not out_dir.exists()

    # Act
    result_path = mut.write_csv_for_buchhaltung(
        name=name,
        street=street,
        house_number=house_number,
        zip_code=zip_code,
        city=city,
    )

    # Assert: directory now exists
    assert out_dir.exists()
    assert out_dir.is_dir()
    # Assert: returned path is correct
    expected = out_dir / f"{name}.csv"
    assert result_path == expected
    assert expected.exists()


def test_write_csv_for_buchhaltung_output_file_contents(
    setup_tmp_csv: tuple[list[list[str]], Path],
) -> None:
    header_rows, out_dir = setup_tmp_csv
    name = "FooBar"
    street = "Beispielweg"
    house_number = "10"
    zip_code = "54321"
    city = "Musterstadt"

    # Act
    out_file = mut.write_csv_for_buchhaltung(name, street, house_number, zip_code, city)

    # Read back
    with out_file.open("r", newline="", encoding="windows-1252") as f:
        reader = list(csv.reader(f, delimiter=";"))

    # Should have exactly 3 rows: two header rows + new contact
    expected_len_reader = 3
    assert len(reader) == expected_len_reader

    # Header rows preserved
    assert reader[0] == header_rows[0]
    assert reader[1] == header_rows[1]

    # New contact row structure:
    new_row = reader[2]
    # It should start with "", name, then 12 empties, then address, "", zip, city:
    expected_prefix = ["", name] + [""] * 12
    expected_suffix = [f"{street} {house_number}", "", zip_code, city]
    assert new_row[: 2 + 12] == expected_prefix
    assert new_row[-4:] == expected_suffix

    # And total length matches the combined prefix + suffix lengths
    assert len(new_row) == len(expected_prefix) + len(expected_suffix)
