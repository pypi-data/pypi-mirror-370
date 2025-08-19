from typing import Optional

from ...application.services.test_service import TestService
from ...domain.models.test_case import TestCase, TestCaseBase
from ...infrastructure.clients.http_client import Client
from ...utils.string import build_query_params, is_valid_id


class TestCaseService:
    def __init__(self, client: Client, test_service: TestService):
        self._client = client
        self.test_service = test_service

    def create(
        self,
        test_id: str,
        input: Optional[str] = None,
        expected_output: Optional[str] = None,
        context: Optional[str] = None,
        variant: Optional[str] = None,
        user_persona: Optional[str] = None,
        scenario: Optional[str] = None,
        goal: Optional[str] = None,
        stopping_criterias: Optional[list[str]] = None,
        initial_prompt: Optional[str] = None,
        reviewed_by_id: Optional[str] = None,
    ) -> TestCase:
        """
        Create a new test case.

        Args:
            test_id (str): ID of the test.
            input (str): Input for the test case.
            expected_output (Optional[str], optional): Expected output for the test case.
            context (Optional[str], optional): Context for the test case.
            variant (Optional[str], optional): Variant for the test case.
            user_persona (Optional[str], optional): User persona for the test case.
            scenario (Optional[str], optional): Scenario for the test case.
            goal (Optional[str], optional): Goal for the test case.
            stopping_criterias (Optional[list[str]], optional): Stopping criteria for the test case.
            initial_prompt (Optional[str], optional): Initial prompt for the test case.
            reviewed_by_id (Optional[str], optional): ID of the user who reviewed the test case.

        Returns:
            TestCase: The created test case object.
        """

        test_case: TestCaseBase = TestCaseBase(
            test_id=test_id,
            input=input,
            expected_output=expected_output,
            context=context,
            variant=variant,
            user_persona=user_persona,
            scenario=scenario,
            goal=goal,
            stopping_criterias=stopping_criterias,
            initial_prompt=initial_prompt,
            reviewed_by_id=reviewed_by_id,
        )
        test_case.model_validate(test_case.model_dump())
        response = self._client.post("testCases", json=test_case.model_dump(by_alias=True))
        test_case_response: TestCase = TestCase(**response.json())
        return test_case_response

    def list(self, test_id: str, offset: Optional[int] = None, limit: Optional[int] = None):
        """
        Retrieve test cases for a given test ID.

        Args:
            test_id (str): ID of the test.

        Returns:
            list[TestCase]: List of test case objects.
        """
        if not is_valid_id(test_id):
            raise ValueError("Test ID provided is not valid.")

        query_params = build_query_params(testIds=[test_id], offset=offset, limit=limit)
        response = self._client.get(f"testCases?{query_params}")
        test_cases = [TestCase(**test_case) for test_case in response.json()]

        if not test_cases:
            try:
                self.test_service.get(test_id)
            except Exception:
                raise ValueError(f"Test with ID {test_id} does not exist.")

        return test_cases

    def get(self, test_case_id: str):
        """
        Retrieve a test case by its ID.

        Args:
            test_case_id (str): ID of the test case.

        Returns:
            TestCase: The retrieved test case object.
        """
        if not is_valid_id(test_case_id):
            raise ValueError("Test case ID provided is not valid.")

        response = self._client.get(f"testCases/{test_case_id}")
        test_case_response = TestCase(**response.json())
        return test_case_response

    def delete(self, test_case_id: str):
        """
        Delete a test case by its ID.

        Args:
            test_case_id (str): ID of the test case to be deleted.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if not is_valid_id(test_case_id):
            raise ValueError("Test case ID provided is not valid.")

        self._client.delete(f"testCases/{test_case_id}")
