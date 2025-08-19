from typing import List, Optional

from ...utils.from_camel_case_base_model import FromCamelCaseBaseModel


class MetricTypeBase(FromCamelCaseBaseModel):
    name: str
    evaluator_model_name: Optional[str] = None
    criteria: Optional[str] = None
    evaluation_steps: Optional[List[str]] = None
    evaluation_params: Optional[List[str]] = None
    judge_prompt: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    description: Optional[str] = None
    documentation_url: Optional[str] = None


class MetricType(MetricTypeBase):
    id: str
    organization_id: Optional[str] = None
    created_at: str
    deleted_at: Optional[str] = None
