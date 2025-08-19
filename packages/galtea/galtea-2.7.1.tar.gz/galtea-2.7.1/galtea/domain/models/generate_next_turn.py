from typing import Optional

from ...utils.from_camel_case_base_model import FromCamelCaseBaseModel


class GenerateNextTurnRequest(FromCamelCaseBaseModel):
    session_id: str


class GenerateNextTurnResponse(FromCamelCaseBaseModel):
    next_message: str
    finished: bool
    stopping_reason: Optional[str] = None
