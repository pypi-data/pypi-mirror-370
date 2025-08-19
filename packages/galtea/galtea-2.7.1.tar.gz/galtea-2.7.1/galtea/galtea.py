from galtea.application.services.conversation_simulator_service import ConversationSimulatorService
from galtea.application.services.inference_result_service import InferenceResultService
from galtea.application.services.session_service import SessionService
from galtea.application.services.simulator_service import SimulatorService
from galtea.application.services.test_case_service import TestCaseService

from .application.services.evaluation_service import EvaluationService
from .application.services.evaluation_task_service import EvaluationTaskService
from .application.services.metric_type_service import MetricTypeService
from .application.services.product_service import ProductService
from .application.services.test_service import TestService
from .application.services.version_service import VersionService
from .infrastructure.clients.http_client import Client
from .utils.validate_installed_version import validate_installed_version


class Galtea:
    def __init__(self, api_key: str, supress_updatable_version_message: bool = False):
        """Initialize the Galtea SDK with the provided API key.
        Args:
            api_key (str): The API key to access the Galtea platform for authentication.
            supress_updatable_version_message (bool): If True, suppresses the message about a newer version available.
        """
        self.__client = Client(api_key)
        self.products = ProductService(self.__client)
        self.tests = TestService(self.__client, self.products)
        self.test_cases = TestCaseService(self.__client, self.tests)
        self.versions = VersionService(self.__client, self.products)
        self.metrics = MetricTypeService(self.__client)
        self.sessions = SessionService(self.__client)
        self.inference_results = InferenceResultService(self.__client, self.sessions)
        self.evaluations = EvaluationService(self.__client, self.products)
        self.evaluation_tasks = EvaluationTaskService(
            self.__client, self.evaluations, self.metrics, self.sessions, self.test_cases
        )
        self.conversation_simulator = ConversationSimulatorService(self.__client)
        self.simulator = SimulatorService(
            self.__client,
            self.sessions,
            self.inference_results,
            self.conversation_simulator,
        )

        # Validate that the installed version of the SDK is compatible with the API
        validate_installed_version(self.__client, supress_updatable_version_message)
