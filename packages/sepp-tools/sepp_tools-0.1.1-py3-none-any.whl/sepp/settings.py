# %%
import itertools
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from soloplan import SoloplanAPI
from soloplan.connectors.api import SoloplanResponse


def find_base_dir(marker: str) -> Path:
    """Find the base directory of the project."""
    current_path = Path(__file__).resolve()
    while not (current_path / marker).exists():
        current_path = current_path.parent
        if current_path == current_path.parent:
            msg = f"Could not find the marker '{marker}' in the directory tree."
            raise FileNotFoundError(msg)
    return current_path


BASE_DIR = find_base_dir("pyproject.toml")

load_dotenv(BASE_DIR / ".env")

soloplan_hostname = os.getenv("SOLOPLAN_HOSTNAME")
soloplan_port = os.getenv("SOLOPLAN_PORT")
soloplan_username = os.getenv("SOLOPLAN_USERNAME")
soloplan_password = os.getenv("SOLOPLAN_PASSWORD")
soloplan_organization = os.getenv("SOLOPLAN_ORGANISATION")


@dataclass
class SoloplanConfig:
    """Configuration for the Soloplan API."""

    hostname: str | None
    port: int | None
    username: str | None
    password: str | None
    organization: str | None


soloplan_config = SoloplanConfig(
    hostname=soloplan_hostname,
    port=int(soloplan_port) if soloplan_port else None,
    username=soloplan_username,
    password=soloplan_password,
    organization=soloplan_organization,
)

MS_REDIRECT_URI = os.getenv("MS_REDIRECT_URI")
MS_TENANT_ID = os.getenv("MS_TENANT_ID")
MS_CLIENT_ID = os.getenv("MS_CLIENT_ID")
MS_CLIENT_SECRET = os.getenv("MS_CLIENT_SECRET")
MS_SCOPE = os.getenv("MS_SCOPE")
MS_REFRESH_TOKEN_URL = os.getenv("MS_REFRESH_TOKEN_URL")

INBOX_ID = os.getenv("INBOX_ID")
ERLEDIGT_ID = os.getenv("ERLEDIGT_ID")
FAILED_ID = os.getenv("FAILED_ID")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""
OPENAI_PROJECT_KEY = os.getenv("OPENAI_PROJECT_KEY") or ""

ERROR_HANDLING_RECIPIENTS = ["guemues@kolibrain.de", "al-khazrage@kolibrain.de"]


@dataclass
class MSGraphConfig:
    """Configuration for the Microsoft Graph API."""

    tenant_id: str | None
    client_id: str | None
    client_secret: str | None
    scope: str | None
    redirect_uri: str | None
    refresh_token_url: str | None


ms_graph_config = MSGraphConfig(
    tenant_id=MS_TENANT_ID,
    client_id=MS_CLIENT_ID,
    client_secret=MS_CLIENT_SECRET,
    scope=MS_SCOPE,
    redirect_uri=MS_REDIRECT_URI,
    refresh_token_url=MS_REFRESH_TOKEN_URL,
)


def fake_soloplan_s_n_c() -> Mock:
    with Path("src/sepp/tests/test_data/soloplan_response_value.json").open(
        "r", encoding="utf-8"
    ) as f:
        fake_soloplan_response_value = json.load(f)
    with Path("src/sepp/tests/test_data/soloplan_order.json").open(
        "r", encoding="utf-8"
    ) as f:
        fake_order = json.load(f)

    fake_soloplan_response = SoloplanResponse(
        success=True,
        value=fake_soloplan_response_value,
        info="Mocked Soloplan Response",
    )
    fake_business_contacts_new: list[str] = []
    fake_found_in = "CSV"

    fake = Mock(spec=SoloplanAPI)
    fake.create_order.side_effect = itertools.cycle(
        [
            ValueError("both search and creation failed"),
            (
                fake_soloplan_response,
                fake_order,
                fake_business_contacts_new,
                fake_found_in,
            ),
        ]
    )
    fake.token_expiration = datetime.now(tz=ZoneInfo("Europe/Berlin")) + timedelta(
        days=1
    )
    fake.token = "mocked_token"  # noqa: S105 Not a password
    fake._get_jwt_token = Mock(return_value=fake.token)

    return fake
