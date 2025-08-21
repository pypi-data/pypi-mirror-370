from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Email:
    """Class to represent an email."""

    message_id: str = ""
    subject: str = ""
    sender: str = ""
    sent_date: str = ""
    unique_id: str = ""
    content: str = ""
    has_attachment: bool = False
    info: str = ""
    retries: int = 0

    def __post_init__(self) -> None:
        self.info = f"email from {self.sender} with subject '{self.subject}' and unique id {self.unique_id} sent on {self.sent_date}"


@dataclass
class Results:
    """Class to represent the results of the email processing."""

    id: str = "N/A"
    email_subject: str = "N/A"
    sent_on: str = "N/A"
    sender: str = "N/A"
    attachment: bool = False
    llm_status: str = "N/A"
    client: str = "N/A"
    found_in: str = "N/A"
    order_id: str = "N/A"
    new_contacts: list = field(default_factory=list)
    transport_order_number: str = "N/A"
    order_already_exists: bool = False
    time_attachment_found: str = "N/A"
    time_of_llm_response: str = "N/A"
    time_soloplan_booked: str = "N/A"
    oppel_info_mail: str = "N/A"
    error_mail: str = "N/A"

    def update(self, updates: Mapping[str, Any]) -> None:
        """Update the results with new values."""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
