"""
Agent adapter module for integrating custom agents with the Galtea conversation simulation framework.

This module provides the abstract base class that users must implement to integrate
their existing agents with the Galtea conversation simulation framework. The adapter pattern allows
any agent implementation to work with the framework regardless of its underlying
architecture or API.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .from_camel_case_base_model import FromCamelCaseBaseModel


class ConversationMessage(FromCamelCaseBaseModel):
    """
    Represents a single message in a conversation.

    Attributes:
        role (str): The role of the message sender (e.g., "user", "assistant")
        content (str): The message content
        metadata (Optional[Dict[str, Any]]): Additional metadata for the message
    """

    role: str
    content: str
    retrieval_context: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentInput(FromCamelCaseBaseModel):
    """
    Input data provided to the agent for processing.

    Attributes:
        messages (List[ConversationMessage]): The conversation history
        session_id (str): The current session identifier
        context (Optional[str]): Additional context information
        metadata (Optional[Dict[str, Any]]): Additional metadata
    """

    messages: List[ConversationMessage]
    session_id: str
    context: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def last_user_message(self) -> Optional[ConversationMessage]:
        """
        Get the last user message from the conversation.

        Returns:
            Optional[ConversationMessage]: The last user message or None if no user message exists
        """
        for message in reversed(self.messages):
            if message.role == "user":
                return message
        return None

    def last_user_message_str(self) -> Optional[str]:
        """
        Get the content of the last user message.

        Returns:
            Optional[str]: The content of the last user message or None if no user message exists
        """
        last_message: Optional[ConversationMessage] = self.last_user_message()
        return last_message.content if last_message else None


class AgentResponse(FromCamelCaseBaseModel):
    """
    Response from the agent after processing input.

    Attributes:
        content (str): The response content
        metadata (Optional[Dict[str, Any]]): Additional metadata for the response
    """

    content: str
    retrieval_context: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Agent(ABC):
    """
    Abstract base class for integrating custom agents with the Galtea conversation simulation framework.

    This adapter pattern allows you to wrap any existing agent implementation
    (LLM calls, agent frameworks, or complex multi-step systems) to work with
    the Galtea conversation simulation framework. The adapter receives structured input about
    the conversation state and returns responses in a standardized format.

    Example:
        ```python
        import galtea
        from my_agent import MyCustomAgent

        class MyAgentAdapter(galtea.Agent):
            def __init__(self):
                self.agent = MyCustomAgent()

            def call(self, input_data: galtea.AgentInput) -> galtea.AgentResponse:
                # Get the latest user message
                user_message = input_data.last_user_message_str()

                # Call your existing agent
                response = self.agent.process(
                    message=user_message,
                    history=input_data.messages,
                    session_id=input_data.session_id
                )

                # Return the response
                return galtea.AgentResponse(content=response)

        # Use in a simulation
        client = galtea.Galtea(api_key="your_api_key")
        my_agent = MyAgentAdapter()

        result = client.simulator.simulate(
            session_id="session_123",
            agent=my_agent,
            max_turns=10
        )
        ```

    Note:
        - The call method must return an AgentResponse object
        - For stateful agents, use input_data.session_id to maintain conversation context
        - For stateless agents, use input_data.messages for the full conversation history
    """

    @abstractmethod
    def call(self, input_data: AgentInput) -> AgentResponse:
        """
        Process the input and generate a response.

        This is the main method that your agent implementation must provide.
        It receives structured information about the current conversation state
        and must return a response in the standardized format.

        Args:
            input_data (AgentInput): Input containing conversation history, session context, and metadata

        Returns:
            AgentResponse: The agent's response containing the content and optional metadata

        Example:
            ```python
            def call(self, input_data: AgentInput) -> AgentResponse:
                # Simple string response
                user_msg = input_data.last_user_message_str()
                response_content = f"I understand you said: {user_msg}"

                return AgentResponse(
                    content=response_content,
                    metadata={"processing_time": 0.1}
                )
            ```
        """
        pass
