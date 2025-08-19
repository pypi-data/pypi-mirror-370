"""
Simulator service for managing conversation simulation between agents and the Galtea platform.

This service orchestrates the conversation loop, calling user agents, interacting with
the conversation simulator backend, and logging the results through the platform.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from galtea.application.services.conversation_simulator_service import ConversationSimulatorService
from galtea.application.services.inference_result_service import InferenceResultService
from galtea.application.services.session_service import SessionService
from galtea.infrastructure.clients.http_client import Client
from galtea.utils.agent import Agent, AgentInput, AgentResponse, ConversationMessage
from galtea.utils.from_camel_case_base_model import FromCamelCaseBaseModel


class SimulationResult(FromCamelCaseBaseModel):
    """
    Result of a conversation simulation.

    Attributes:
        session_id (str): The session identifier
        total_turns (int): Total number of conversation turns
        messages (List[ConversationMessage]): Complete conversation history
        finished (bool): Whether the simulation finished naturally
        stopping_reason (Optional[str]): Reason for stopping if finished
        metadata (Optional[Dict[str, Any]]): Additional simulation metadata
    """

    session_id: str
    total_turns: int
    messages: List[ConversationMessage]
    finished: bool
    stopping_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SimulatorService:
    """
    Service for managing conversation simulations between agents and the Galtea platform.

    This service orchestrates the conversation loop, manages the interaction between
    user-defined agents and the conversation simulator backend, and logs all results
    through the platform's tracking system.
    """

    def __init__(
        self,
        client: Client,
        session_service: SessionService,
        inference_result_service: InferenceResultService,
        conversation_simulator_service: ConversationSimulatorService,
    ):
        """Initialize the SimulatorService with required dependencies.

        Args:
            client (Client): The HTTP client for making API requests
            session_service (SessionService): Service for managing sessions
            inference_result_service (InferenceResultService): Service for logging inference results
            conversation_simulator_service (ConversationSimulatorService): Service for generating user messages
        """
        self._client: Client = client
        self._session_service: SessionService = session_service
        self._inference_result_service: InferenceResultService = inference_result_service
        self._conversation_simulator_service: ConversationSimulatorService = conversation_simulator_service
        self._logger: logging.Logger = logging.getLogger(__name__)

    def simulate(
        self,
        session_id: str,
        agent: Agent,
        max_turns: int = 20,
        log_inference_results: bool = True,
        enable_last_inference: bool = True,
        include_metadata: bool = False,
    ) -> SimulationResult:
        """
        Simulate a conversation between a user simulator and the provided agent.

        This method manages the entire conversation loop:
        1. Generates user messages using the conversation simulator
        2. Calls the provided agent to generate responses to each simulated user message
        3. Optionally logs each agent inference result to the Galtea platform for later analysis and benchmarking
        4. Continues until the maximum number of turns is reached or the conversation ends naturally

        Args:
            session_id (str): The session identifier for this conversation
            agent (Agent): The user-defined agent (typically an LLM wrapper) that generates responses to user messages.
            max_turns (int, optional): Maximum number of conversation turns (user + agent exchanges). Defaults to 20.
            log_inference_results (bool, optional): If True (default), logs each agent inference result to the Galtea
                platform for tracking, evaluation, and later comparison.
            enable_last_inference (bool, optional): If True (default), performs one final call to the agent with the
                simulated user's ending message, even if the conversation has finished. This allows capturing the
                agent's response to the user's closing statement, which can be useful for evaluating end-of-conversation
                behavior.
            include_metadata (bool, optional): If True, includes additional metadata in the returned results and
                conversation messages, such as turn numbers and simulation parameters. Defaults to False.

        Returns:
            SimulationResult: An object containing the complete simulation results, including the conversation history,
                total turns, completion status, and optional metadata.

        Raises:
            ValueError: If session_id is missing or agent is None.
            Exception: If the simulation fails due to API errors or agent errors.

        Example:
            ```python
            import galtea

            # Initialize the Galtea client
            client = galtea.Galtea(api_key="your_api_key")

            # Create a session
            session = client.sessions.create(version_id="version_123")

            # Define your agent
            class MyAgent(galtea.Agent):
                def call(self, input_data: galtea.AgentInput) -> galtea.AgentResponse:
                    user_msg = input_data.last_user_message_str()
                    return galtea.AgentResponse(content=f"Response to: {user_msg}")

            # Run simulation
            result = client.simulator.simulate(
                session_id=session.id,
                agent=MyAgent(),
                max_turns=5
            )

            print(f"Simulation completed with {result.total_turns} turns")
            ```
        """
        print("Starting conversation simulation...")
        if not session_id:
            raise ValueError("Session ID is required for simulation")

        if agent is None:
            raise ValueError("Agent is required for simulation")

        if max_turns <= 0:
            raise ValueError("max_turns must be greater than 0")

        self._logger.info(f"Starting conversation simulation for session {session_id}")

        messages: List[ConversationMessage] = []
        turn_count: int = 0
        finished: bool = False
        stopping_reason: Optional[str] = None
        simulation_metadata: Dict[str, Any] = {}

        try:
            # Start the conversation loop
            while turn_count < max_turns and not finished:
                self._logger.debug(f"Starting turn {turn_count + 1} of {max_turns}")

                # Generate user message from conversation simulator
                try:
                    user_response = self._conversation_simulator_service.generate_next_user_message(session_id)
                    user_message_content: str = user_response.next_message
                    finished = user_response.finished
                    stopping_reason = user_response.stopping_reason

                    if not user_message_content and not finished:
                        self._logger.warning("Empty user message received, ending simulation")
                        break

                    # Add user message to conversation history
                    if user_message_content:
                        user_message = ConversationMessage(
                            role="user",
                            content=user_message_content,
                            metadata={"turn": turn_count + 1, "source": "simulator"} if include_metadata else None,
                        )
                        messages.append(user_message)

                        # Call the user's agent
                        agent_response: Optional[AgentResponse] = None
                        timeBeforeCall: Optional[datetime] = None
                        timeAfterCall: Optional[datetime] = None
                        try:
                            if not finished or enable_last_inference:
                                agent_input = AgentInput(
                                    messages=messages,
                                    session_id=session_id,
                                    metadata={"turn": turn_count + 1} if include_metadata else None,
                                )

                                timeBeforeCall = datetime.now()
                                agent_response = agent.call(agent_input)
                                timeAfterCall = datetime.now()

                                if not agent_response.content:
                                    self._logger.warning("Agent returned empty response, ending simulation")
                                    break

                                # Add agent response to conversation history
                                assistant_message = ConversationMessage(
                                    role="assistant",
                                    content=agent_response.content,
                                    retrieval_context=agent_response.retrieval_context,
                                    metadata=agent_response.metadata if include_metadata else None,
                                )
                                messages.append(assistant_message)

                            # Log inference result if enabled
                            if log_inference_results:
                                try:
                                    self._inference_result_service.create(
                                        session_id=session_id,
                                        input=user_message_content,
                                        output=agent_response.content if agent_response else None,
                                        retrieval_context=agent_response.retrieval_context if agent_response else None,
                                        latency=(timeAfterCall - timeBeforeCall).total_seconds() * 1000
                                        if timeAfterCall and timeBeforeCall
                                        else None,
                                    )
                                    # If conversation is finished, store the stopping reason in the session
                                    if finished and stopping_reason:
                                        self._session_service._update_stopping_reason(
                                            session_id=session_id, stopping_reason=stopping_reason
                                        )
                                    self._logger.debug(f"Logged inference result for turn {turn_count + 1}")
                                except Exception as e:
                                    self._logger.error(f"Failed to log inference result: {e!s}")
                                    # Continue simulation even if logging fails

                        except Exception as e:
                            self._logger.error(f"Agent call failed on turn {turn_count + 1}: {e!s}")
                            stopping_reason = f"Agent error: {e!s}"
                            break

                except Exception as e:
                    self._logger.error(f"Failed to generate user message on turn {turn_count + 1}: {e!s}")
                    stopping_reason = f"Simulator error: {e!s}"
                    break

                turn_count += 1

            # Prepare simulation metadata
            if include_metadata:
                simulation_metadata = {
                    "max_turns": max_turns,
                    "completed_turns": turn_count,
                    "ended_naturally": finished,
                    "log_inference_results": log_inference_results,
                }

            self._logger.info(
                f"Simulation completed for session {session_id}: "
                f"{turn_count} turns, finished={finished}, reason={stopping_reason}"
            )

            return SimulationResult(
                session_id=session_id,
                total_turns=turn_count,
                messages=messages,
                finished=finished,
                stopping_reason=stopping_reason,
                metadata=simulation_metadata if include_metadata else None,
            )

        except Exception as e:
            self._logger.error(f"Simulation failed for session {session_id}: {e!s}")
            raise Exception(f"Simulation failed: {e!s}") from e
