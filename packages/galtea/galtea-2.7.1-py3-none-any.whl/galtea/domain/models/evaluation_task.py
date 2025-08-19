from typing import Optional

from ...utils.from_camel_case_base_model import FromCamelCaseBaseModel


class EvaluationTask(FromCamelCaseBaseModel):
    id: str
    metric_type_id: str
    evaluation_id: Optional[str] = None
    score: Optional[float] = None
    status: str
    created_at: str
    deleted_at: Optional[str] = None
    evaluated_at: Optional[str] = None
