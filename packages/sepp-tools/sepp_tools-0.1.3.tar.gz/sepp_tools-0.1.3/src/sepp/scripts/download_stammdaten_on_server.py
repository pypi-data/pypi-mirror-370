import json
import logging

import pandas as pd
import requests

from sepp.settings import BASE_DIR, soloplan_config

port = soloplan_config.port
hostname = soloplan_config.hostname
username = soloplan_config.username
password = soloplan_config.password

credentials = {"username": username, "password": password, "organizationNumber": 1}

logger = logging.getLogger(__name__)


def download_stammdaten() -> None:
    """Login and fetch master data from the Soloplan."""
    try:
        res = requests.post(f"{hostname}:{port}/login", data=credentials, timeout=10)
        token = res.json()["access_token"]

        headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}

        n = 40000
        url = f"http://192.168.0.204:4711/api/SoloplanOrderImport/v2/MasterDataBusinessPartner/0?%24top={n}"
        res = requests.get(url, headers=headers, timeout=10)

        df = pd.json_normalize(json.loads(res.content)["masterDataBusinessPartner"])
        df.columns = pd.Index([c.split(".")[-1] for c in df.columns])
        df.to_csv(f"{BASE_DIR}/StammdatenOppel_aktuell.csv", index=False)
    except Exception:
        logger.exception("Error while fetching master data from Soloplan.")


download_stammdaten()
