import logging
import time

import googlemaps
import requests

logger = logging.getLogger(__name__)


def geocode_with_google(query: str, api: str) -> dict:
    """Uses Google Places API to resolve a company name into
    {'city': ..., 'country': ..., 'zip_code': ...} or {} if no match.
    """
    gmaps = googlemaps.Client(key=api)
    try:
        results = gmaps.places(query=query, language="en")
        if results.get("status") == "OK" and results.get("results"):
            top = results["results"][0]
            place_id = top["place_id"]

            details = gmaps.place(place_id=place_id, fields=["address_component"])

            city = None
            country = None
            zip_code = None
            for comp in details["result"]["address_components"]:
                types = comp["types"]
                if "locality" in types:
                    city = comp["long_name"]
                elif "country" in types:
                    country = comp["long_name"]
                elif "postal_code" in types:
                    zip_code = comp["long_name"]

            return {"city": city, "country": country, "zip": zip_code}
    except Exception:
        logger.exception("Error during Google geocoding")

    return {}


def geocode_with_nominatim(available_location_cues: list[str]) -> dict:
    """Uses Nominatim (OpenStreetMap) to resolve an address into
    {'city': ..., 'country': ..., 'zip_code': ...} or {} if no match.
    Must respect:
      • User-Agent in headers
      • ≤ 1 request per second.
    """
    # 1) Build the query string
    address_str = ", ".join(available_location_cues).strip()
    logger.info("Geocoding address: %s", address_str)
    if not address_str:
        logger.error("No address information provided.")
        return {}

    # 2) Endpoint and parameters
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address_str, "format": "jsonv2", "addressdetails": 1, "limit": 1}

    headers = {
        "User-Agent": "sepp-app/0.1.0 (shlychkov@kolibrain.de)",
        "Accept-Language": "en",  # optional but helps
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
    except requests.exceptions.RequestException:
        # network or timeout issue
        logger.exception("Network error")
        return {}

    error_403 = 403
    if resp.status_code == error_403:
        # Still getting 403 → either User-Agent is unacceptable or IP is blocked.
        logger.error("Nominatim returned 403. Check your User-Agent and rate limits.")
        return {}

    data = resp.json()
    if not data:
        return {}

    top = data[0].get("address", {})

    city = top.get("city") or top.get("town") or top.get("village") or ""
    country = top.get("country", "")
    zip_code = top.get("postcode", "")

    if not city or not country:
        return {}

    # 5) Sleep 1 second to respect rate limit
    time.sleep(1)

    return {"city": city, "country": country, "zip": zip_code}
