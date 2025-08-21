class UnauthorizedUser(Exception):
    """Exception raised when a user is unauthorized to perform an action."""


class NoAttachmentFoundError(Exception):
    """Exception raised when no attachment is found in the email."""


class NoBuchhaltungsNummerFoundError(Exception):
    """Exception raised when no Buchhaltungsnummer is found in the email."""


class NoPDForXLSXError(Exception):
    """Exception raised when no PD (Process Data) is found for an XLSX attachment."""


class LLMResponseIncompleteError(Exception):
    """Exception raised when sender or receiver information is incomplete in the llm response."""


class EmailFromBuchhaltung(Exception):
    """Exception raised when an email is from the Buchhaltung."""
