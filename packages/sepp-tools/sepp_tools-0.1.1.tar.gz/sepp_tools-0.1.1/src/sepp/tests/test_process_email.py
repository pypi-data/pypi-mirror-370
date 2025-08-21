from pathlib import Path
from unittest.mock import Mock, call

import pytest
from microsoft.connectors.api import MSGraphAPI

from sepp import process_email as mut
from sepp.scripts.mailing_script import Email


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


def test_email_from_unauthorized_users() -> None:
    email = Email(
        message_id="123",
        subject="Test Subject",
        sender="123",
        sent_date="2023-10-01T12:00:00Z",
        unique_id="test_message_id",
        content="Test Body",
        has_attachment=False,
    )

    result = mut.email_from_unauthorized_users(email)
    assert result is True

    email.sender = "@kolibrain.de"

    result = mut.email_from_unauthorized_users(email)
    assert result is False
    email.sender = "@spedition-oppel.de"
    result = mut.email_from_unauthorized_users(email)
    assert result is False


@pytest.mark.parametrize(
    ("email_content", "expected"),
    [
        # a valid Buchhaltungsnummer 14 + 5 digits in the div
        (
            "<html><body>"
            '<div class="elementToProof">'
            "Ihre Buchhaltungsnummer lautet: 1412345. Vielen Dank."
            "</div>"
            "</body></html>",
            # result:
            "1412345",
        ),
        # no matching 14xxxxx sequence in the div
        (
            "<html><body>"
            '<div class="elementToProof">'
            "Hier steht keine relevante Nummer."
            "</div>"
            "</body></html>",
            # result:
            None,
        ),
        # multiple numbers—should pick the first valid one
        (
            '<div class="elementToProof">Erste 1412345, zweite 1499999</div>',
            # result:
            "1412345",
        ),
    ],
)
def test_parse_buchhaltungsnummer(email_content: str, expected: str) -> None:
    assert mut.parse_buchhaltungsnummer(email_content) == expected


def test_email_from_buchhaltung() -> None:
    subject = "Ihre Buchhaltungsnummer"
    result = mut.email_from_buchhaltung(subject)
    assert result is False
    subject = "Neuer Geschäftspartner"
    result = mut.email_from_buchhaltung(subject)
    assert result is True


def test_get_buchhaltungsnummer_for_new_contact() -> None:
    email = Email(
        message_id="123",
        subject="Neuer Geschäftspartner (123456)",
        sender="123",
        sent_date="2023-10-01T12:00:00Z",
        unique_id="test_message_id",
        content="""
            "<html><body>"
            '<div class="elementToProof">'
            "Ihre Buchhaltungsnummer lautet: 1412345. Vielen Dank."
            "</div>"
            "</body></html>"
            """,
        has_attachment=False,
    )
    new_contact_id, buchhaltungsnummer = mut.get_buchhaltungsnummer_for_new_contact(
        email
    )
    assert new_contact_id == "123456"
    assert buchhaltungsnummer == "1412345"

    email.content = """
            "<html><body>"
            '<div class="elementToProof">'
            "Some other content without a number."
            "</div>"
            "</body></html>"
            """
    new_contact_id, buchhaltungsnummer = mut.get_buchhaltungsnummer_for_new_contact(
        email
    )
    assert buchhaltungsnummer is None

    email.subject = "Neuer Geschäftspartner xxx"
    new_contact_id, buchhaltungsnummer = mut.get_buchhaltungsnummer_for_new_contact(
        email
    )
    assert new_contact_id is None
    assert buchhaltungsnummer is None


def test_get_attachments_from_email_pdf(monkeypatch: Mock) -> None:
    email = Email()

    fetch_mock = Mock(return_value={"invoice.pdf": b"dummy_content"})
    monkeypatch.setattr(mut, "fetch_mail_attachments", fetch_mock)

    attachments = mut.get_attachments_from_email(fake_msgraph, email)
    assert attachments == {"invoice.pdf": b"dummy_content"}
    fetch_mock.assert_called_once_with(
        ms_graph=fake_msgraph, email=email, attachment_type="pdf"
    )


def test_get_attachments_from_email_xlxs(monkeypatch: Mock, fake_msgraph: Mock) -> None:
    email = Email()
    # Arrange: first call (pdf) → empty dict, second (xlsx) → our XLSX dict
    xlsx_data = {"report.xlsx": b"aaa"}
    fetch_mock = Mock(side_effect=[{}, xlsx_data])
    monkeypatch.setattr(mut, "fetch_mail_attachments", fetch_mock)

    # Act
    result = mut.get_attachments_from_email(fake_msgraph, email)

    # Assert: we got the xlsx_data back
    assert result == xlsx_data

    # And fetch_mail_attachments was called twice in the right order
    expected_count = 2
    assert fetch_mock.call_count == expected_count
    assert fetch_mock.call_args_list == [
        call(ms_graph=fake_msgraph, email=email, attachment_type="pdf"),
        call(ms_graph=fake_msgraph, email=email, attachment_type="xlsx"),
    ]


def test_get_attachments_from_email_no_pdf_no_xlxs(
    monkeypatch: Mock, fake_msgraph: Mock
) -> None:
    email = Email()
    # Arrange: both pdf and xlsx yield empty dict
    fetch_mock = Mock(side_effect=[{}, {}])
    monkeypatch.setattr(mut, "fetch_mail_attachments", fetch_mock)

    # Act
    attachments = mut.get_attachments_from_email(fake_msgraph, email)
    # Assert: we got None for both
    assert attachments == {}


def test_process_attachments(fake_logger: Mock) -> None:
    email = Email()
    attachments: dict[str, bytes] = {}
    # Test with empty attachments
    file_data, file_name = mut.process_attachments(attachments, email)
    assert file_data is None
    assert file_name is None

    attachments = {
        "invoice.pdf": b"dummy_pdf_content",
        "report.xlsx": b"dummy_xlsx_content",
    }
    file_data, file_name = mut.process_attachments(attachments, email)

    fake_logger.info.assert_called_with(
        "More than one attachment found for %s. Only the first one will be processed.",
        email.info,
    )
    assert file_data == b"dummy_pdf_content"
    assert file_name == "invoice.pdf"


def test_save_attachment(tmp_path: Path) -> None:
    file_data = b"dummy_content"
    file_name = "test_file.txt"
    file_path = mut.save_attachment(file_data, file_name, tmp_path)

    assert isinstance(file_path, Path)
    assert file_path.exists()
    assert file_path.read_bytes() == file_data
    assert file_path.name == file_name

    # Clean up
    file_path.unlink()


def test_check_and_convert_to_pdf(monkeypatch: Mock) -> None:
    fake_excel_to_pdf = Mock()
    monkeypatch.setattr(mut, "excel_to_pdf", fake_excel_to_pdf)
    file_path = Path("dummy.xlsx")

    file_path = mut.check_and_convert_to_pdf(file_path)
    assert file_path == Path("dummy.pdf")

    file_path = Path("dummy.pdf")
    file_path = mut.check_and_convert_to_pdf(file_path)
    assert file_path == Path("dummy.pdf")


def test_get_transport_order_pdf_with_valid_attachment(
    monkeypatch: Mock,
    tmp_path: Path,
    fake_msgraph: Mock,
) -> None:
    email = Email()

    fetch_mock = Mock(return_value={"invoice.pdf": b"dummy_content"})
    monkeypatch.setattr(mut, "fetch_mail_attachments", fetch_mock)

    pdf_path = mut.get_transport_order_pdf(fake_msgraph, email, tmp_path)
    assert isinstance(pdf_path, Path)
    assert pdf_path.name == "invoice.pdf"
    assert pdf_path.exists()
    assert pdf_path.read_bytes() == b"dummy_content"


def test_get_transport_order_pdf_with_no_valid_attachments(
    monkeypatch: Mock,
    tmp_path: Path,
    fake_msgraph: Mock,
) -> None:
    email = Email()

    fetch_mock = Mock(return_value={})
    monkeypatch.setattr(mut, "fetch_mail_attachments", fetch_mock)

    with pytest.raises(mut.NoPDForXLSXError):
        mut.get_transport_order_pdf(fake_msgraph, email, tmp_path)


@pytest.fixture
def fake_email() -> Email:
    return Email(
        message_id="123",
        subject="Test Subject",
        sender="@kolibrain.de",
        sent_date="2023-10-01T12:00:00Z",
        unique_id="test_message_id",
        content="""
            "<html><body>"
            '<div class="elementToProof">'
            "Ihre Buchhaltungsnummer lautet: 1412345. Vielen Dank."
            "</div>"
            "</body></html>"
            """,
        has_attachment=True,
    )


@pytest.fixture
def fake_attachment() -> dict[str, bytes]:
    return {"test.pdf": b"%PDF-1.4 dummy"}


def test_process_email_and_retrieve_transport_order_valid_order(
    fake_msgraph: Mock,
    monkeypatch: Mock,
    tmp_path: Path,
    fake_email: Email,
    fake_attachment: Mock,
) -> None:
    contacts_with_new_buchhaltungsnummer: list[tuple[str, str]] = []

    fake_get_attachments_from_email = Mock(return_value=fake_attachment)
    monkeypatch.setattr(
        mut, "get_attachments_from_email", fake_get_attachments_from_email
    )

    saving_path = tmp_path

    real = mut.get_transport_order_pdf

    def side_effect(*args: dict, **kwargs: dict) -> Path:
        kwargs.pop("saving_path", None)
        return real(*args, saving_path=saving_path, **kwargs)  # type: ignore[return-value, misc, arg-type]

    fake_get_transport_order_pdf = Mock(side_effect=side_effect)
    monkeypatch.setattr(mut, "get_transport_order_pdf", fake_get_transport_order_pdf)

    transport_order = mut.process_email_and_retrieve_transport_order(
        fake_msgraph,
        fake_email,
        contacts_with_new_buchhaltungsnummer,
        saving_path=saving_path,
    )

    assert transport_order is not None
    assert saving_path.exists()
    assert (saving_path / "test.pdf").read_bytes() == b"%PDF-1.4 dummy"


def test_process_email_and_retrieve_transport_order_not_autorized(
    fake_msgraph: Mock,
    tmp_path: Path,
    fake_email: Mock,
) -> None:
    contacts_with_new_buchhaltungsnummer: list[tuple[str, str]] = []

    # Simulate unauthorized user
    fake_email.sender = "fake"

    with pytest.raises(mut.UnauthorizedUser):
        mut.process_email_and_retrieve_transport_order(
            fake_msgraph,
            fake_email,
            contacts_with_new_buchhaltungsnummer,
            saving_path=tmp_path,
        )


@pytest.fixture
def buchhaltungs_email() -> Email:
    return Email(
        message_id="123",
        subject="Test Subject",
        sender="@kolibrain.de",
        sent_date="2023-10-01T12:00:00Z",
        unique_id="test_message_id",
        content="""
            "<html><body>"
            '<div class="elementToProof">'
            "Ihre Buchhaltungsnummer lautet: 1412345. Vielen Dank."
            "</div>"
            "</body></html>"
            """,
        has_attachment=True,
    )


def test_process_email_and_retrieve_transport_order_buchhaltung(
    fake_msgraph: Mock,
    tmp_path: Path,
    buchhaltungs_email: Email,
) -> None:
    contacts_with_new_buchhaltungsnummer: list[tuple[str, str]] = []

    buchhaltungs_email.subject = "Neuer Geschäftspartner (123456)"

    with pytest.raises(mut.EmailFromBuchhaltung):
        mut.process_email_and_retrieve_transport_order(
            fake_msgraph,
            buchhaltungs_email,
            contacts_with_new_buchhaltungsnummer,
            saving_path=tmp_path,
        )
    assert contacts_with_new_buchhaltungsnummer[0] == ("123456", "1412345")
    buchhaltungs_email.subject = "Test Subject"  # Reset subject for other tests


def test_process_email_and_retrieve_transport_order_buchhaltung_no_number(
    fake_msgraph: Mock,
    tmp_path: Path,
    buchhaltungs_email: Email,
) -> None:
    contacts_with_new_buchhaltungsnummer: list[tuple[str, str]] = []

    buchhaltungs_email.subject = "Neuer Geschäftspartner xxx"

    with pytest.raises(mut.NoBuchhaltungsNummerFoundError):
        mut.process_email_and_retrieve_transport_order(
            fake_msgraph,
            buchhaltungs_email,
            contacts_with_new_buchhaltungsnummer,
            saving_path=tmp_path,
        )
    assert contacts_with_new_buchhaltungsnummer == []
    buchhaltungs_email.subject = "Test Subject"  # Reset subject for other tests


def test_process_email_and_retrieve_transport_order_no_attachment(
    fake_msgraph: Mock,
    tmp_path: Path,
    buchhaltungs_email: Email,
) -> None:
    contacts_with_new_buchhaltungsnummer: list[tuple[str, str]] = []

    # Simulate no attachment
    buchhaltungs_email.has_attachment = False

    with pytest.raises(mut.NoAttachmentFoundError):
        mut.process_email_and_retrieve_transport_order(
            fake_msgraph,
            buchhaltungs_email,
            contacts_with_new_buchhaltungsnummer,
            saving_path=tmp_path,
        )
