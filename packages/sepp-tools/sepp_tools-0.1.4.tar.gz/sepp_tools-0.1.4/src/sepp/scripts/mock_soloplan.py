import itertools
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock
from zoneinfo import ZoneInfo

from soloplan import SoloplanAPI
from soloplan.connectors.api import SoloplanResponse


def fake_soloplan_api() -> Mock:
    """Creates a mock SoloplanAPI instance for local testing of the pipeline.

    Returns
    -------
    Mock
        A mock SoloplanAPI instance.
    """
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
