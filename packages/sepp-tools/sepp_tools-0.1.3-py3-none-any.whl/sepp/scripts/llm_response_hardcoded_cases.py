import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


def apply_hardcoded_cases(llm_response: dict) -> None:
    logger.info("Looking for hardcoded exceptions for LLM response.")

    if "hermes" in llm_response.get("client", {}).get("name", "").lower():
        logger.info("Client is 'Hermes', exceptions might apply...")
        swap_sender_receiver_for_hermes(llm_response)
        return

    if "xxxlutz" in llm_response.get("client", {}).get("name", "").lower():
        logger.info("Client name is 'XXXLutz', exceptions might apply...")
        add_return_transport_for_xxxlutz(llm_response)
        return

    if "mondi" in llm_response.get("client", {}).get("name", "").lower():
        logger.info("Client name is 'Mondi', exceptions might apply...")
        add_delivery_date_for_mondi(llm_response)
        return

    logger.info("No hardcoded exceptions found.")
    return


def add_delivery_date_for_mondi(llm_response: dict) -> None:
    """Adds a delivery date for Mondi if it is not present."""
    logger.info("Attempting to add delivery date for Mondi.")
    transports: list[dict] = llm_response.get("transports", [])
    for transport in transports:
        loading_date = datetime.strptime(
            transport.get("loadingDate", [""])[0], "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=ZoneInfo("Europe/Berlin"))
        # set delivery date next day at 6 am
        delivery_date = loading_date + timedelta(days=1)
        delivery_date = delivery_date.replace(hour=6, minute=0, second=0)
        transport["deliveryDate"] = [delivery_date.strftime("%Y-%m-%d %H:%M:%S")]
        logger.info(
            "Added delivery date for Mondi transport: %s",
            transport["deliveryDate"][0],
        )


def swap_sender_receiver_for_hermes(llm_response: dict) -> None:
    transports = llm_response.get("transports", [])
    for transport in transports:
        sender = transport.get("sender", {})
        receiver = transport.get("receiver", {})

        sender_city = sender.get("city", "").lower()
        receiver_city = receiver.get("city", "").lower()

        if (
            "mülheim" in sender_city or "kaiserslautern" in sender_city
        ) and "ansbach" in receiver_city:
            # swap them
            transport["sender"], transport["receiver"] = (
                transport["receiver"],
                transport["sender"],
            )
            logger.info(
                "Swapped sender and receiver for Hermes transport (now: %s -> %s)",
                sender_city,
                receiver_city,
            )


def add_return_transport_for_xxxlutz(llm_response: dict) -> None:
    """Adds a return transport for XXXLutz if it is not present."""
    logger.info("Attempting to add return transports for XXXLutz.")
    try:
        transports: list[dict] = llm_response.get("transports", [])
        return_transports = []
        for transport in transports:
            loading_date = transport.get("loadingDate", [""])[0]
            loading_date = datetime.strptime(loading_date, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=ZoneInfo("Europe/Berlin")
            )

            delivery_date = transport.get("deliveryDate", [""])[0]
            delivery_date = datetime.strptime(
                delivery_date, "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=ZoneInfo("Europe/Berlin"))

            sender = transport.get("sender", {})
            receiver = transport.get("receiver", {})
            carrier = transport.get("carrier", {})
            return_transport = {
                "order_nr": None,
                "pallets": None,
                "pieces": None,
                "cartons": None,
                "customer_ref": None,
                "deliveryDate": [delivery_date.strftime("%Y-%m-%d %H:%M:%S")],
                "deliverRefNr": None,
                "loadingDate": [delivery_date.strftime("%Y-%m-%d %H:%M:%S")],
                "loadingRefNR": None,
                "sender": receiver,
                "receiver": sender,
                "carrier": carrier,
                "volume": None,
                "weight": 0.0,
                "goods": {
                    "number_of_rolls": None,
                    "gross_weight_kg": None,
                    "net_weight_kg": None,
                    "pallets": None,
                    "loading_space_meters": None,
                },
            }
            return_transports.append(return_transport)
        if return_transports:
            # insert return transport after each original transport
            new_transports = []
            for original_transport, return_transport in zip(
                transports, return_transports, strict=True
            ):
                new_transports.append(original_transport)
                new_transports.append(return_transport)
            llm_response["transports"] = new_transports
            logger.info("Added return transport for XXXLutz.")

        transports = llm_response.get("transports", [])
        for i, transport in enumerate(transports):  # fix loading dates
            if i > 0:
                transport["loadingDate"] = transports[i - 1].get("deliveryDate", [""])

    except Exception:
        logger.exception("Failed to add return transport for XXXLutz.")
