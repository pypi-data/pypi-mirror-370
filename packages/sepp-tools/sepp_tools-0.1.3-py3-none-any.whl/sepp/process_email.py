import json
import logging
import re
from dataclasses import asdict
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from fpdf import FPDF
from microsoft.connectors.api import MSGraphAPI

from sepp.commons import Email
from sepp.exceptions import (
    EmailFromBuchhaltung,
    NoAttachmentFoundError,
    NoBuchhaltungsNummerFoundError,
    NoPDForXLSXError,
    UnauthorizedUser,
)
from sepp.scripts.mailing_script import (
    fetch_mail_attachments,
)

logger = logging.getLogger(__name__)


def check_and_convert_to_pdf(file_path: Path) -> Path:
    """Checks if the file is a PDF and converts it if necessary.

    Parameters
    ----------
    file_path : Path
        The path to the file.

    Returns
    -------
    Path
        The path to the converted PDF file.

    """
    if file_path.suffix == ".xlsx":
        excel_to_pdf(file_path)  # function takes a Path
        return file_path.with_suffix(".pdf")
    return file_path


def save_attachment(
    file_data: bytes, file_name: str, saving_path: Path = Path("transport_orders_imgs")
) -> Path:
    """Saves the attachment into a file.

    Parameters
    ----------
    file_data : bytes
        The data in the attached file.
    file_name : str
        The name of the attached file.
    saving_path : Path
        The path where the file will be saved. By default, it is set to "transport_orders_imgs".

    Returns
    -------
    Path
        The path to the saved file.

    """
    Path(saving_path).mkdir(parents=True, exist_ok=True)

    file_path = Path(saving_path) / file_name
    with file_path.open("wb") as f:
        f.write(file_data)
    return file_path


def process_attachments(
    attachments: dict, email: Email
) -> tuple[bytes, str] | tuple[None, None]:
    """Processes the attachments from the email.
    If there are multiple attachments, only the first one is processed.
    If no attachments are found, returns None.

    Parameters
    ----------
    attachments : dict
        The attachments from the email.
    email : Email
        The email object being processed.

    Returns
    -------
    tuple
        A tuple containing the file data and file name.
        If no attachments are found, returns (None, None).

    """
    n_attachments = len(list(attachments.keys()))

    if n_attachments == 0:
        return None, None

    if n_attachments > 1:
        logger.info(
            "More than one attachment found for %s. Only the first one will be processed.",
            email.info,
        )

    file_name = next(iter(attachments.keys()))
    file_data = attachments[file_name]

    return file_data, file_name


def get_attachments_from_email(ms_graph: MSGraphAPI, email: Email) -> dict:
    """Retrieves attachments from the email.
    If no `pdf` attachments are found, it attempts to retrieve `xlsx` attachments.

    Parameters
    ----------
    ms_graph : MSGraphAPI
        MSGraphAPI instance to interact with Microsoft Graph API.
    email : Email
        The email object being processed.

    Returns
    -------
    dict
        A dictionary containing the attachment data.
        If no attachments are found, returns an empty dictionary.

    """
    attachments = fetch_mail_attachments(
        ms_graph=ms_graph, email=email, attachment_type="pdf"
    )
    if not attachments:
        return fetch_mail_attachments(
            ms_graph=ms_graph, email=email, attachment_type="xlsx"
        )
    return attachments


def email_from_unauthorized_users(email: Email) -> bool:
    """Checks if the email is from @kolibrain.de or @spedition-oppel.de.

    Parameters
    ----------
    email : Email
        The email object to check.

    Returns
    -------
    bool
        True if the email is from an unauthorized user, False otherwise.

    """
    return (
        "@kolibrain.de" not in email.sender
        and "@spedition-oppel.de" not in email.sender
    )


def parse_buchhaltungsnummer(email_content: str) -> str | None:
    """Parses the Buchhaltungsnummer from the email content.
    Parameters.
    ----------
    email_content : str
        The content of the email to parse.

    Returns
    -------
    str | None
        The Buchhaltungsnummer if found, None otherwise.

    """
    soup = BeautifulSoup(email_content, "lxml")
    div_match = soup.find("div", class_="elementToProof")
    mailtext = (
        div_match.text if div_match else (soup.body.get_text() if soup.body else "")
    )
    regex_match = re.search(r"\b14\d{5}\b", mailtext)
    return regex_match.group() if regex_match else None


def email_from_buchhaltung(email_subject: str) -> bool:
    """Checks if the email is from Buchhaltung."""
    return "Neuer Geschäftspartner" in email_subject


def get_buchhaltungsnummer_for_new_contact(
    email: Email,
) -> tuple:
    """Handles emails from Buchhaltung.
    Parses the new contact ID and Buchhaltungsnummer from the email subject and content.
    If the Buchhaltungsnummer is not found, sends an error email to the admins.

    Marks the email as read.

    Parameters
    ----------
    email : Email
        The email object to check.

    Returns
    -------
    tuple
        A tuple containing the new contact ID and Buchhaltungsnummer.
        If the Buchhaltungsnummer is not found, returns (None, None).

    """
    try:
        new_contact_id = email.subject.split("(")[1].replace(")", "")
        buchhaltungsnummer = parse_buchhaltungsnummer(email.content)
    except (IndexError, Exception):
        return None, None
    else:
        return new_contact_id, buchhaltungsnummer


def email_has_no_attachment(email: Email) -> bool:
    """Checks if the email has an attachment."""
    return bool(email.has_attachment)


def get_transport_order_pdf(
    ms_graph: MSGraphAPI, email: Email, saving_path: Path
) -> Path | None:
    """Retrieves the attached transport order from the email, converts it to `.pdf` if necessary, saves and returns its path.
    If no valid `.pdf` or `.xlsx` attachments are found, sends an error email to the sender and returns None.

    Parameters
    ----------
    ms_graph : MSGraphAPI
        MSGraphAPI instance to interact with Microsoft Graph API.

    email : Email
        The email object being processed.
    saving_path : Path
        The path where the attachment will be saved.
        By default, it is set to "transport_orders_imgs".

    Returns
    -------
    Path | None
        The path to the saved PDF file.
        If no valid attachments are found, returns None.

    """
    attachments = get_attachments_from_email(ms_graph, email)
    file_data, file_name = process_attachments(attachments, email)

    if file_data is None or file_name is None:
        _raise_no_pd_for_xlsx_error(
            "Email appears to have an attachment, but it is not .pdf or .xlsx"
        )
    else:
        file_path = save_attachment(file_data, file_name, saving_path=saving_path)
    return check_and_convert_to_pdf(file_path)


def _raise_unauthorized_user(e: str = "") -> None:
    """Raises an UnauthorizedUserError."""
    raise UnauthorizedUser(e)


def _raise_no_attachment_found_error(e: str = "") -> None:
    """Raises a NoAttachmentFoundError."""
    raise NoAttachmentFoundError(e)


def _raise_no_buchhaltungsnummer_found_error(e: str = "") -> None:
    """Raises a NoBuchhaltungsNummerFoundError."""
    raise NoBuchhaltungsNummerFoundError(e)


def _raise_no_pd_for_xlsx_error(e: str = "") -> None:
    """Raises a NoPDForXLSXError."""
    raise NoPDForXLSXError(e)


def _raise_email_from_buchhaltung(e: str = "") -> None:
    """Raises an EmailFromBuchhaltungError."""
    raise EmailFromBuchhaltung(e)


def process_email_and_retrieve_transport_order(
    ms_graph: MSGraphAPI,
    email: Email,
    contacts_with_new_buchhaltungsnummer: list,
    saving_path: Path,
) -> Path | None:
    """Processes the email and retrieves the transport order PDF.
    PDF is saved in the specified saving path.
    Processed email metadata is saved in a JSON file in the same directory.

    If the email is from Buchhaltung, it updates the list of contacts with new Buchhaltungsnummer and marks the email as read.
    Returns None and notifies the sender if the email has no attachment.
    Returns None and notifies the sender if the email is from unauthorized users.
    If the email has a valid attachment, it retrieves the transport order PDF and returns its path.
    If any error occurs during processing, it sends an error email to the admins and returns None.

    Parameters
    ----------
    ms_graph : MSGraphAPI
        MSGraphAPI instance to interact with Microsoft Graph API.
    email : Email
        The email object being processed.
    contacts_with_new_buchhaltungsnummer : list
        List of tuples containing the new contact ID and Buchhaltungsnummer.
    email_processing_results : Results
        The results object to store the results of the email processing.
    saving_path : Path
        The path where the transport order PDF will be saved.
        By default, it is set to "transport_orders_imgs".

    Returns
    -------
    Path | None
        The path to the retrieved transport order PDF file.
        If the email has no valid attachment or if any error occurs, returns None.

    """
    if email_from_unauthorized_users(email):
        _raise_unauthorized_user("Email is from an unauthorized user")

    if email_from_buchhaltung(email.subject):
        logger.info(
            "Email appears to be from Buchhaltung. Processing it to get new contact ID and Buchhaltungsnummer."
        )
        new_contact_id, buchhaltungsnummer = get_buchhaltungsnummer_for_new_contact(
            email
        )
        if new_contact_id and buchhaltungsnummer:
            contacts_with_new_buchhaltungsnummer.append(
                (new_contact_id, buchhaltungsnummer)
            )
            logger.info(
                "New contact ID %s and Buchhaltungsnummer %s added to the list.",
                new_contact_id,
                buchhaltungsnummer,
            )
            _raise_email_from_buchhaltung("Email from Buchhaltung was processed.")
        else:
            logger.error(
                "Failed to retrieve new contact ID and Buchhaltungsnummer from the email."
            )
            _raise_no_buchhaltungsnummer_found_error(
                "Email appears to be from Buchhaltung, but no Buchhaltungsnummer found."
            )

    if not email.has_attachment:
        _raise_no_attachment_found_error("Email has no attachment.")

    Path(saving_path).mkdir(parents=True, exist_ok=True)
    pdf_saving_path = Path(saving_path)

    email_data = json.dumps(asdict(email), indent=4, ensure_ascii=False)
    with (pdf_saving_path / "email_meta.json").open("w", encoding="utf-8") as f:
        f.write(email_data)

    return get_transport_order_pdf(
        ms_graph=ms_graph, email=email, saving_path=pdf_saving_path
    )


def excel_to_pdf(excelpath: Path) -> None:
    excel_file = excelpath
    df = pd.read_excel(excel_file)

    # PDF erstellen
    class PDF(FPDF):
        def header(self) -> None:
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, "Excel to PDF", border=0, ln=1, align="C")

        def footer(self) -> None:
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", align="C")

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    # DataFrame in PDF-Zellen schreiben
    for row in df.itertuples():
        pdf.cell(0, 10, " | ".join(str(value) for value in row[1:]), ln=1)
    # PDF speichern
    pdf.output(excel_file.with_suffix(".pdf").as_posix(), "F")
