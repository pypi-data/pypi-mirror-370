from typing import Optional

from ...utils.from_camel_case_base_model import FromCamelCaseBaseModel


class TestBase(FromCamelCaseBaseModel):
    product_id: Optional[str] = None
    name: str
    type: str
    language: Optional[str] = None
    ground_truth_uri: Optional[str] = None
    few_shot: Optional[str] = None
    custom_user_persona: Optional[str] = None
    uri: Optional[str] = None


class Test(TestBase):
    id: str
    created_at: str
    deleted_at: Optional[str] = None
