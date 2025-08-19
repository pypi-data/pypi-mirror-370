from typing import Optional

from ...utils.from_camel_case_base_model import FromCamelCaseBaseModel


class CostInfoProperties(FromCamelCaseBaseModel):
    cost_per_input_token: Optional[float] = None
    cost_per_output_token: Optional[float] = None
    cost_per_cache_read_input_token: Optional[float] = None


class UsageInfoProperties(FromCamelCaseBaseModel):
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cache_read_input_tokens: Optional[int] = None


# Legacy evaluation-based models (maintained for backward compatibility)
class InferenceResultBase(CostInfoProperties, UsageInfoProperties):
    session_id: str
    actual_input: Optional[str] = None
    actual_output: Optional[str] = None
    retrieval_context: Optional[str] = None
    latency: Optional[float] = None


class InferenceResult(InferenceResultBase):
    id: str
    index: int
