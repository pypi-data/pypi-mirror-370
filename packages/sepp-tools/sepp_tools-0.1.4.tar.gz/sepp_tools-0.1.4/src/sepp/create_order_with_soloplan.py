import json
import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from microsoft.connectors.api import MSGraphAPI
from soloplan import SoloplanAPI
from soloplan.connectors.api import SoloplanResponse

from sepp.commons import Email, Results
from sepp.scripts.mailing_script import (
    send_error_email,
    send_failed_email,
    send_generic_email,
)
from sepp.settings import (
    BASE_DIR,
    ERLEDIGT_ID,
    FAILED_ID,
)

logger = logging.getLogger(__name__)


def time_now() -> str:
    """Returns the current day-time in the format 'DD.MM.YYYY HH:MM:SS' in the Europe/Berlin timezone."""
    return datetime.now(tz=ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y %H:%M:%S")


def update_retries_log(unique_email_id: str, last_retry: datetime) -> None:
    retries_log_path = BASE_DIR / "soloplan_retries_df.csv"
    # Ensure columns are set even if the file is empty
    columns = ["unique_email_id", "retries", "last_retry"]
    try:
        retries_log_df = pd.read_csv(retries_log_path)
    except FileNotFoundError:
        retries_log_df = pd.DataFrame(columns=columns)

    if unique_email_id not in retries_log_df["unique_email_id"].to_numpy():
        new_entry = pd.DataFrame(
            {
                "unique_email_id": [unique_email_id],
                "retries": [1],
                "last_retry": [last_retry],
            }
        )
        # Only concat if new_entry is not empty or all-NA
        if not new_entry.empty and not new_entry.isna().all(axis=None):
            retries_log_df = pd.concat([retries_log_df, new_entry], ignore_index=True)
    else:
        retries_log_df.loc[
            retries_log_df["unique_email_id"] == unique_email_id, "last_retry"
        ] = last_retry
        retries_log_df.loc[
            retries_log_df["unique_email_id"] == unique_email_id, "retries"
        ] += 1

    retries_log_df.to_csv(retries_log_path, index=False)


def create_order_with_soloplan(
    llm_response: dict,
    raw_pdf_text: str,
    *,
    ms_graph: MSGraphAPI,
    email: Email,
    pdf_file_path: Path,
    saving_path: Path,
    soloplan: SoloplanAPI,
    results: Results,
    is_test: bool = False,
) -> tuple[dict, list]:
    """Creates an order in Soloplan using the provided LLM response and raw PDF text.

    Parameters
    ----------
    llm_response : dict
        The response from the LLM containing order details.
    raw_pdf_text : str
        The raw text extracted from the PDF file.
    ms_graph : MSGraphAPI
        MSGraphAPI instance to interact with Microsoft Graph API.
    email : Email
        The email object being processed.
    pdf_file_path : Path
        The path to the PDF file. Needed for error handling and saving results.
    saving_path : Path
        The path where the results will be saved.
    soloplan : SoloplanAPI
        SoloplanAPI instance to interact with Soloplan API.
    results : Results
        The results object to store the results of the order creation.
    is_test : bool, optional
        If True, the order will be created in test mode. Default is False.

    Returns
    -------
    tuple[dict, list]
        A tuple containing the Soloplan response, order JSON, list of new business contacts, and the found_in string.

    """
    llm_response_str = json.dumps(
        llm_response,
    )
    now_dt = datetime.now(tz=ZoneInfo("Europe/Berlin"))
    date_iso = now_dt.date().isoformat()

    try:
        soloplan_response, order, business_contacts_new, found_in = (
            soloplan.create_order(
                model_output=llm_response_str,  # expecting a JSON string
                raw_text=raw_pdf_text,
                order_date=date_iso,  # Placeholder date, will be updated later
                info_text="",
                is_test=is_test,
            )
        )

    except ValueError as e:
        if "search and creation" in str(e).lower():
            error_msg = (
                f"Soloplan API has raised the 'Search and Creation' error while processing an {email.info}.\n"
                "The retries log for this email will be updated with the current time and the email will be retried in 2 minutes. The client is not notified at this point."
            )

            logger.warning(error_msg)
            send_error_email(
                ms_graph=ms_graph, error_msg=error_msg, path_to_folder=saving_path
            )

            update_retries_log(
                unique_email_id=email.unique_id,
                last_retry=datetime.now(tz=ZoneInfo("Europe/Berlin")),
            )

        return {}, []

    except Exception as e:
        error_msg = (
            f"Soloplan API has raised an unexpected error while processing an {email.info}\n"
            f"Error: {e}\n"
            "Email will be marked as read, moved to the 'Failed' folder and the client will be notified."
        )

        logger.exception(error_msg)

        send_error_email(
            ms_graph=ms_graph,
            error_msg=f"{error_msg}:\n{e}",
            path_to_folder=saving_path,
        )

        message_to_customer = "SEPP konnte den Auftrag leider nicht anlegen, da Soloplan CarLo einen Fehler zurückgegeben hat"
        send_failed_email(
            ms_graph=ms_graph,
            email=email,
            explanation=message_to_customer,
            pdf_path=pdf_file_path,
        )
        ms_graph.mark_email_as_read(email.message_id)
        ms_graph.move_email(email.message_id, destination_folder=FAILED_ID)
        return {}, []

    else:
        if not soloplan_response.success:
            if "as it already exists" in soloplan_response.info:
                order_number = llm_response.get("order_id", "")

                message = f"Der Auftrag {order_number} von {email.info}konnte nicht erneut angelegt werden, da er bereits existiert."

                logger.info("Order already exists in Soloplan")

                ms_graph.mark_email_as_read(email.message_id)
                send_generic_email(
                    ms_graph=ms_graph,
                    primary_recipient=email.sender,
                    message=message,
                    bcc_list=["shlychkov@kolibrain.de"],
                    subject=f"Auftrag {order_number} bereits existiert",
                )
                ms_graph.move_email(email.message_id, destination_folder=ERLEDIGT_ID)
                results.update({"order_already_exists": True})
                return {}, []

            error_msg = (
                f"Soloplan returned a response but the model was unsuccessful: {soloplan_response.info}\n"
                f"while processing an {email.info}.\n"
                "The email will be mark as read, moved to the 'Failed' folder and the client will be notified."
            )
            logger.error(error_msg)
            send_error_email(
                ms_graph=ms_graph,
                error_msg=error_msg,
                path_to_folder=saving_path,
            )
            message_to_customer = "SEPP konnte leider den Auftrag leider nicht anlegen, da Soloplan CarLo einen Fehler zurückgegeben hat"
            send_failed_email(
                ms_graph=ms_graph,
                email=email,
                explanation=message_to_customer,
                pdf_path=pdf_file_path,
            )
            ms_graph.mark_email_as_read(email.message_id)
            ms_graph.move_email(email.message_id, destination_folder=FAILED_ID)
            return {}, []

    response_data = get_soloplan_response_data(soloplan_response)
    save_json_with_soloplan_results(
        soloplan_response=soloplan_response,
        order_json=order,
        file_name=pdf_file_path.name,
        saving_path=saving_path,
    )

    results.update(
        {
            "found_in": found_in,
            "new_contacts": business_contacts_new,
            "transport_order_number": response_data.get("Number", "N/A"),
            "time_soloplan_booked": time_now(),
        }
    )
    logger.info(
        "Successfully created order with Soloplan and saved results to JSON file."
    )
    return response_data, business_contacts_new


def save_json_with_soloplan_results(
    soloplan_response: SoloplanResponse,
    order_json: dict,
    file_name: str,
    saving_path: Path,
) -> None:
    """Saves the Soloplan response and order JSON to a JSONL file.

    Parameters
    ----------
    soloplan_response : SoloplanResponse
        The response from the Soloplan API after creating an order.
    order_json : dict
        The JSON representation of the order created in Soloplan.
    file_name : str
        The name of the PDF file associated with the order, used to create the JSONL file name.
    saving_path : Path
        The path where the JSONL file will be saved.

    """
    json_data = {
        "date": datetime.now(tz=ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y %H:%M"),
        "soloplan_success": soloplan_response.success,
        "soloplan_response": soloplan_response.value,
        "order_json": order_json,
    }

    p = saving_path / file_name
    new_name = f"{p.stem}_soloplan_order.json"
    json_file_path = p.with_name(new_name)
    with json_file_path.open("w") as json_file:
        json_file.write(json.dumps(json_data, indent=4, ensure_ascii=False) + "\n")


def get_soloplan_response_data(soloplan_response: SoloplanResponse) -> dict:
    """Extracts the default filter values from the Soloplan response.

    Parameters
    ----------
    soloplan_response : SoloplanResponse
        _description_

    Returns
    -------
    dict
        A dictionary containing the default filter values from the Soloplan response.

    """
    try:
        resp_data = soloplan_response.value["dataSets"][0]["defaultFilterValues"]
    except (KeyError, IndexError):
        logger.exception("Error extracting data from Soloplan response")
        return {}
    except Exception:
        logger.exception(
            "Unexpected error while extracting data from Soloplan response"
        )
        return {}

    return {d["key"]: d["value"] for d in resp_data}
