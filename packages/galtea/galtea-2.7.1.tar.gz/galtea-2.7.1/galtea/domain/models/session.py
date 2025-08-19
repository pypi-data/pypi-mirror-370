from typing import Optional

from ...utils.from_camel_case_base_model import FromCamelCaseBaseModel


class SessionBase(FromCamelCaseBaseModel):
    """Base model for creating a new session."""

    custom_id: Optional[str] = (
        None  # client-provided ID to associate galtea session with the user's application session
    )
    version_id: Optional[str] = None
    test_case_id: Optional[str] = None
    context: Optional[str] = None  # flexible string context for user-defined information


class Session(SessionBase):
    """Complete session model returned from the API."""

    id: str
    created_at: str
    deleted_at: Optional[str] = None
    stopping_reason: Optional[str] = None
