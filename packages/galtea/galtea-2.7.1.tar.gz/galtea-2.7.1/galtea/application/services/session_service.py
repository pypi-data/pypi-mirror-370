from typing import List, Optional

from galtea.utils.string import build_query_params, is_valid_id

from ...domain.models.session import Session, SessionBase
from ...infrastructure.clients.http_client import Client


class SessionService:
    """
    Service for managing Sessions.
    A Session is a group of inference results that make a full conversation between a user and an AI system.
    """

    def __init__(self, client: Client):
        """Initialize the SessionService with the provided HTTP client.

        Args:
            client (Client): The HTTP client for making API requests.
        """
        self._client: Client = client

    def create(
        self,
        version_id: str,
        custom_id: Optional[str] = None,
        test_case_id: Optional[str] = None,
        context: Optional[str] = None,
        is_production: Optional[bool] = None,
    ) -> Session:
        """Create a new session.

        Args:
            version_id (str): The version ID to associate with this session
            custom_id (str, optional): Client-provided session ID to associate with this session.
            test_case_id (str, optional): The test case ID (implies a test_id)
            context (str, optional): Flexible string context for user-defined information
            is_production (bool, optional): Whether this is a PRODUCTION session or not.
                A PRODUCTION session is the one we create for tracking real-time user interactions.
                Defaults to False.

        Returns:
            Session: The created session object

        Raises:
            ValueError: If is_production is False and test_case_id is None
        """
        if not is_valid_id(version_id):
            raise ValueError("A valid version_id is required to create a session")

        # Construct SessionBase payload
        session_base: SessionBase = SessionBase(
            custom_id=custom_id,
            version_id=version_id,
            test_case_id=test_case_id,
            context=context,
        )

        # Validate the payload

        request_body = session_base.model_dump(by_alias=True, exclude_none=True)
        session_base.model_validate(request_body)

        # Add isProduction to the request body since it's not part of Session entity
        request_body["isProduction"] = is_production

        # Send the request
        response = self._client.post("sessions", json=request_body)

        return Session(**response.json())

    def get(self, session_id: str) -> Session:
        """Get a session by ID.

        Args:
            session_id (str): The session ID to retrieve

        Returns:
            Session: The session object
        """
        response = self._client.get(f"sessions/{session_id}")
        return Session(**response.json())

    def get_by_custom_id(self, version_id: str, custom_id: str) -> Session:
        """Get a session by custom ID and version ID.

        Args:
            version_id (str): The version ID to filter by
            custom_id (str): The client-provided session ID to retrieve

        Returns:
            Session: The session object

        Raises:
            ValueError: If the custom_id or version_id is not valid
        """
        if not is_valid_id(version_id):
            raise ValueError("A valid version ID must be provided.")

        query_params = build_query_params(customIds=[custom_id], versionIds=[version_id])
        response = self._client.get(f"sessions?{query_params}")
        sessions = [Session(**session) for session in response.json()]

        if not sessions:
            raise ValueError(f"Session with custom ID {custom_id} and version ID {version_id} does not exist.")

        return sessions[0]

    def get_or_create(
        self,
        custom_id: str,
        version_id: str,
        test_case_id: Optional[str] = None,
        context: Optional[str] = None,
        is_production: Optional[bool] = False,
    ) -> Session:
        """Get an existing session or create a new one if it doesn't exist.

        Args:
            custom_id (str): Client-provided session ID to fetch or create from.
            version_id (str): The version ID to associate with this session
            test_case_id (Optional[str]): The test case ID (implies a test_id)
            context (Optional[str]): Flexible string context for user-defined information
            is_production (bool, optional): Whether this is a production session. Defaults to False.

        Returns:
            Session: The existing or newly created session object
        """
        if not is_valid_id(custom_id):
            raise ValueError("A valid session ID must be provided.")
        if not is_valid_id(version_id):
            raise ValueError("A valid version ID must be provided.")

        try:
            return self.get_by_custom_id(custom_id=custom_id, version_id=version_id)
        except Exception:
            return self.create(
                custom_id=custom_id,
                version_id=version_id,
                test_case_id=test_case_id,
                context=context,
                is_production=is_production,
            )

    def list(
        self,
        version_id: Optional[str] = None,
        test_case_id: Optional[str] = None,
        custom_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Session]:
        """List sessions with optional filtering.

        Args:
            version_id (str, optional): Filter by version ID
            test_case_id (str, optional): Filter by test case ID
            custom_id (str, optional): Filter by custom ID (client-provided session ID)
            offset (Optional[int]): Number of results to skip
            limit (Optional[int]): Maximum number of results to return

        Returns:
            List[Session]: List of session objects
        """
        if not (version_id or test_case_id or custom_id):
            raise ValueError("At least one of version_id, test_case_id, or custom_id must be provided.")
        if version_id and not is_valid_id(version_id):
            raise ValueError("A valid version ID must be provided.")
        if test_case_id and not is_valid_id(test_case_id):
            raise ValueError("A valid test case ID must be provided.")

        query_params = build_query_params(
            versionIds=[version_id] if version_id else None,
            testCaseIds=[test_case_id] if test_case_id else None,
            customIds=[custom_id] if custom_id else None,
            offset=offset,
            limit=limit,
        )
        response = self._client.get(f"sessions?{query_params}")
        return [Session(**session) for session in response.json()]

    def _update_stopping_reason(self, session_id: str, stopping_reason: str) -> Session:
        """Update the stopping reason for a session.

        Args:
            session_id (str): The session ID to update
            stopping_reason (str): The stopping reason for which the session was stopped

        Returns:
            Session: The updated session object

        Raises:
            ValueError: If the session ID is not valid
        """
        if not is_valid_id(session_id):
            raise ValueError("A valid session ID must be provided.")

        response = self._client.patch(f"sessions/{session_id}", json={"stoppingReason": stopping_reason})
        return Session(**response.json())

    def delete(self, session_id: str) -> None:
        """Delete a session by ID.

        Args:
            session_id (str): The session ID to delete

        Raises:
            ValueError: If the session ID is not valid
        """
        if not is_valid_id(session_id):
            raise ValueError("A valid session ID must be provided.")

        self._client.delete(f"sessions/{session_id}")
