from galtea.domain.models.generate_next_turn import GenerateNextTurnRequest, GenerateNextTurnResponse
from galtea.infrastructure.clients.http_client import Client
from galtea.utils.string import is_valid_id


class ConversationSimulatorService:
    """
    Service for managing Conversations.
    A Conversation is a group of messages exchanged between a user and the system.
    It acts as a container for all the conversation tasks that measure how effectively the
    product version performs against the user queries.
    """

    def __init__(self, client: Client):
        self._client = client

    def generate_next_user_message(self, session_id: str) -> GenerateNextTurnResponse:
        """
        Simulate a user message for the current conversation and user scenario.

        Args:
            session_id (str): The ID of the session for which the user message is being generated.

        Returns:
            dict: The generated user message payload.
        """
        if not is_valid_id(session_id):
            raise ValueError("Session ID provided is not valid.")

        request = GenerateNextTurnRequest(session_id=session_id)
        response = self._client.post(
            "conversationSimulator/generateNextUserMessage", json=request.model_dump(by_alias=True)
        )
        response = GenerateNextTurnResponse(**response.json())
        return response
