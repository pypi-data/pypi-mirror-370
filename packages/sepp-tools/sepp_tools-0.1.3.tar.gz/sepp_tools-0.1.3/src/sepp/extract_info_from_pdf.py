import base64
import json
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

import openai
import PyPDF2
from pdf2image import convert_from_path

from sepp.exceptions import LLMResponseIncompleteError
from sepp.llm_prompts import return_client_prompt, return_transports_prompt
from sepp.scripts.geocoding import (
    geocode_with_google,
    geocode_with_nominatim,
)
from sepp.scripts.llm_response_hardcoded_cases import apply_hardcoded_cases
from sepp.settings import (
    OPENAI_API_KEY,
)

if TYPE_CHECKING:
    from openai.types.chat import (
        ChatCompletionContentPartImageParam,
        ChatCompletionContentPartTextParam,
        ChatCompletionMessageParam,
    )

GOOGLE_API = "AIzaSyDm7dmhpfaFy4KLSslwDVdj2Ae2rLWzq-M"
MAX_RETRIES = 2


logger = logging.getLogger(__name__)


REQUIRED_TRANSPORT_FIELDS = {
    "sender_name": lambda t: t.get("sender", {}).get("name", ""),
    "sender_city": lambda t: t.get("sender", {}).get("city", ""),
    "receiver_name": lambda t: t.get("receiver", {}).get("name", ""),
    "receiver_city": lambda t: t.get("receiver", {}).get("city", ""),
    "loading_date": lambda t: bool(t.get("loadingDate")) and all(t.get("loadingDate")),
    "delivery_date": lambda t: bool(t.get("deliveryDate"))
    and all(t.get("deliveryDate")),
}


def _handle_oppel(pdf_path: Path) -> tuple[dict[str, Any], str]:
    """Handles the case when the customer is Oppel.
    Makes the LLM rerun the PDF processing and returns the new response.

    Parameters
    ----------
    llm_response : dict
        The response from the LLM
    pdf_path : str
        The path to the PDF file.

    Returns
    -------
    tuple[dict, str]
        A tuple containing the new LLM response and the raw text, extracted from the PDF.

    """
    logger.info(
        "Oppel was selected as customer by ChatGPT what might be wrong. Try again!"
    )
    llm_response, raw_pdf_text = pdf_to_json(pdf_path, OPENAI_API_KEY)
    return llm_response, raw_pdf_text


def _handle_incomplete_response(
    pdf_path: Path, missing_items: list
) -> tuple[dict[str, Any], str]:
    logger.info("The LLM response was incomplete. Trying to rerun the PDF processing.")

    transport_info_missing = [
        item for item in missing_items if item in REQUIRED_TRANSPORT_FIELDS
    ]

    client_info_missing = [
        item for item in missing_items if item not in REQUIRED_TRANSPORT_FIELDS
    ]

    additional_instruction_transports = f"Last time your response was incomplete. Put additional on the following entries you missed: {', '.join(transport_info_missing)}."
    additional_instruction_client = f"Last time your response was incomplete. Put additional on the following entries you missed: {', '.join(client_info_missing)}."

    completed_llm_response, raw_pdf_text = pdf_to_json(
        pdf_path,
        api_key=OPENAI_API_KEY,
        additional_instructions_client=additional_instruction_client,
        additional_instructions_transports=additional_instruction_transports,
    )
    return completed_llm_response, raw_pdf_text


def get_llm_response(
    pdf_path: Path, max_retries: int = 2
) -> tuple[dict[str, Any], str]:
    """Extracts information from a PDF file using an LLM.

    This function processes the PDF file, checks for required fields in the
    transport and client information, and attempts to fill in any missing
    fields through retries. If the LLM response is still incomplete after
    the maximum number of retries, it raises an `LLMResponseIncompleteError`.

    Parameters
    ----------
    pdf_path : Path
        The path to the PDF file to be processed.
    max_retries : int, optional
        The maximum number of retries to attempt if the LLM response is incomplete.

    Returns
    -------
    tuple[dict[str, Any], str]
        A tuple containing:
        - A dictionary with the LLM response containing transport and client information.
        - A string with the raw text extracted from the PDF.

    Raises
    ------
    LLMResponseIncompleteError
        If the LLM response is incomplete after the maximum number of retries.

    """
    logger.info("Processing PDF: %s", pdf_path)

    # Initial run
    llm_dict, raw_text = pdf_to_json(pdf_path, OPENAI_API_KEY)

    # Special “Oppel” customer case
    if llm_dict.get("client", {}).get("name", "").upper().find("OPPEL") != -1:
        logger.info("Detected 'OPPEL' in client name, re-running PDF processing.")
        llm_dict, raw_text = _handle_oppel(pdf_path)

    logger.info("LLM response received, checking for missing fields.")

    for attempt in range(1, max_retries + 1):
        transport_missing = _check_transports(llm_dict)
        client_missing, client_available = _check_client_fields(
            llm_dict.get("client", {})
        )

        if not transport_missing and not client_missing:
            logger.info("All required fields are present.")
            break

        logger.info(
            "Attempt %d/%d - transports missing %s, client missing %s",
            attempt,
            max_retries,
            transport_missing,
            client_missing,
        )

        # If the only missing things are client geo-fields, try to infer them
        geo_fields = {"zip", "city", "country"}
        if not transport_missing and set(client_missing).issubset(geo_fields):
            _fill_in_missing_for_client(llm_dict.get("client", {}), client_available)
            client_missing, _ = _check_client_fields(llm_dict.get("client", {}))
            if not client_missing:
                break

        # Otherwise, ask LLM to fill in missing transport or client data

        llm_dict, raw_text = _handle_incomplete_response(
            pdf_path, transport_missing + client_missing
        )

    apply_hardcoded_cases(llm_dict)
    _final_sanity_check(llm_dict)

    raw_text = _check_and_fill_raw_text(llm_dict, raw_text)
    logger.info("Final check passed, returning results.")
    return llm_dict, raw_text


def _check_and_fill_raw_text(llm_dict: dict[str, Any], raw_text: str) -> str:
    """Check if the raw text is empty and fill it with the LLM response values if necessary.

    Parameters
    ----------
    llm_dict : dict[str, Any]
        The LLM response containing transport and client information.
    raw_text : str
        The raw text extracted from the PDF file.

    Returns
    -------
    str
        The raw text, either the original or filled with the LLM response values if it was empty.

    """
    if len(raw_text) == 0:
        logger.warning("Raw text is empty, trying to fill it with the LLM response.")
        return str([v for k, v in llm_dict.items()])
    return raw_text


def _check_transports(llm: dict[str, Any]) -> list[str]:
    """Check if all required transport fields are present in the LLM response.

    Parameters
    ----------
    llm : dict[str, Any]
        The LLM response containing transport information.

    Returns
    -------
    list[str]
        A list of missing transport fields, formatted as "transport[index].field_name".
        If no transports are present, returns ["transports"].

    """
    transports = llm.get("transports") or []
    missing: list[str] = []
    if not transports:
        return ["transports"]
    for idx, t in enumerate(transports, start=1):
        for name, fn in REQUIRED_TRANSPORT_FIELDS.items():
            if not fn(t):
                missing.append(f"transport[{idx}].{name}")
    return missing


def _geocode_client(client: dict, available_fields: list[str]) -> dict[str, Any]:
    """Geocode the client information to fill in missing fields like city, zip, and country.
    Uses Nominatim if city or zip is available, otherwise uses Google Maps API.

    Parameters
    ----------
    client : dict
        The client information dictionary from the LLM response.
    available_fields : list[str]
        A list of fields that are available in the client information.

    Returns
    -------
    dict[str, Any]
        A dictionary containing the geocoded fields that were missing in the client information.
        Returns an empty dictionary if no geocoding was possible or if all fields were already filled.

    """
    name = client.get("name")
    if not name:
        logger.error("Client name is missing, cannot geocode.")
        return {}

    cues = [client[f] for f in available_fields if client.get(f)]

    if {"zip", "city"} & set(available_fields):
        # if we have zip or city, we can use Nominatim
        logger.info("Geocoding via Nominatim using %s", cues)
        result = geocode_with_nominatim(available_location_cues=cues)

        if not all(result.get(field) for field in ("city", "country", "zip")):
            logger.warning("Nominatim geocoding failed, trying Google Maps API.")
            # If Nominatim fails, we must use Google
            cues = [name, *cues]
            result = geocode_with_google(query=" ".join(cues), api=GOOGLE_API)
    else:
        logger.info("No city or zip available, using Google for %s: %s", name, cues)
        # If we don't have city or zip, we must use Google
        cues = [name, *cues]
        result = geocode_with_google(query=" ".join(cues), api=GOOGLE_API)

    # return only the fields we actually filled
    return {k: v for k, v in result.items() if k not in available_fields and v}


def _check_client_fields(client: dict) -> tuple[list[str], list[str]]:
    """Check if all required client fields are present in the LLM response.

    Parameters
    ----------
    client : dict
        The client information dictionary from the LLM response.

    Returns
    -------
    tuple[list[str], list[str]]
        A tuple containing:
        - A list of missing client fields that are mandatory.
        - A list of available client fields that are present in the response.

    """
    missing: list[str] = []
    available: list[str] = []
    if not client.get("name"):
        missing.append("name")
    for cue in ("street", "houseNumber", "zip", "city", "country"):
        (available if client.get(cue) else missing).append(cue)

    mandatory = {"name", "zip", "city", "country"}
    return list(set(missing) & mandatory), available


def _final_sanity_check(llm_response: dict[str, Any], max_retries: int = 2) -> None:
    """Check if the LLM response is complete after processing.
    This function verifies that all required fields in the transport and client
    information are present. If any fields are still missing, it raises an
    `LLMResponseIncompleteError`.

    Parameters
    ----------
    llm_response : dict[str, Any]
        The LLM response containing transport and client information.
    max_retries : int, optional
        The maximum number of retries to attempt if the response is incomplete, by default 2.

    Raises
    ------
    LLMResponseIncompleteError
        If the LLM response is still incomplete after processing, indicating that
        required fields are missing in the transport or client information.

    """
    final_transport = _check_transports(llm_response)
    final_client_missing, _ = _check_client_fields(llm_response.get("client", {}))
    if final_transport or final_client_missing:
        error_msg = (
            f"LLM response is still incomplete after {max_retries} attempts and applying hardcoded cases. "
            f"Missing fields: {final_transport + final_client_missing}"
        )
        raise LLMResponseIncompleteError(error_msg)


def _fill_in_missing_for_client(
    client_dict: dict[str, Any], client_available: list[str]
) -> None:
    geocoded = _geocode_client(client_dict, client_available)
    if geocoded:
        # record what we filled in
        for k in geocoded:
            client_dict[k] = geocoded[k]


def pdf_to_json(
    pdf_path: Path,
    api_key: str,
    additional_instructions_client: str = "",
    additional_instructions_transports: str = "",
) -> tuple[dict[str, Any], str]:
    extracted_text = extract_text_from_pdf(pdf_path)

    if not extracted_text:
        extracted_text = ""

    entities = extract_entities_from_text(extracted_text, pdf_path, api_key)

    json_data = generate_json_with_retry(
        extracted_text,
        pdf_path,
        api_key,
        entities,
        additional_instructions_client=additional_instructions_client,
        additional_instructions_transports=additional_instructions_transports,
    )

    if not json_data:
        logger.error("No json data given for this transport order.")
        return {}, ""

    return json.loads(json_data), extracted_text


def extract_text_from_pdf(pdf_path: Path) -> str:
    try:
        with pdf_path.open("rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
            logger.info(
                "Successfully extracted the text from the pdf. The text has %d characters.",
                len(text),
            )
            return text
    except Exception:
        logger.exception("Error reading PDF file")
        return ""


def extract_entities_from_text(
    text: str, pdf_path: Path, api_key: str
) -> dict[str, str]:
    """Ask GPT to identify Auftraggeber/Absender/Empfänger/Spediteur in the given text/PDF.
    Returns a dict like {"Auftraggeber": "...", "Absender": "...", "Empfänger": "...", "Spediteur": "..."}.
    """
    openai.api_key = api_key

    pages: list[Path] = convert_pdf_to_image(pdf_path)

    prompt = (
        "Identifiziere im folgenden Text alle genannten Organisationen und Personen "
        "sowie ihre Rolle im Transportauftrag (Auftraggeber, Absender, Empfänger, Spediteur). "
        "Gib die Ergebnisse in folgendem Format zurück:\n\n"
        "Auftraggeber: [Name]\n"
        "Absender: [Name]\n"
        "Empfänger: [Name 1], [Name 2], ...\n"
        "Spediteur: [Name]\n\n"
        f"Text:\n{text}"
    )

    # Build multimodal content with precise types for mypy:
    content_parts: list[
        ChatCompletionContentPartTextParam | ChatCompletionContentPartImageParam
    ] = [{"type": "text", "text": prompt}]
    for path_to_page in pages:
        base64_image = encode_image(image_path=path_to_page)
        content_parts.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            }
        )

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": content_parts},
    ]

    resp = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )

    raw_output = resp.choices[0].message.content or ""
    # Parse the simple role: value lines
    entities: dict[str, str] = {}
    for raw_line in raw_output.splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        role, value = line.split(":", 1)
        role = role.strip()
        value = value.strip()
        if role and value:
            entities[role] = value

    return entities


def encode_image(image_path: Path) -> str:
    with image_path.open("rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def convert_pdf_to_image(pdf_path: Path) -> list[Path]:
    images = convert_from_path(pdf_path.as_posix())
    pages = []
    for i in range(len(images)):
        # Save pages as images in the pdf
        tmp_dir = Path.cwd() / "transport_orders_imgs"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        images[i].save(tmp_dir / f"page{i}.jpg", "JPEG")
        path_to_page = tmp_dir / f"page{i}.jpg"
        pages.append(path_to_page)

    return pages


def generate_json_with_retry(
    text: str,
    pdf_path: Path,
    key: str,
    entities: dict[str, str] | None = None,
    retries: int = 3,
    additional_instructions_client: str = "",
    additional_instructions_transports: str = "",
) -> str | None:
    for attempt in range(retries):
        logger.info("Start retry number: %d for GPT", attempt)
        json_data = generate_json_from_text(
            text,
            pdf_path,
            key,
            entities,
            additional_instructions_transports=additional_instructions_transports,
            additional_instructions_client=additional_instructions_client,
        )
        if json_data and "client" in json_data:
            return json_data
        logger.error(
            "Attempt %d failed to get complete JSON data, retrying...", attempt + 1
        )
    return None


def generate_json_from_text(
    text: str,
    pdf_path: Path,
    key: str,
    entities: dict[str, str] | None = None,
    additional_instructions_client: str = "",
    additional_instructions_transports: str = "",
) -> str | None:
    openai.api_key = key

    prompts = []
    prompts.append(
        return_client_prompt(
            text,
            entities.get("Auftraggeber", "") if entities else "",
            additional_instructions=additional_instructions_client,
        )
    )
    prompts.append(
        return_transports_prompt(
            text,
            entities if entities else {},
            additional_instructions=additional_instructions_transports,
        ),
    )

    pages = convert_pdf_to_image(pdf_path)

    try:
        json_output: list[dict[str, Any]] = []
        for prompt in prompts:
            content_parts: list[
                ChatCompletionContentPartTextParam | ChatCompletionContentPartImageParam
            ] = [{"type": "text", "text": prompt}]
            for path_to_page in pages:
                base64_image = encode_image(image_path=path_to_page)
                content_parts.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    }
                )

            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": content_parts},
            ]

            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )
            raw_output = response.choices[0].message.content

            logger.info("Raw prompt output: %s", raw_output)

            # Delete comments from the code
            if raw_output:
                json_output.append(_sanitize_raw_llm_output(raw_output))

        if json_output:
            result = {
                "client": json_output[0].get("client", {}),
                "order_id": json_output[0].get("overall", {}).get("orderID", ""),
                "transports": json_output[1].get("transports", []),
            }
        return json.dumps(result)

    except json.JSONDecodeError:
        logger.exception("JSON decoding error")
        return None
    except Exception:
        logger.exception("Error generating JSON from text")
        return None


def _sanitize_raw_llm_output(raw_output: str) -> dict[str, Any]:
    raw_output = re.sub(
        r"//.*?$|/\*.*?\*/", "", raw_output, flags=re.DOTALL | re.MULTILINE
    )

    if "transports" in raw_output.lower():
        json_match = re.search(r'({.*"transports": \[.*\].*})', raw_output, re.DOTALL)
    else:
        json_match = re.search(r"({.*})", raw_output, re.DOTALL)

    if not json_match:
        # If no outer braces found, try to capture the key-value pair
        json_match = re.search(r'("transports": \[.*\])', raw_output, re.DOTALL)

    if json_match:
        json_string = json_match.group(1)

        # Add outer braces if missing
        if not json_string.startswith("{"):
            json_string = "{" + json_string + "}"

        try:
            sanitized_json_data = json.loads(json_string)
        except json.JSONDecodeError:
            logger.exception("Error decoding JSON")
    return sanitized_json_data
