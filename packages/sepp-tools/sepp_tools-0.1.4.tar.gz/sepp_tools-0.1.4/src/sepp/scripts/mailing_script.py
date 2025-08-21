import csv
import logging
import shutil
import tempfile
from collections.abc import Iterable
from datetime import datetime
from itertools import islice
from pathlib import Path
from zoneinfo import ZoneInfo

from microsoft.connectors.api import MicrosoftResponse, MSGraphAPI

from sepp.commons import Email
from sepp.settings import BASE_DIR, FAILED_ID

logger = logging.getLogger(__name__)

STAMM_DATA_CSV = Path(BASE_DIR / "DTVF_Deb_Stamm_20241108_133047.csv")
OUTPUT_CSV_DIR = Path(BASE_DIR / "New Business Partner CSVs")


def germany_date_time(date_time: str) -> tuple[str, str]:
    """Convert UTC date and time to Germany date and time."""
    utc_time = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=ZoneInfo("UTC")
    )
    germany_time = utc_time.astimezone(ZoneInfo("Europe/Berlin"))
    date = germany_time.strftime("%d-%m-%Y")
    time = germany_time.strftime("%H:%M")
    return date, time


def move_failed_mail(ms_graph: MSGraphAPI, email: Email) -> None:
    """Moves the email to the failed folder and marks it as read.

    Parameters
    ----------
    ms_graph : MSGraphAPI
        MSGraphAPI instance to interact with Microsoft Graph API.

    email : Email
        Email instance to be moved.

    """
    ms_graph.mark_email_as_read(email.message_id)
    ms_graph.move_email(email.message_id, destination_folder=FAILED_ID)
    logger.info(
        "Moved email from %s sent on %s with subject '%s' to folder 'FAILED'",
        email.sender,
        email.sent_date,
        email.subject,
    )


def send_generic_email(
    ms_graph: MSGraphAPI,
    primary_recipient: str,
    message: str,
    bcc_list: list[str],
    subject: str,
) -> MicrosoftResponse:
    """Sends a generic email.

    Parameters
    ----------
    ms_graph : MSGraphAPI
        MSGraphAPI instance to interact with Microsoft Graph API.

    primary_recipient : str
        Primary recipient of the email.

    message : str
        Body of the email.

    bcc_list : list[str]
        List of BCC recipients.

    subject : str
        Subject of the email.

    Returns
    -------
    MicrosoftResponse
        Response from the Microsoft Graph API after sending the email.

    """
    return ms_graph.send_email(
        recipient_list=[primary_recipient],
        subject=subject,
        message=message,
        bcc_list=bcc_list,
    )


def send_success_email(
    ms_graph: MSGraphAPI,
    primary_recipient: str,
    client_name: str,
    transport_order_number: str,
    external_number: str,
) -> MicrosoftResponse:
    date, time = (
        datetime.now(tz=ZoneInfo("Europe/Berlin")).strftime("%d-%m-%Y %H:%M").split(" ")
    )
    """Sends an email to the sender of the processed email with the order number and client name.

    Parameters
    ----------
    ms_graph : MSGraphAPI
        MSGraphAPI instance to interact with Microsoft Graph API.
    email : Email
        Email instance being processed.
    client_name : str
        Name of the client.
    order_number : str
        Order number of the transport order.
    external_number : str
        External number of the transport order.

    Returns
    -------
    MicrosoftResponse
        Response from the Microsoft Graph API after sending the email.

    """

    recipient_list = [primary_recipient]
    bcc_list = ["al-khazrage@kolibrain.de", "shlychkov@kolibrain.de"]
    subject = f"Sepp - Automatisch erstellter Transportauftrag von {client_name} (Nr. {transport_order_number})"
    message = f"""Hallo Oppel-Team,
    \nich habe den Transportauftrag von {client_name} mit der Nummer {transport_order_number} und der Externen Nummer {external_number} am {date} um {time} erfasst.
    \nLiebe Grüße\nSEPP
    """

    return ms_graph.send_email(
        recipient_list=recipient_list,
        subject=subject,
        message=message,
        bcc_list=bcc_list,
    )


def send_failed_email(
    ms_graph: MSGraphAPI,
    email: Email,
    explanation: str | Iterable[str] = "",
    pdf_path: Path | None = None,
) -> MicrosoftResponse:
    """Sends an email to the sender of the failed email and admins with an explanation.

    Parameters
    ----------
    ms_graph : MSGraphAPI
        MSGraphAPI instance to interact with Microsoft Graph API.
    email : Email
        Email instance being processed.
    explanation : str
        Explanation of the failure.
    pdf_path : Path | None
        Path to the PDF attachment. If None, no attachment will be sent.

    Returns
    -------
    MicrosoftResponse
        Response from the Microsoft Graph API after sending the email.

    """
    recipient_list = [email.sender]
    bcc_list = ["al-khazrage@kolibrain.de", "shlychkov@kolibrain.de"]

    failed_email_date = email.sent_date
    date, time = germany_date_time(failed_email_date)
    subject = "SEPP Fehlermeldung"
    message_content = f"""Hallo Oppel-Team,
    \nich konnte den Transportauftrag, der mir am {date} um {time} mit dem Betreff <{email.subject}> zugeschickt wurde, leider nicht verarbeiten.
    {explanation}
    \nIhr findet den Transportauftrag den ich nicht verarbeiten konnte im Anhang an diese Mail.
    \nLiebe Grüße\nSEPP
    """

    if pdf_path:
        pdf_path_str = pdf_path.as_posix()
        message = ms_graph.send_email_with_attachment(
            recipient_list=recipient_list,
            subject=subject,
            message=message_content,
            attachment_path=pdf_path_str,
            bcc_list=bcc_list,
        )
    else:
        message = ms_graph.send_email(
            recipient_list=recipient_list,
            subject=subject,
            message=message_content,
            bcc_list=bcc_list,
        )

    if not message.success:
        error_msg = f"ATTENTION - IMMEDIATE ACTION REQUIRED: The {email.info} was not processed successfully AND we failed to send an error message to the sender of the mail."
        logger.error(error_msg)
        send_error_email(ms_graph=ms_graph, error_msg=error_msg)

    return message


def send_error_email(
    ms_graph: MSGraphAPI,
    error_msg: str | Iterable[str],
    *,
    include_log: bool = True,
    path_to_folder: Path | None = None,
) -> None:
    """Send an error email to the admins with the error message.

    Parameters
    ----------
    ms_graph : MSGraphAPI
        MSGraphAPI instance to interact with Microsoft Graph API.
    error_msg : str
        Error message to be sent in the email.
    path_to_folder : Path | None, optional
        Path to a folder that should be zipped and attached to the email. If None, no folder will be attached.
        Default is None.

    include_log : bool, optional
        If True, the latest log file will be attached to the email. Default is True.

    """
    recipient_list = [
        "al-khazrage@kolibrain.de",
        "guemues@kolibrain.de",
        "shlychkov@kolibrain.de",
    ]
    attachment_paths = []
    temp_files_to_cleanup = []  # Track temporary files to delete later

    if include_log:
        log_dir = Path(BASE_DIR) / "logs"
        latest_log = max(
            log_dir.glob("*.log"), key=lambda f: f.stat().st_ctime, default=None
        )
        if latest_log:
            attachment_paths.append(latest_log.as_posix())

    if path_to_folder and path_to_folder.exists() and path_to_folder.is_dir():
        try:
            # Create temporary zip file
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
                temp_zip_path = temp_zip.name

            # Create the archive at the temporary location
            archive_path = shutil.make_archive(
                temp_zip_path.replace(".zip", ""),  # Remove .zip as shutil adds it
                "zip",
                str(path_to_folder.parent),
                str(path_to_folder.name),
            )

            attachment_paths.append(archive_path)
            temp_files_to_cleanup.append(archive_path)  # Mark for cleanup
            logger.info(
                "Created temporary zip %s for folder %s", archive_path, path_to_folder
            )

        except Exception:
            logger.exception(
                "Failed to zip folder %s. The folder will not be attached to the error email.",
                path_to_folder,
            )

    if not isinstance(error_msg, str):
        error_msg = "".join(error_msg)
    error_msg += "\n\n"

    try:
        # Send the email
        message = ms_graph.send_email_with_attachments(
            recipient_list=recipient_list,
            subject="SEPP ERROR",
            message=error_msg,
            attachment_paths=attachment_paths,
        )

        if not message.success:
            logger.error(
                "Failed to send error message to al-khazrage@kolibrain.de and guemues@kolibrain.de"
            )
    finally:
        # Clean up temporary files
        try:
            for temp_file in temp_files_to_cleanup:
                Path(temp_file).unlink()
                logger.info("Cleaned up temporary file: %s", temp_file)
        except Exception:
            logger.exception("Failed to clean up temporary file")


def send_email_to_buchhaltung(
    ms_graph: MSGraphAPI, businesscontact: list[tuple[dict, int]], pdf_path: Path
) -> None:
    for contact in businesscontact:
        name = contact[0].get("name", "")
        street = contact[0].get("street", "")
        house_number = contact[0].get("houseNumber", "")
        zip_code = contact[0].get("zip", "")
        city = contact[0].get("city", "")

        csv_path = write_csv_for_buchhaltung(name, street, house_number, zip_code, city)

        message_content = f"""
            Sehr geehrte Damen und Herren,

            ich konnte den folgenden Geschäftspartner nicht in CarLo finden:

            {name}
            {street} {house_number}
            {zip_code} {city}

            Um ihn neu anlegen zu können brauche ich eine neue Geschäftspartnernummer.
            Bitte senden Sie diese Nummer also Antwort auf diese Nachricht.

            WICHTIG: Bitte nur die Nummer ohne weiteren Text oder Anhang senden.

            Liebe Grüße und vielen Dank
            SEPP
            """
        pdf_path_str = pdf_path.as_posix()
        csv_path_str = csv_path.as_posix()
        msg = ms_graph.send_email_with_attachments(
            recipient_list=["fibu@spedition-oppel.de"],
            subject=f"Neuer Geschäftspartner ({contact[1]})",
            message=message_content,
            attachment_paths=[pdf_path_str, csv_path_str],
            bcc_list=["al-khazrage@kolibrain.de"],
        )

        if not msg.success:
            logger.error("Failed to send mail to Buchhaltung.")


def fetch_mail_attachments(
    ms_graph: MSGraphAPI, email: Email, attachment_type: str
) -> dict[str, str]:
    """Fetches the attachments of an email.
    This function is used to fetch the attachments of an email using the MSGraphAPI.

    Parameters
    ----------
    ms_graph : MSGraphAPI
        MSGraphAPI instance to interact with Microsoft Graph API.
    email : Email
        Email instance to fetch attachments from.
    attachment_type : str
        Type of the attachment to fetch. This can be "pdf" or "csv".

    Returns
    -------
    dict[str, str]
        Dictionary containing the attachment name and its content.
        The key is the attachment name and the value is the content of the attachment.

    """
    fetch_attachments_response = ms_graph.get_attachments(
        email.message_id, type=attachment_type
    )
    if not fetch_attachments_response.success:
        logger.error("Failed to load attachments for %s via msgraph API", email.info)
        return {}

    return fetch_attachments_response.value


def write_csv_for_buchhaltung(
    name: str, street: str, house_number: str, zip_code: str, city: str
) -> Path:
    """Reads the first two rows from BASE_CSV, appends a new contact row,
    and writes to transport_orders_imgs/{name}.csv, creating the directory if needed.
    """
    # Prepare paths
    OUTPUT_CSV_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_CSV_DIR / f"{name}.csv"

    # Read first two rows
    with STAMM_DATA_CSV.open("r", newline="", encoding="windows-1252") as src:
        reader = csv.reader(src, delimiter=";")
        header_rows = list(islice(reader, 2))

    # Build new contact row
    new_contact = [
        "",
        name,
        *[""] * 12,  # placeholders for the empty columns
        f"{street} {house_number}",
        "",
        zip_code,
        city,
    ]

    # Write combined rows
    with out_path.open("w", newline="", encoding="windows-1252") as dst:
        writer = csv.writer(dst, delimiter=";")
        writer.writerows([*header_rows, new_contact])

    return out_path
