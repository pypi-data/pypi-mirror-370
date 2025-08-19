import os
from typing import Optional

from galtea.domain.exceptions.entity_not_found_exception import EntityNotFoundException

from ...application.services.product_service import ProductService
from ...domain.models.test import Test, TestBase
from ...infrastructure.clients.http_client import Client
from ...utils.s3 import download_file_from_s3, upload_file_to_s3
from ...utils.string import build_query_params, is_valid_id


class TestService:
    """
    Service for managing Tests.
    A Test is a collection of test cases designed to evaluate specific aspects or capabilities of your product versions.
    """

    def __init__(self, client: Client, product_service: ProductService):
        self._client = client
        self.product_service = product_service

    def __generate_and_upload_presigned_url(self, file_path: str, fileType: str):
        presigned_url_response = self._client.get(
            "storage/generate-put-presigned-url",
            {"key": os.path.basename(file_path), "fileType": fileType},
        )

        if "uploadPresignedUrl" in presigned_url_response.json():
            presigned_url = presigned_url_response.json().get("uploadPresignedUrl")
        else:
            raise Exception("Failed to generate presigned URL")

        if not upload_file_to_s3(file_path, presigned_url):
            raise Exception(f"Failed to upload file to {presigned_url}")

        return presigned_url_response.json().get("downloadPresignedUrl")

    def create(
        self,
        name: str,
        type: str,
        product_id: str,
        ground_truth_file_path: Optional[str] = None,
        test_file_path: Optional[str] = None,
        variants: Optional[list[str]] = None,
        strategies: Optional[list[str]] = None,
        custom_user_focus: Optional[str] = None,
        few_shot_examples: Optional[str] = None,
        language: Optional[str] = None,
        max_test_cases: Optional[int] = None,
    ):
        """
        Create a new test. A test is a collection of test cases.

        Args:
            name (str): Name of the test.
            type (str): Type of the test.
                Possible value is one of the following: `QUALITY`, `RED_TEAMING`, `SCENARIOS`.
            product_id (str): Product ID of the test.
            ground_truth_file_path (str, optional): Path to the ground truth file to be uploaded.
            test_file_path (str, optional): Path to the test file to be uploaded.
            variants (list[str], optional): Whether we should create variants in the synthetic data.
                Only makes sense for tests created by Galtea.
                Be cautious with this parameter, as it will create more test cases and be more expensive.
                Example: `["paraphrased", "typos", "incorrect", "cognitively_diverse", "linguistic_diverse"]`.\n
                To check the available variants, please refer to the documentation:
                https://docs.galtea.ai/concepts/product/test/red-teaming-threats.
            strategies (list[str], optional): Red teaming strategies to apply. A red teaming strategy
                is a specific technique applied to an initial prompt (derived from a selected threat)
                to modify or obfuscate it.
                It only makes sense for `RED_TEAMING` tests created by Galtea.\n
                The `original` strategy is required when creating red teaming tests.\n
                Example: `["original", "base64", "morse_code"]`.\n
                To check the available strategies, please refer to the documentation: https://docs.galtea.ai/concepts/product/test/red-teaming-strategies.\n
            custom_user_focus (str, optional): Specific User Focus for guiding the synthetic
                scenarios generator engine.\n
                It only makes sense for `SCENARIOS` tests created by Galtea.
            few_shot_examples (str, optional): Few-shot examples to be used in the test.
                This is only applicable for `QUALITY` tests created by Galtea.
                It helps to provide context and examples for the model to to guide on how to best create the test cases.
                If provided, it should be a list of strings, where each string is an example.\n
                Example:
                    Q: What is the capital of France?
                    A: The capital of France is Paris.
                    Q: What is the capital of Germany?
                    A: The capital of Germany is Berlin.
            language (str, optional): Language for generating the synthetic test cases.
                Defaults to the language used in the ground truth file.
                If provided, should be written in english and should be a valid language from the ISO 639 standard.
                For example: "english", "spanish", "french", etc.
                More information can be found here:
                    https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes.
            max_test_cases (int, optional): Maximum number of test cases to generate.
                It's only applicable for tests generated by Galtea.
                This helps controlling the size of the test dataset and the amount of credits spent.

        Returns:
            Test: The created test object.
        """
        ground_truth_url = (
            self.__generate_and_upload_presigned_url(ground_truth_file_path, "groundTruth")
            if ground_truth_file_path
            else None
        )
        test_presigned_url = (
            self.__generate_and_upload_presigned_url(test_file_path, "testFile") if test_file_path else None
        )

        test = TestBase(
            product_id=product_id,
            name=name,
            type=type,
            ground_truth_uri=ground_truth_url,
            uri=test_presigned_url,
            few_shot=few_shot_examples,
            custom_user_persona=custom_user_focus,
            language=language,
        )

        test.model_validate(test.model_dump())

        # Create a dictionary with all test fields including variants and strategies
        request_body = test.model_dump(by_alias=True)
        request_body["variants"] = variants
        request_body["strategies"] = strategies
        request_body["maxTestCases"] = max_test_cases

        response = self._client.post("tests", json=request_body)
        test_response = Test(**response.json())

        return test_response

    def get(self, test_id: str):
        """
        Retrieve a test by its ID.

        Args:
            test_id (str): ID of the test to retrieve.

        Returns:
            Test: The retrieved test object.
        """
        if not is_valid_id(test_id):
            raise ValueError("Test ID provided is not valid.")

        response = self._client.get(f"tests/{test_id}")
        return Test(**response.json())

    def get_by_name(self, product_id: str, test_name: str, type: Optional[str] = None):
        """
        Retrieve a test by its name and the product ID it is assiacted with.

        Args:
            product_id (str): ID of the product.
            test_name (str): Name of the test to retrieve.
            type (str, optional): Type of the test.
                This is needed when there is a test with the same name for both types.
                Possible value is one of the following:
                    `QUALITY`,
                    `RED_TEAMING`,
                    `SCENARIOS`,

        Returns:
            Test: The retrieved test object.
        """
        if not is_valid_id(product_id):
            raise ValueError("Product ID provided is not valid.")

        query_params = build_query_params(
            productIds=[product_id], names=[test_name], types=[type.upper()] if type else None
        )
        response = self._client.get(f"tests?{query_params}")
        tests = [Test(**test) for test in response.json()]

        if not tests:
            try:
                self.product_service.get(product_id)
            except Exception:
                raise EntityNotFoundException(f"Product with ID {product_id} does not exist.")

        if not tests:
            raise EntityNotFoundException(f"Test with name {test_name} does not exist.")

        if len(tests) > 1:
            raise ValueError(f"Multiple tests with name {test_name} exist, please specify the type parameter.")

        return tests[0]

    def download(self, test: Test, output_directory: str):
        """
        Download a test file from S3 using the presigned URL.

        Args:
            test (Test): Test object.
            output_directory (str): Directory where the file will be downloaded.

        Returns:
            str: Path to the downloaded file.
        """
        query_params = build_query_params(s3Uri=test.uri)
        response = self._client.get(f"storage/generate-get-presigned-url?{query_params}")
        if "downloadPresignedUrl" in response.json():
            download_url = response.json().get("downloadPresignedUrl")
        else:
            raise Exception("Failed to generate download URL")

        return download_file_from_s3(download_url, os.path.basename(test.uri), output_directory)

    def list(self, product_id: str, offset: Optional[int] = None, limit: Optional[int] = None):
        """
        List all tests for a given product.

        Args:
            product_id (str): ID of the product.
            offset (int, optional): Offset for pagination.
            limit (int, optional): Limit for pagination.

        Returns:
            list[Test]: List of test objects.
        """
        if not is_valid_id(product_id):
            raise ValueError("Product ID provided is not valid.")

        query_params = build_query_params(productIds=[product_id], offset=offset, limit=limit)
        response = self._client.get(f"tests?{query_params}")
        tests = [Test(**test) for test in response.json()]

        if not tests:
            try:
                self.product_service.get(product_id)
            except Exception:
                raise ValueError(f"Product with ID {product_id} does not exist.")

        return tests

    def delete(self, test_id: str):
        """
        Delete a test by its ID.

        Args:
            test_id (str): ID of the test to delete.

        Returns:
            Test: Deleted test object.
        """
        if not is_valid_id(test_id):
            raise ValueError("Test ID provided is not valid.")

        self._client.delete(f"tests/{test_id}")
