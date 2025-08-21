import argparse
import json
import logging
import sys
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import microsoft
import pandas as pd
from microsoft.connectors.api import MicrosoftResponse, MSGraphAPI
from openai import RateLimitError
from soloplan import SoloplanAPI

from sepp.commons import Email, Results
from sepp.create_order_with_soloplan import create_order_with_soloplan
from sepp.exceptions import (
    EmailFromBuchhaltung,
    LLMResponseIncompleteError,
    NoAttachmentFoundError,
    NoBuchhaltungsNummerFoundError,
    NoPDForXLSXError,
    UnauthorizedUser,
)
from sepp.extract_info_from_pdf import get_llm_response
from sepp.process_email import process_email_and_retrieve_transport_order
from sepp.scripts.mailing_script import (
    move_failed_mail,
    send_email_to_buchhaltung,
    send_error_email,
    send_failed_email,
    send_success_email,
)
from sepp.scripts.mock_soloplan import fake_soloplan_api
from sepp.settings import (
    BASE_DIR,
    ERLEDIGT_ID,
    FAILED_ID,
    ms_graph_config,  # Add msgraph import from settings
    soloplan_config,
)

SLEEP_INTERVAL = 60
MAX_PAGES = 4
MAX_EMAIL_RETRIES = 1
MINS_BEFORE_RETRY = 2

logger = logging.getLogger(__name__)


def time_now() -> str:
    """Returns the current time in Germany."""
    return datetime.now(tz=ZoneInfo("Europe/Berlin")).strftime("%Y%m%d_%H%M%S")


def create_retries_csv() -> None:
    """Creates a CSV file to log retries if it does not exist."""
    retries_log_path = BASE_DIR / "soloplan_retries_df.csv"
    if not retries_log_path.exists():
        retries_df = pd.DataFrame(
            {
                "unique_email_id": pd.Series(dtype=str),
                "retries": pd.Series(dtype=int),
                "last_retry": pd.Series(dtype="datetime64[ns]"),
            }
        )
        retries_df.to_csv(retries_log_path, index=False)


def email_cannot_be_retried(
    email: Email, ms_graph: MSGraphAPI, pdf_file_path: Path
) -> bool:
    retries_df = pd.read_csv(BASE_DIR / "soloplan_retries_df.csv")
    if email.unique_id not in retries_df["unique_email_id"].to_numpy():
        logger.info(
            "Email has not been retried before.  Proceeding with processing...",
        )
        return False

    email_retries = retries_df.loc[
        retries_df["unique_email_id"] == email.unique_id, "retries"
    ].to_numpy()

    if email_retries > MAX_EMAIL_RETRIES:
        logger.warning(
            "Email has reached the maximum number of retries.\n"
            "Marking email as read and moving to 'FAILED' folder.\n"
            "Sending error email to admins and failed email to customer.",
        )
        ms_graph.mark_email_as_read(email.message_id)
        move_failed_mail(ms_graph, email)
        message_to_customer = "SEPP konnte den Auftrag leider nicht anlegen, da Soloplan CarLo einen Fehler zurückgegeben hat"
        send_failed_email(
            ms_graph=ms_graph,
            email=email,
            explanation=message_to_customer,
            pdf_path=pdf_file_path,
        )
        message_to_admins = (
            f"{email.info} could not be processed because of consistent Soloplan 'Search and creation' errors.\n"
            "It has reached the maximum number of retries and has been moved to the failed folder."
        )

        send_error_email(ms_graph, message_to_admins)
        return True

    if email_retries <= MAX_EMAIL_RETRIES:
        last_retry = retries_df.loc[
            retries_df["unique_email_id"] == email.unique_id, "last_retry"
        ].to_numpy()

        if datetime.now(tz=ZoneInfo("Europe/Berlin")) - pd.to_datetime(
            last_retry[0]
        ) < pd.Timedelta(minutes=MINS_BEFORE_RETRY):
            logger.info(
                "Email has already been retried recently. Skipping further processing.",
            )
            return True

    logger.info(
        "Email has been retried before but more than %d minutes ago. Proceeding with processing...",
        MINS_BEFORE_RETRY,
    )
    return False


def setup_logging() -> None:
    """Sets up logging configuration."""
    date_time = datetime.now(tz=ZoneInfo("Europe/Berlin")).strftime("%Y%m%d_%H%M")
    Path(BASE_DIR / "logs").mkdir(parents=True, exist_ok=True)
    log_file_name = f"{BASE_DIR}/logs/sepp_session_{date_time}.log"
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    root = logging.getLogger()  # root logger
    root.setLevel(logging.INFO)

    # Remove any existing handlers from root
    if root.hasHandlers():
        root.handlers.clear()

    handler = logging.FileHandler(log_file_name)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    root.addHandler(handler)


def fetch_unread_emails(ms_graph: MSGraphAPI) -> MicrosoftResponse:
    """Fetch unread emails from the inbox.

    Returns
    -------
    MicrosoftResponse
        The response object from the Microsoft Graph API.

    """
    try:
        return ms_graph.get_unread_emails()

    except Exception:
        error_msg = "Unexpected error fetching unread emails"
        logger.exception(error_msg)
        send_error_email(ms_graph, error_msg)
        return MicrosoftResponse(
            success=True,  # Error is not connected to the API, rather some local issue
            value=[],
            info=error_msg,
        )


def ms_graph_response_unsuccessful(
    ms_graph: MSGraphAPI, response: MicrosoftResponse
) -> bool:
    """Check the response from Microsoft Graph API.

    If there is an error related to the API, sends an error email to admins.

    Parameters
    ----------
    response : MicrosoftResponse
        The response object from the Microsoft Graph API.

    Returns
    -------
    bool
        True if the response is unsuccessful, False otherwise.

    """
    if not response.success:
        error_msg = f"Failed to retrieve emails from sepp@kolibrain.de via the msgraph API: {response.info}"
        logger.error(error_msg)
        send_error_email(ms_graph, error_msg)
        return True
    return False


def wrap_email(email: dict) -> Email:
    """Wraps the email data into an Email dataclass object.

    Parameters
    ----------
    email : dict
        Microsoft Graph API email dict object

    Returns
    -------
    Email
        Wrapped email object

    """
    message_id = email.get("id", "")
    subject = email.get("subject", "<KEIN BETREFF>")
    sender = email.get("sender", {}).get("emailAddress", {}).get("address", "")
    date = email.get("sentDateTime", "")
    unique_id = email.get("internetMessageId", "")
    content = email.get("body", {}).get("content", "")
    attachment = email.get("hasAttachments", [])
    return Email(
        message_id=message_id,
        subject=subject,
        sender=sender,
        sent_date=date,
        unique_id=unique_id,
        content=content,
        has_attachment=attachment,
    )


def handle_not_authorized_users(
    ms_graph: MSGraphAPI, email: Email, exception: Exception
) -> None:
    """Handles emails from unauthorized users.
    Sends an email to the sender and marks the email as read.

    Parameters
    ----------
    ms_graph : MSGraphAPI
        MSGraphAPI instance to interact with Microsoft Graph API.
    email : Email
        The email object to check.
    exception : Exception
        The exception that was raised, typically UnauthorizedUser.

    """
    logger.exception(
        "%s. Email sender will be notified. Email is marked as read", exception
    )
    message = """Sehr geehrte Damen und Herren,
                        \nSie sind nicht also Nutzer für diesen Dienst zugelassen.
                        \nIch habe meinen Administrator informiert und dieser wird sich in Kürze mit Ihnen in Verbindung setzen.
                        \nMit freundlichen Grüßen,\nSEPP
                        """
    ms_graph.send_email([email.sender], "Nutzer nicht registriert", message)
    ms_graph.mark_email_as_read(email.message_id)


def handle_emails_without_attachments(
    ms_graph: MSGraphAPI, email: Email, exception: Exception
) -> None:
    """Handles emails without attachments.
    Sends a `failed` message to the sender and marks the email as read.

    Parameters
    ----------
    ms_graph : MSGraphAPI
        MSGraphAPI instance to interact with Microsoft Graph API.
    email : Email
        The email object to check.
    exception : Exception
        The exception that was raised, typically NoAttachmentFoundError.

    """
    logger.exception(
        "%s. Customer will be notified. Email is marked as read", exception
    )
    error_message = (
        "\n Ursache: Ich konnte für diese Mail leider keinen Anhang (.pdf oder .xlsx) finden. "
        "Bitte überprüft die Mail nochmal"
    )

    send_failed_email(ms_graph=ms_graph, email=email, explanation=error_message)
    ms_graph.mark_email_as_read(email.message_id)


def handle_no_pdf_xlsx_error(
    ms_graph: MSGraphAPI,
    email: Email,
    exception: Exception,
) -> None:
    """Handles emails that do not contain a valid PDF or XLSX attachment.

    Parameters
    ----------
    ms_graph : MSGraphAPI
        MSGraphAPI instance to interact with Microsoft Graph API.
    email : Email
        The email object being processed.
    exception : Exception
        The exception that was raised, typically NoPDForXLSXError.

    """
    logger.exception(
        "%s. Customer will be notified. Email is marked as read", exception
    )

    error_message = (
        "\n Ursache: Ich konnte für diese Mail leider keinen Anhang (.pdf oder .xlsx) finden. "
        "Bitte überprüft die Mail nochmal"
    )
    send_failed_email(ms_graph=ms_graph, email=email, explanation=error_message)
    ms_graph.mark_email_as_read(email.message_id)


def unexpected_error_handler(
    ms_graph: MSGraphAPI,
    email: Email,
    error: Exception,
) -> None:
    error_msg = f"Unexpected error processing email {email.info}: {error}\nEmail is marked as read and moved to 'FAILED' folder"
    message_to_customer = f"SEPP konnte leider nicht die PDF von der Email gesendet von {email.sender} am {email.sent_date} mit dem Betreff {email.subject} verarbeiten."
    logger.exception(
        "%s. Customer and admins will be notified. Email is marked as read and moved to 'FAILED' folder",
        error_msg,
    )
    send_error_email(ms_graph=ms_graph, error_msg=error_msg)
    send_failed_email(ms_graph=ms_graph, email=email, explanation=message_to_customer)
    ms_graph.mark_email_as_read(email.message_id)
    ms_graph.move_email(email.message_id, destination_folder=FAILED_ID)


def process_email_to_order(
    ms_graph: MSGraphAPI,
    email: Email,
    contacts_with_new_buchhaltungsnummer: list,
    email_processing_results: Results,
    saving_path: Path,
) -> Path | None:
    """Processes the email to retrieve the transport order and returns the path to the retrieved transport order PDF file.

    Runs the email processing function from the `process_email` module.
    PDF file and email metadata are saved to the specified saving path.

    Catches specific exceptions and handles them accordingly:
    - UnauthorizedUserError: Handles unauthorized users by sending a corresponding message to the email sender and marking the email as read.
    - NoAttachmentFoundError: Handles emails without attachments by sending a `failed` message to the email sender and marking the email as read.
    - NoBuchhaltungsNummerFoundError: Handles emails from Buchhaltung without a Buchhaltungsnummer by sending an `error` message to admins and marking the email as read.
    - NoPDForXLSXError: Handles emails without valid PDF or XLSX attachments by sending a `failed` message to the email sender and marking the email as read.
    - Other exceptions: Catches any other unexpected errors, logs them, sends an `error` message to admins, `failed` message to email sender, marks the email as read and moves it to the "FAILED" folder.


    Parameters
    ----------
    ms_graph : MSGraphAPI
        MSGraphAPI instance to interact with Microsoft Graph API.
    email : Email
        The email object being processed.
    contacts_with_new_buchhaltungsnummer : list
        List of contacts with new Buchhaltungsnummer to be updated in Soloplan.
    email_processing_results : Results
        The results object to store the results of the email processing.
    saving_path : Path
        The path where the results will be saved.

    Returns
    -------
    Path | None
        The path to the retrieved transport order PDF file, or None if an error occurred.

    """
    job_id = email.unique_id.split("@")[0].replace("<", "")

    logger.info(
        "Processing email with subject '%s' from %s as job_id: %s",
        email.subject,
        email.sender,
        job_id,
    )

    email_processing_results.update(
        {
            "id": job_id,
            "email_subject": email.subject,
            "sent_on": email.sent_date,
            "sender": email.sender,
        }
    )
    saving_path = saving_path / Path(job_id)

    try:
        return process_email_and_retrieve_transport_order(
            ms_graph=ms_graph,
            email=email,
            contacts_with_new_buchhaltungsnummer=contacts_with_new_buchhaltungsnummer,
            saving_path=saving_path,
        )
    except UnauthorizedUser as e:
        handle_not_authorized_users(ms_graph, email, e)

    except NoAttachmentFoundError as e:
        handle_emails_without_attachments(ms_graph, email, e)

    except EmailFromBuchhaltung as e:
        logger.exception(msg=e)
        ms_graph.mark_email_as_read(email.message_id)

    except NoBuchhaltungsNummerFoundError as e:
        logger.exception(msg=e)
        send_error_email(
            ms_graph=ms_graph,
            error_msg=f"Error processing email {email.info}: {e}.",
        )
        ms_graph.mark_email_as_read(email.message_id)

    except NoPDForXLSXError as e:
        handle_no_pdf_xlsx_error(ms_graph, email, e)

    except Exception as e:
        unexpected_error_handler(ms_graph, email, e)
    return None


def save_llm_response_to_json(
    file_name: str, llm_response: dict, raw_text: str, saving_path: Path
) -> None:
    """Saves the LLM response to a JSON file.

    Parameters
    ----------
    file_name : str
        The name of the file to save the response to, typically the PDF file name.
    llm_response : dict
        The LLM response containing the extracted information from the PDF.
    raw_text : str
        The raw text extracted from the PDF file.
    saving_path : Path
        The path where the JSON file will be saved.

    """
    json_data = {
        "file_name": file_name,
        "model_output": llm_response,
        "raw_text": raw_text,
    }

    p = saving_path / file_name
    new_name = f"{p.stem}_llm_response.json"
    logger.info("Saving LLM response to JSON file: %s", new_name)
    json_file_path = p.with_name(new_name)
    with json_file_path.open("w", encoding="utf-8") as json_file:
        json_file.write(json.dumps(json_data, indent=4, ensure_ascii=False) + "\n")


def update_soloplan_with_buchhaltungsnummer(
    ms_graph: MSGraphAPI,
    contacts_with_new_buchhaltungsnummer: list,
    soloplan: SoloplanAPI,
) -> None:
    """Updates Soloplan with the new Buchhaltungsnummer for the given contacts.

    Parameters
    ----------
    contacts_with_new_buchhaltungsnummer : list
        List of tuples containing the new contact ID and Buchhaltungsnummer.
    soloplan : SoloplanAPI
        SoloplanAPI instance to interact with Soloplan API.

    """
    try:
        if len(contacts_with_new_buchhaltungsnummer) == 0:
            logger.info("No new Buchhaltungsnummer found.")
            return
        logger.info("Updating Soloplan with new Buchhaltungsnummer...")
        for contact in contacts_with_new_buchhaltungsnummer:
            expected_num_elements = 2
            assert len(contact) == expected_num_elements, (
                "Contact tuple in new contacts list must have exactly 2 elements"
            )
            soloplan.update_Buchhaltungsnummer_Soloplan(contact[0], contact[1])
    except (AssertionError, IndexError) as e:
        logger.exception("Error updating Soloplan with Buchhaltungsnummer")
        send_error_email(
            ms_graph=ms_graph,
            error_msg=f"Error updating Soloplan with Buchhaltungsnummer: {e}",
        )
    except Exception as e:
        logger.exception("Unexpected error updating Soloplan with Buchhaltungsnummer")
        send_error_email(
            ms_graph=ms_graph,
            error_msg=f"Unexpected error updating Soloplan with Buchhaltungsnummer: {e}",
        )


def write_results_to_csv(results: Results, csv_file: Path) -> None:
    """Writes the results of email processing into a CSV file.
    If the CSV file does not exist, it creates a new one with the appropriate headers.
    If the CSV file exists, it appends the new results to the existing file.
    If the row already exists, it does not append it again.

    Parameters
    ----------
    results : Results
        The results object containing the data to be written to the CSV file.
    csv_file : Path
        The path to the CSV file where the results will be saved.

    """
    results_dict = asdict(results)
    if results_dict.get("id") == "N/A":
        return

    try:
        data_f = pd.read_csv(
            csv_file,
            keep_default_na=False,
        )
    except FileNotFoundError:
        new_columns = list(results_dict)
        data_f = pd.DataFrame(columns=new_columns)
    except IsADirectoryError:
        (csv_file / "sepp-dokumentation.csv").touch()
        csv_file = csv_file / "sepp-dokumentation.csv"
        new_columns = list(results_dict)
        data_f = pd.DataFrame(columns=new_columns)

    except pd.errors.EmptyDataError:
        new_columns = list(results_dict)
        data_f = pd.DataFrame(columns=new_columns)

    # Check if the id already exists in the DataFrame
    if not any(data_f["id"] == results_dict["id"]):
        # Append the new row
        data_f = pd.concat([data_f, pd.DataFrame([results_dict])], ignore_index=True)

        # Save the updated DataFrame back to the CSV file
        data_f.to_csv(csv_file, index=False, encoding="utf-8")


def finalize_successful_processing(
    ms_graph: MSGraphAPI,
    email: Email,
    email_processing_results: Results,
    client: str,
    external_number: str,
    transport_order_number: str,
) -> None:
    """Finalizes the successful processing of the email.
    Sends a success message to the sender, marks the email as read and moves it to the "ERLEDIGT" folder.
    If the Graph API returns an unsuccessful response, the email is not moved and an error message is sent to the admins.

    Parameters
    ----------
    email : Email
        The email object being processed.
    email_processing_results : Results
        The results object to store the results of the email processing.
    client : str
        The name of the client.
    order_number : str
        The order number of the transport order.
    external_number : str
        The external number of the transport order.
    transport_order_number : str
        The booking number of the transport order in Soloplan.

    """
    logger.info("All tasks completed successfully, finalizing...")
    success_email = send_success_email(
        ms_graph=ms_graph,
        primary_recipient=email.sender,
        client_name=client,
        transport_order_number=transport_order_number,
        external_number=external_number,
    )

    if not success_email.success:
        ms_graph.mark_email_as_read(email.message_id)
        error_msg = (
            f"{email.info} was processed successfully but we failed ",
            f"to send a confirmation mail to andreas for the transport order: {transport_order_number}",
        )
        logger.error(error_msg)
        send_error_email(
            ms_graph=ms_graph,
            error_msg=error_msg,
        )
    else:
        email_processing_results.update({"oppel_info_mail": time_now()})
        ms_graph.mark_email_as_read(email.message_id)
        ms_graph.move_email(email.message_id, destination_folder=ERLEDIGT_ID)
        logger.info("Successfully processed %s", email.info)


def collect_unread_emails(ms_graph: MSGraphAPI) -> list[dict] | None:
    """Collects unread emails from the inbox using the Microsoft Graph API.

    Returns
    -------
    list[dict] | None
        A list of unread email dictionaries if successful, or None if there was an error.

    """
    logger.info("Collecting unread emails...")
    ms_graph_response = fetch_unread_emails(ms_graph)

    if ms_graph_response_unsuccessful(ms_graph=ms_graph, response=ms_graph_response):
        return None

    return ms_graph_response.value


def get_existing_llm_response(
    pdf_file_path: Path,
) -> tuple[dict | None, str | None]:
    # Check if the PDF file already has a corresponding JSON file with the LLM response

    checked_file = pdf_file_path.with_name(f"{pdf_file_path.stem}_llm_response.json")

    if checked_file.exists():
        logger.info(
            "LLM response already exists for %s, skipping extraction",
            pdf_file_path.name,
        )

        with checked_file.open("r", encoding="utf-8") as f:
            results = json.load(f)
        llm_response_dict = results.get("model_output")
        raw_pdf_text = results.get("raw_text")
        return llm_response_dict, raw_pdf_text
    return None, None


def extract_information_from_pdf(
    ms_graph: MSGraphAPI,
    email: Email,
    pdf_file_path: Path,
    email_processing_results: Results,
    saving_path: Path,
) -> tuple[dict, str]:
    """Extracts information from the PDF file using an LLM, returns the LLM response as a dictionary with the extracted information and the raw text from the PDF.

    Runs the `get_llm_response` function from the `extract_info_from_pdf` module to get the LLM response.
    Handles various exceptions that may occur during the extraction process:
    - LLMResponseIncompleteError: If the LLM response is incomplete and logs it.
    - Exception: Catches any other unexpected errors and logs them.
    - - If the exception is related to the LLM being out of tokens (error code 429), it sends an error email to admins and waits for 5 minutes before retrying within the while loop.

    If the extraction is unsuccessful (i.e., the LLM response dictionary or raw PDF text is None), it sends an `error` message to admins,
    `failed` message to the sender of the email, marks the email as read, and moves it to the "FAILED" folder.
    Updates the `email_processing_results` object with the `Failed` status and the time of the response.

    If the extraction is successful, it updates the `email_processing_results` object with the `Success` status,
    the time of the response, the client name, and the order ID.
    Saves the LLM response to a JSON file in the specified saving path.

    Parameters
    ----------
    email : Email
        The email object being processed, containing metadata about the email.
    pdf_file_path : Path
        The path to the PDF file that was processed, which contains the extracted information.
    email_processing_results : Results
        The results object to store the results of the email processing, including LLM status and timestamps.
    ms_graph : MSGraphAPI
        MSGraphAPI instance to interact with Microsoft Graph API.
    saving_path : Path
        The path where the results will be saved, typically the same directory as the PDF file.

    Returns
    -------
    tuple[dict | None, str | None]
        A tuple containing the LLM response dictionary with the extracted information and the raw text from the PDF.
        If an error occurs, returns (None, None).

    """
    llm_response_dict, raw_pdf_text = get_existing_llm_response(
        pdf_file_path=pdf_file_path,
    )

    while not llm_response_dict or not raw_pdf_text:
        try:
            llm_response_dict, raw_pdf_text = get_llm_response(
                pdf_path=pdf_file_path,
            )
            break

        except LLMResponseIncompleteError:
            logger.exception("Could not extract essential info from PDF")
            error_msg = f"LLM response appears to be incomplete: could not extract some crucial info from PDF: {pdf_file_path.name} from {email.info}"
            llm_response_dict, raw_pdf_text = {}, ""
            break

        except RateLimitError:
            logger.exception("Error processing PDF with LLM (429 - out of tokens)")
            error_msg = "Hilfe, dem SEPP ist das Geld für ChatGPT ausgegangen!"
            send_error_email(
                ms_graph=ms_graph,
                error_msg=error_msg,
            )
            time.sleep(300)
            continue

        except Exception as e:
            error_msg = f"Unexpected error processing PDF with LLM: {e}"
            logger.exception("Unexpected error processing PDF with LLM")
            llm_response_dict, raw_pdf_text = {}, ""
            break

    if not llm_response_dict or not raw_pdf_text:
        error_msg = f"Unexpected error processing PDF with LLM: {pdf_file_path.name} from {email.info}"
        msg_to_customer = f"SEPP konnte leider nicht Informationen aus der PDF von der Email gesendet von {email.sender} am {email.sent_date} mit dem Betreff {email.subject} extrahieren."
        send_error_email(
            ms_graph=ms_graph,
            error_msg=error_msg,
            path_to_folder=pdf_file_path.parent,
        )
        send_failed_email(
            ms_graph=ms_graph,
            email=email,
            explanation=msg_to_customer,
            pdf_path=pdf_file_path,
        )
        ms_graph.mark_email_as_read(email.message_id)
        move_failed_mail(ms_graph, email)
        email_processing_results.update(
            {
                "llm_status": "Failed",
                "time_of_llm_response": time_now(),
            }
        )

    else:
        email_processing_results.update(
            {
                "llm_status": "Success",
                "time_of_llm_response": time_now(),
                "client": llm_response_dict.get("client", {}).get("name"),
                "order_id": llm_response_dict.get("order_id"),
            }
        )
        save_llm_response_to_json(
            pdf_file_path.name,
            llm_response_dict,
            raw_text=raw_pdf_text,
            saving_path=saving_path,
        )

    return llm_response_dict, raw_pdf_text


def notify_buchhaltung(
    ms_graph: MSGraphAPI, business_contacts_list: list, pdf_file_path: Path
) -> None:
    """Sends an email to Buchhaltung with the new business contacts."""
    if len(business_contacts_list) > 0:
        send_email_to_buchhaltung(
            ms_graph=ms_graph,
            businesscontact=business_contacts_list,
            pdf_path=pdf_file_path,
        )


def setup_output_folder() -> Path:
    """Creates the output folder for results if it doesn't exist."""
    output_folder = BASE_DIR / "Results"
    output_folder.mkdir(parents=True, exist_ok=True)
    return output_folder


def main(
    soloplan_api: SoloplanAPI, ms_graph: MSGraphAPI, *, debug: bool = False
) -> None:
    # create a folder for output results
    output_folder = setup_output_folder()
    current_day = datetime.now(tz=ZoneInfo("Europe/Berlin")).day
    email_processing_results = Results()

    while True:
        time.sleep(SLEEP_INTERVAL)
        if datetime.now(tz=ZoneInfo("Europe/Berlin")).day != current_day:
            current_day = datetime.now(tz=ZoneInfo("Europe/Berlin")).day
            setup_logging()

        ### Email processing block ###
        try:
            soloplan_api.refresh_token()
            logger.info("%s Starting a new SEPP session %s", "v" * 25, "v" * 25)

            write_results_to_csv(
                email_processing_results,
                csv_file=output_folder / "sepp-dokumentation.csv",
            )  # write the results of the previous iteration to the csv file
            email_processing_results = Results()

            emails = collect_unread_emails(ms_graph)
            if not emails:
                logger.info(
                    "No unread emails. Sleeping for %d seconds...", SLEEP_INTERVAL
                )
                continue

            contacts_with_new_buchhaltungsnummer: list[tuple] = []

            for e in emails:
                logger.info("%s Processing email %s", "-" * 30, "-" * 30)
                write_results_to_csv(
                    email_processing_results,
                    csv_file=output_folder / "sepp-dokumentation.csv",
                )  # write the results of the previous iteration to the csv file
                email_processing_results = Results()
                email = wrap_email(e)

                pdf_file_path = process_email_to_order(
                    ms_graph=ms_graph,
                    email=email,
                    contacts_with_new_buchhaltungsnummer=contacts_with_new_buchhaltungsnummer,
                    email_processing_results=email_processing_results,
                    saving_path=output_folder,
                )

                if not pdf_file_path or email_cannot_be_retried(
                    email=email, ms_graph=ms_graph, pdf_file_path=pdf_file_path
                ):
                    continue

                logger.info(
                    "Retrieved PDF file: %s. Processing with LLM ...",
                    pdf_file_path.name,
                )

                email_processing_results.update(
                    {"attachment": True, "time_attachment_found": time_now()}
                )

                ### Entry point for the pdf processing ###
                llm_response_dict, raw_pdf_text = extract_information_from_pdf(
                    email=email,
                    email_processing_results=email_processing_results,
                    pdf_file_path=pdf_file_path,
                    ms_graph=ms_graph,
                    saving_path=pdf_file_path.parent,
                )

                if not llm_response_dict or not raw_pdf_text:
                    continue

                if debug:
                    logger.info(
                        "Running in DEBUG mode, using fake order id: 000_%s for soloplan order creation",
                        time_now(),
                    )

                    llm_response_dict["order_id"] = f"000_{time_now()}"

                ### soloplan order creation block ###
                logger.info(
                    "LLM-processed data received, creating order in Soloplan..."
                )
                response_data, business_contacts_new = create_order_with_soloplan(
                    llm_response_dict,
                    raw_pdf_text,
                    ms_graph=ms_graph,
                    email=email,
                    pdf_file_path=pdf_file_path,
                    saving_path=pdf_file_path.parent,
                    soloplan=soloplan_api,
                    results=email_processing_results,
                    is_test=False,
                )

                if not response_data:
                    continue

                notify_buchhaltung(ms_graph, business_contacts_new, pdf_file_path)

                finalize_successful_processing(
                    ms_graph=ms_graph,
                    email=email,
                    email_processing_results=email_processing_results,
                    client=llm_response_dict.get("client", {}).get("name", "N/A"),
                    external_number=response_data.get("ExternalNumber", "N/A"),
                    transport_order_number=response_data.get("Number", "N/A"),
                )

            update_soloplan_with_buchhaltungsnummer(
                ms_graph, contacts_with_new_buchhaltungsnummer, soloplan_api
            )
            logger.info(
                "All emails processed. Ending SEPP session, sleeping for %d seconds...",
                SLEEP_INTERVAL,
            )

        except Exception as e:
            logger.exception("Unexpected error in main loop")
            logger.info(
                "Unexpected error in main loop, sending error email and exiting..."
            )
            send_error_email(
                ms_graph=ms_graph,
                error_msg=f"Unexpected error occurred in sepp main loop: {e}",
            )
            send_failed_email(
                ms_graph=ms_graph,
                email=email,
                explanation="SEPP konnte leider nicht die PDF von der Email gesendet von "
                f"{email.sender} am {email.sent_date} mit dem Betreff {email.subject} verarbeiten.",
                pdf_path=pdf_file_path if "pdf_file_path" in locals() else None,
            )
            continue


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="SEPP Main Script")

    argparser.add_argument(
        "--mock_soloplan",
        action="store_true",
        help="Run with a mock Soloplan order creation",
        default=False,
    )

    argparser.add_argument(
        "--debug",
        action="store_true",
        help="Run in debug mode with fake order IDs",
        default=False,
    )

    args = argparser.parse_args()

    setup_logging()
    logger.info("SEPP started, logging initialized.")

    try:
        ms_graph = microsoft.MSGraphAPI(**asdict(ms_graph_config))
        logger.info("MS Graph API initialized successfully.")
    except Exception as e:
        logger.exception("Failed to initialize MS Graph API. Exiting...")
        send_error_email(
            ms_graph=ms_graph,
            error_msg=f"Failed to initialize MS Graph API: {e}",
        )
        sys.exit(1)

    if not args.mock_soloplan:
        try:
            soloplan = SoloplanAPI(**asdict(soloplan_config))
            logger.info("Soloplan API initialized successfully.")
        except Exception as e:
            logger.exception("Failed to initialize Soloplan API. Exiting...")
            send_error_email(
                ms_graph=ms_graph,
                error_msg=f"Failed to initialize Soloplan API: {e}",
            )
            sys.exit(1)
    else:
        soloplan = fake_soloplan_api()
        logger.info("Using mocked Soloplan API.")

    create_retries_csv()  # Create the CSV file for retries if it does not exist
    main(
        soloplan_api=soloplan, ms_graph=ms_graph, debug=args.debug
    )  # Pass the SoloplanAPI instance to main
