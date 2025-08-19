from typing import Optional

from ...utils.from_camel_case_base_model import FromCamelCaseBaseModel


class Evaluation(FromCamelCaseBaseModel):
    id: str
    session_id: str
    created_at: str
    deleted_at: Optional[str] = None
