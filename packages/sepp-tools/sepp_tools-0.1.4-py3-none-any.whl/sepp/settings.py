import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


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


@dataclass
class SoloplanConfig:
    """Configuration for the Soloplan API."""

    hostname: str | None
    port: int | None
    username: str | None
    password: str | None
    organization: str | None


soloplan_config = SoloplanConfig(
    hostname=os.getenv("SOLOPLAN_HOSTNAME"),
    port=int(port) if (port := os.getenv("SOLOPLAN_PORT")) is not None else None,
    username=os.getenv("SOLOPLAN_USERNAME"),
    password=os.getenv("SOLOPLAN_PASSWORD"),
    organization=os.getenv("SOLOPLAN_ORGANISATION"),
)


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
    tenant_id=os.getenv("MS_TENANT_ID"),
    client_id=os.getenv("MS_CLIENT_ID"),
    client_secret=os.getenv("MS_CLIENT_SECRET"),
    scope=os.getenv("MS_SCOPE"),
    redirect_uri=os.getenv("MS_REDIRECT_URI"),
    refresh_token_url=os.getenv("MS_REFRESH_TOKEN_URL"),
)
