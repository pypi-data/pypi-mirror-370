from typing import Optional

from ...application.services.product_service import ProductService
from ...domain.models.evaluation import Evaluation
from ...infrastructure.clients.http_client import Client
from ...utils.string import build_query_params, is_valid_id


class EvaluationService:
    """
    Service for managing Evaluations.
    An Evaluation is a group of inference results from a session that can be evaluated.
    It acts as a container for all the evaluation tasks that measure how effectively the
    product version performs against the test cases.
    """

    def __init__(self, client: Client, product_service: ProductService):
        self._client = client
        self.product_service = product_service

    def get(self, evaluation_id: str):
        """
        Retrieve an evaluation by its ID.

        Args:
            evaluation_id (str): ID of the evaluation to retrieve.

        Returns:
            Evaluation: The retrieved evaluation object.
        """
        if not is_valid_id(evaluation_id):
            raise ValueError("Evaluation ID provided is not valid.")

        response = self._client.get(f"evaluations/{evaluation_id}")
        return Evaluation(**response.json())

    def list(self, product_id: str, offset: Optional[int] = None, limit: Optional[int] = None):
        """
        Get a list of evaluations for a given product.

        Args:
            product_id (str): ID of the product.
            offset (int, optional): Offset for pagination.
            limit (int, optional): Limit for pagination.

        Returns:
            List[Evaluation]: List of evaluations.
        """
        if not is_valid_id(product_id):
            raise ValueError("Product ID provided is not valid.")

        query_params = build_query_params(productIds=[product_id], offset=offset, limit=limit)
        response = self._client.get(f"evaluations?{query_params}")
        evaluations = [Evaluation(**evaluation) for evaluation in response.json()]

        if not evaluations:
            try:
                self.product_service.get(product_id)
            except Exception:
                raise ValueError(f"Product with ID {product_id} does not exist.")

        return evaluations

    def delete(self, evaluation_id: str):
        """
        Delete an evaluation by its ID.

        Args:
            evaluation_id (str): ID of the evaluation to delete.

        Returns:
            None: None.
        """
        if not is_valid_id(evaluation_id):
            raise ValueError("Evaluation ID provided is not valid.")

        self._client.delete(f"evaluations/{evaluation_id}")
