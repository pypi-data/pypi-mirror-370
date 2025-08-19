from typing import Optional

from ...utils.from_camel_case_base_model import FromCamelCaseBaseModel


class VersionBase(FromCamelCaseBaseModel):
    name: str
    product_id: str
    dataset_description: Optional[str] = None
    dataset_uri: Optional[str] = None
    description: Optional[str] = None
    endpoint: Optional[str] = None
    guardrails: Optional[str] = None
    system_prompt: Optional[str] = None
    model_id: Optional[str] = None


class Version(VersionBase):
    id: str
    created_at: str
    deleted_at: Optional[str] = None
