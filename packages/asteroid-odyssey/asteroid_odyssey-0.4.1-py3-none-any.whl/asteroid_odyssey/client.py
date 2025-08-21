"""
Asteroid Agents Python SDK - High-Level Client Interface

Provides a clean, easy-to-use interface for interacting with the Asteroid Agents API,
similar to the TypeScript SDK.

This module provides a high-level client that wraps the generated OpenAPI client
without modifying any generated files.
"""

import time
import os
import logging
import base64
from typing import Dict, Any, Optional, List, Union, Tuple
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from .agents_v1_gen import (
    Configuration as AgentsV1Configuration,
    ApiClient as AgentsV1ApiClient,
    APIApi as AgentsV1APIApi,
    ExecutionApi as AgentsV1ExecutionApi,
    AgentProfileApi as AgentsV1AgentProfileApi,
    ExecutionStatusResponse,
    ExecutionResult,
    UploadExecutionFiles200Response,
    Status,
    StructuredAgentExecutionRequest,
    CreateAgentProfileRequest,
    UpdateAgentProfileRequest,
    DeleteAgentProfile200Response,
    AgentProfile,
    Credential,
)
from .agents_v1_gen.exceptions import ApiException
from .agents_v2_gen import (
    Configuration as AgentsV2Configuration,
    ApiClient as AgentsV2ApiClient,
    ExecutionApi as AgentsV2ExecutionApi,
    ExecutionActivity,
    ExecutionUserMessagesAddTextBody,
)


class AsteroidAPIError(Exception):
    """Base exception for all Asteroid API related errors."""
    pass


class ExecutionError(AsteroidAPIError):
    """Raised when an execution fails or is cancelled."""
    def __init__(self, message: str, execution_result: Optional[ExecutionResult] = None):
        super().__init__(message)
        self.execution_result = execution_result


class TimeoutError(AsteroidAPIError):
    """Raised when an execution times out."""
    def __init__(self, message: str):
        super().__init__(message)


def encrypt_with_public_key(plaintext: str, pem_public_key: str) -> str:
    """
    Encrypt plaintext using RSA public key with PKCS1v15 padding.

    Args:
        plaintext: The string to encrypt
        pem_public_key: PEM-formatted RSA public key

    Returns:
        Base64-encoded encrypted string

    Raises:
        ValueError: If encryption fails or key is invalid

    Example:
        encrypted = encrypt_with_public_key("my_password", public_key_pem)
    """
    try:
        # Load the PEM public key (matches node-forge behavior)
        public_key = serialization.load_pem_public_key(pem_public_key.encode('utf-8'))

        if not isinstance(public_key, rsa.RSAPublicKey):
            raise ValueError("Invalid RSA public key")

        # Encrypt using PKCS1v15 padding (matches "RSAES-PKCS1-V1_5" from TypeScript)
        encrypted_bytes = public_key.encrypt(
            plaintext.encode('utf-8'),
            padding.PKCS1v15()
        )

        # Encode as base64 (matches forge.util.encode64)
        return base64.b64encode(encrypted_bytes).decode('utf-8')

    except Exception as e:
        raise ValueError(f"Failed to encrypt: {str(e)}") from e


class AsteroidClient:
    """
    High-level client for the Asteroid Agents API.

    This class provides a convenient interface for executing agents and managing
    their execution lifecycle, similar to the TypeScript SDK.
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Create an API client with the provided API key.

        Args:
            api_key: Your API key for authentication
            base_url: Optional base URL (defaults to https://odyssey.asteroid.ai/api/v1)

        Example:
            client = AsteroidClient('your-api-key')
        """
        if api_key is None:
            raise TypeError("API key cannot be None")

        # Configure the API client
        config = AgentsV1Configuration(
            host=base_url or "https://odyssey.asteroid.ai/api/v1",
            api_key={'ApiKeyAuth': api_key}
        )

        self.api_client = AgentsV1ApiClient(config)
        self.api_api = AgentsV1APIApi(self.api_client)
        self.execution_api = AgentsV1ExecutionApi(self.api_client)
        self.agent_profile_api = AgentsV1AgentProfileApi(self.api_client)

        self.agents_v2_config = AgentsV2Configuration(
            host=base_url or "https://odyssey.asteroid.ai/agents/v2",
            api_key={'ApiKeyAuth': api_key}
        )
        self.agents_v2_api_client = AgentsV2ApiClient(self.agents_v2_config)
        self.agents_v2_execution_api = AgentsV2ExecutionApi(self.agents_v2_api_client)

    # --- V1 ---

    def execute_agent(self, agent_id: str, execution_data: Dict[str, Any], agent_profile_id: Optional[str] = None) -> str:
        """
        Execute an agent with the provided parameters.

        Args:
            agent_id: The ID of the agent to execute
            execution_data: The execution parameters
            agent_profile_id: Optional ID of the agent profile

        Returns:
            The execution ID

        Raises:
            AsteroidAPIError: If the execution request fails

        Example:
            execution_id = client.execute_agent('my-agent-id', {'input': 'some dynamic value'}, 'agent-profile-id')
        """
        req = StructuredAgentExecutionRequest(dynamic_data=execution_data, agent_profile_id=agent_profile_id)
        try:
            response = self.execution_api.execute_agent_structured(agent_id, req)
            return response.execution_id
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to execute agent: {e}") from e

    def get_execution_status(self, execution_id: str) -> ExecutionStatusResponse:
        """
        Get the current status for an execution.

        Args:
            execution_id: The execution identifier

        Returns:
            The execution status details

        Raises:
            AsteroidAPIError: If the status request fails

        Example:
            status = client.get_execution_status(execution_id)
            print(status.status)
        """
        try:
            return self.execution_api.get_execution_status(execution_id)
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to get execution status: {e}") from e

    def get_execution_result(self, execution_id: str) -> ExecutionResult:
        """
        Get the final result of an execution.

        Args:
            execution_id: The execution identifier

        Returns:
            The execution result object

        Raises:
            AsteroidAPIError: If the result request fails or execution failed

        Example:
            result = client.get_execution_result(execution_id)
            print(result.outcome, result.reasoning)
        """
        try:
            response = self.execution_api.get_execution_result(execution_id)

            if response.error:
                raise AsteroidAPIError(response.error)

            # Handle case where execution_result might be None or have invalid data
            if response.execution_result is None:
                raise AsteroidAPIError("Execution result is not available yet")
            
            return response.execution_result
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to get execution result: {e}") from e
        except Exception as e:
            # Handle validation errors from ExecutionResult model
            if "must be one of enum values" in str(e):
                raise AsteroidAPIError("Execution result is not available yet - execution may still be running") from e
            raise e

    def wait_for_execution_result(
        self,
        execution_id: str,
        interval: float = 1.0,
        timeout: float = 3600.0
    ) -> ExecutionResult:
        """
        Wait for an execution to reach a terminal state and return the result.

        Continuously polls the execution status until it's either "completed",
        "cancelled", or "failed".

        Args:
            execution_id: The execution identifier
            interval: Polling interval in seconds (default is 1.0)
            timeout: Maximum wait time in seconds (default is 3600 - 1 hour)

        Returns:
            The execution result object

        Raises:
            ValueError: If interval or timeout parameters are invalid
            TimeoutError: If the execution times out
            ExecutionError: If the execution ends as "cancelled" or "failed"

        Example:
            result = client.wait_for_execution_result(execution_id, interval=2.0)
            print(result.outcome, result.reasoning)
        """
        # Validate input parameters
        if interval <= 0:
            raise ValueError("interval must be positive")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        start_time = time.time()

        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time >= timeout:
                raise TimeoutError(f"Execution {execution_id} timed out after {timeout}s")

            status_response = self.get_execution_status(execution_id)
            current_status = status_response.status

            if current_status == Status.COMPLETED:
                try:
                    return self.get_execution_result(execution_id)
                except Exception as e:
                    if "not available yet" in str(e):
                        # Execution completed but result not ready yet, wait a bit more
                        time.sleep(interval)
                        continue
                    raise e
            elif current_status in [Status.FAILED, Status.CANCELLED]:
                # Get the execution result to provide outcome and reasoning
                try:
                    execution_result = self.get_execution_result(execution_id)
                    reason = f" - {status_response.reason}" if status_response.reason else ""
                    raise ExecutionError(
                        f"Execution {execution_id} ended with status: {current_status.value}{reason}",
                        execution_result
                    )
                except Exception as e:
                    # If we can't get the execution result, fall back to the original behavior
                    reason = f" - {status_response.reason}" if status_response.reason else ""
                    raise ExecutionError(f"Execution {execution_id} ended with status: {current_status.value}{reason}") from e

            # Wait for the specified interval before polling again
            time.sleep(interval)

    def upload_execution_files(
        self,
        execution_id: str,
        files: List[Union[bytes, str, Tuple[str, bytes]]],
        default_filename: str = "file.txt"
    ) -> UploadExecutionFiles200Response:
        """
        Upload files to an execution.

        Args:
            execution_id: The execution identifier
            files: List of files to upload. Each file can be:
                   - bytes: Raw file content (will use default_filename)
                   - str: File path as string (will read file and use filename)
                   - Tuple[str, bytes]: (filename, file_content) tuple
            default_filename: Default filename to use when file is provided as bytes

        Returns:
            The upload response containing message and file IDs

        Raises:
            Exception: If the upload request fails

        Example:
            # Upload with file content (file should be in your current working directory)
            with open('hello.txt', 'r') as f:
                file_content = f.read()

            response = client.upload_execution_files(execution_id, [file_content.encode()])
            print(f"Uploaded files: {response.file_ids}")

            # Upload with filename and content
            files = [('hello.txt', file_content.encode())]
            response = client.upload_execution_files(execution_id, files)

            # Or create content directly
            hello_content = "Hello World!".encode()
            response = client.upload_execution_files(execution_id, [hello_content])
        """
        try:
            # Process files to ensure proper format
            processed_files = []
            for file_item in files:
                if isinstance(file_item, tuple):
                    # Already in (filename, content) format
                    filename, content = file_item
                    if isinstance(content, str):
                        content = content.encode()
                    processed_files.append((filename, content))
                elif isinstance(file_item, str):
                    # Check if string is a file path that exists, otherwise treat as content
                    if os.path.isfile(file_item):
                        # File path - read the file
                        filename = os.path.basename(file_item)
                        with open(file_item, 'rb') as f:
                            content = f.read()
                        processed_files.append((filename, content))
                    else:
                        # String content - encode and use default filename
                        content = file_item.encode()
                        processed_files.append((default_filename, content))
                elif isinstance(file_item, bytes):
                    # Raw bytes - use default filename
                    processed_files.append((default_filename, file_item))
                else:
                    # Other types - convert to string content and encode
                    content = str(file_item).encode()
                    processed_files.append((default_filename, content))

            response = self.execution_api.upload_execution_files(execution_id, files=processed_files)
            return response
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to upload execution files: {e}") from e

    def get_browser_session_recording(self, execution_id: str) -> str:
        """
        Get the browser session recording URL for a completed execution.

        Args:
            execution_id: The execution identifier

        Returns:
            The URL of the browser session recording

        Raises:
            Exception: If the recording request fails

        Example:
            recording_url = client.get_browser_session_recording(execution_id)
            print(f"Recording available at: {recording_url}")
        """
        try:
            response = self.execution_api.get_browser_session_recording(execution_id)
            return response.recording_url
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to get browser session recording: {e}") from e

    def get_agent_profiles(self, organization_id: str) -> List[AgentProfile]:
        """
        Get a list of agent profiles for a specific organization.

        Args:
            organization_id: The organization identifier (required)
        Returns:
            A list of agent profiles
        Raises:
            Exception: If the agent profiles request fails
        Example:
            profiles = client.get_agent_profiles("org-123")
        """
        try:
            response = self.agent_profile_api.get_agent_profiles(organization_id=organization_id)
            return response  # response is already a List[AgentProfile]
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to get agent profiles: {e}") from e
    def get_agent_profile(self, profile_id: str) -> AgentProfile:
        """
        Get an agent profile by ID.
        Args:
            profile_id: The ID of the agent profile
        Returns:
            The agent profile
        Raises:
            Exception: If the agent profile request fails
        Example:
            profile = client.get_agent_profile("profile_id")
        """
        try:
            response = self.agent_profile_api.get_agent_profile(profile_id)
            return response
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to get agent profile: {e}") from e

    def create_agent_profile(self, request: CreateAgentProfileRequest) -> AgentProfile:
        """
        Create an agent profile with automatic credential encryption.

        Args:
            request: The request object
        Returns:
            The agent profile
        Raises:
            Exception: If the agent profile creation fails
        Example:
            request = CreateAgentProfileRequest(
                name="My Agent Profile",
                description="This is my agent profile",
                organization_id="org-123",
                proxy_cc=CountryCode.US,
                proxy_type=ProxyType.RESIDENTIAL,
                captcha_solver_active=True,
                sticky_ip=True,
                credentials=[Credential(name="user", data="password")]
            )
            profile = client.create_agent_profile(request)
        """
        try:
            # Create a copy to avoid modifying the original request
            processed_request = request

            # If credentials are provided, encrypt them before sending
            if request.credentials and len(request.credentials) > 0:
                # Get the public key for encryption
                public_key = self.get_credentials_public_key()

                # Encrypt each credential's data field
                encrypted_credentials = []
                for credential in request.credentials:
                    encrypted_credential = Credential(
                        name=credential.name,
                        data=encrypt_with_public_key(credential.data, public_key),
                        id=credential.id,
                        created_at=credential.created_at
                    )
                    encrypted_credentials.append(encrypted_credential)

                # Create new request with encrypted credentials
                processed_request = CreateAgentProfileRequest(
                    name=request.name,
                    description=request.description,
                    organization_id=request.organization_id,
                    proxy_cc=request.proxy_cc,
                    proxy_type=request.proxy_type,
                    captcha_solver_active=request.captcha_solver_active,
                    sticky_ip=request.sticky_ip,
                    credentials=encrypted_credentials
                )

            response = self.agent_profile_api.create_agent_profile(processed_request)
            return response
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to create agent profile: {e}") from e
    def update_agent_profile(self, profile_id: str, request: UpdateAgentProfileRequest) -> AgentProfile:
        """
        Update an agent profile with automatic credential encryption.

        Args:
            profile_id: The ID of the agent profile
            request: The request object
        Returns:
            The agent profile
        Raises:
            Exception: If the agent profile update fails
        Example:
            request = UpdateAgentProfileRequest(
                name="My Agent Profile",
                description="This is my agent profile",
                credentials_to_add=[Credential(name="api_key", data="secret")]
            )
            profile = client.update_agent_profile("profile_id", request)
        """
        try:
            # Create a copy to avoid modifying the original request
            processed_request = request

            # If credentials_to_add are provided, encrypt them before sending
            if request.credentials_to_add and len(request.credentials_to_add) > 0:
                # Get the public key for encryption
                public_key = self.get_credentials_public_key()

                # Encrypt the data field of each credential to add
                encrypted_credentials_to_add = []
                for credential in request.credentials_to_add:
                    encrypted_credential = Credential(
                        name=credential.name,
                        data=encrypt_with_public_key(credential.data, public_key),
                        id=credential.id,
                        created_at=credential.created_at
                    )
                    encrypted_credentials_to_add.append(encrypted_credential)

                # Create new request with encrypted credentials
                processed_request = UpdateAgentProfileRequest(
                    name=request.name,
                    description=request.description,
                    proxy_cc=request.proxy_cc,
                    proxy_type=request.proxy_type,
                    captcha_solver_active=request.captcha_solver_active,
                    sticky_ip=request.sticky_ip,
                    credentials_to_add=encrypted_credentials_to_add,
                    credentials_to_delete=request.credentials_to_delete
                )

            response = self.agent_profile_api.update_agent_profile(profile_id, processed_request)
            return response
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to update agent profile: {e}") from e
    def delete_agent_profile(self, profile_id: str) -> DeleteAgentProfile200Response:
        """
        Delete an agent profile.
        Args:
            profile_id: The ID of the agent profile
        Returns:
            Confirmation message from the server
        Raises:
            Exception: If the agent profile deletion fails
        Example:
            response = client.delete_agent_profile("profile_id")
        """
        try:
            response = self.agent_profile_api.delete_agent_profile(profile_id)
            return response
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to delete agent profile: {e}") from e

    def get_credentials_public_key(self) -> str:
        """
        Get the public key for encrypting credentials.

        Returns:
            PEM-formatted RSA public key string

        Raises:
            Exception: If the public key request fails

        Example:
            public_key = client.get_credentials_public_key()
        """
        try:
            response = self.agent_profile_api.get_credentials_public_key()
            return response
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to get credentials public key: {e}") from e

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_value, tb):
        """Context manager exit: clean up API client connection pool."""
        try:
            # Try to grab the pool_manager; if any attr is missing, skip
            try:
                pool_manager = self.api_client.rest_client.pool_manager
            except AttributeError:
                pool_manager = None

            if pool_manager:
                pool_manager.clear()
        except Exception as e:
            # Log but don't mask the original exception (if any)
            logging.warning("Failed to clear connection pool: %s", e)

        # Returning False allows any exception in the 'with' block to propagate
        return False

    # Utility methods for nicer response formatting
    def format_agent_profile(self, profile: AgentProfile) -> str:
        """Format an agent profile for nice display."""
        credentials_info = f"{[(credential.name, credential.id) for credential in profile.credentials]}" if profile.credentials else "No credentials"
        return f"""Agent Profile:
  ID: {profile.id}
  Name: {profile.name}
  Description: {profile.description}
  Organization: {profile.organization_id}
  Proxy: {profile.proxy_cc.value} ({profile.proxy_type.value})
  Captcha Solver: {'Enabled' if profile.captcha_solver_active else 'Disabled'}
  Sticky IP: {'Yes' if profile.sticky_ip else 'No'}
  Credentials: {credentials_info}
  Created: {profile.created_at.strftime('%Y-%m-%d %H:%M:%S')}
  Updated: {profile.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"""

    def format_agent_profiles_list(self, profiles: List[AgentProfile]) -> str:
        """Format a list of agent profiles for nice display."""
        if not profiles:
            return "No agent profiles found."

        result = f"Found {len(profiles)} agent profile(s):\n"
        for i, profile in enumerate(profiles, 1):
            credentials_count = len(profile.credentials) if profile.credentials else 0
            result += f"  {i}. {profile.name} (ID: {profile.id[:8]}...) - {credentials_count} credentials\n"
        return result.rstrip()

    # --- V2 ---

    def get_last_n_execution_activities(self, execution_id: str, n: int) -> List[ExecutionActivity]:
        """
        Get the last N execution activities for a given execution ID, sorted by their timestamp in descending order.
        Args:
            execution_id: The execution identifier
            n: The number of activities to return
        Returns:
            A list of execution activities
        Raises:
            Exception: If the execution activities request fails
        """
        return self.agents_v2_execution_api.activities_get(execution_id, order="desc", limit=n)
    def add_message_to_execution(self, execution_id: str, message: str) -> None:
        """
        Add a message to an execution.
        Args:
            execution_id: The execution identifier
            message: The message to add
        Returns:
            None
        Raises:
            Exception: If the message addition fails
        Example:
            add_message_to_execution(client, "execution_id", "Hello, world!")
        """
        message_body = ExecutionUserMessagesAddTextBody(message=message)
        return self.agents_v2_execution_api.user_messages_add(execution_id, message_body)


# Convenience functions that mirror the TypeScript SDK pattern
def create_client(api_key: str, base_url: Optional[str] = None) -> AsteroidClient:
    """
    Create an API client with a provided API key.

    This is a convenience function that creates an AsteroidClient instance.

    Args:
        api_key: Your API key
        base_url: Optional base URL

    Returns:
        A configured AsteroidClient instance

    Example:
        client = create_client('your-api-key')
    """
    return AsteroidClient(api_key, base_url)

# --- V1 ---

def execute_agent(client: AsteroidClient, agent_id: str, execution_data: Dict[str, Any], agent_profile_id: Optional[str] = None) -> str:
    """
    Execute an agent with the provided parameters.

    Args:
        client: The AsteroidClient instance
        agent_id: The ID of the agent to execute
        execution_data: The execution parameters
        agent_profile_id: Optional ID of the agent profile

    Returns:
        The execution ID

    Example:
        execution_id = execute_agent(client, 'my-agent-id', {'input': 'some dynamic value'}, 'agent-profile-id')
    """
    return client.execute_agent(agent_id, execution_data, agent_profile_id)



def get_execution_status(client: AsteroidClient, execution_id: str) -> ExecutionStatusResponse:
    """
    Get the current status for an execution.

    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier

    Returns:
        The execution status details

    Example:
        status = get_execution_status(client, execution_id)
        print(status.status)
    """
    return client.get_execution_status(execution_id)


def get_execution_result(client: AsteroidClient, execution_id: str) -> ExecutionResult:
    """
    Get the final result of an execution.

    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier

    Returns:
        The execution result object

    Raises:
        Exception: If the result is not available yet or execution failed

    Example:
        result = get_execution_result(client, execution_id)
        print(result.outcome, result.reasoning)
    """
    return client.get_execution_result(execution_id)


def wait_for_execution_result(
    client: AsteroidClient,
    execution_id: str,
    interval: float = 1.0,
    timeout: float = 3600.0
) -> ExecutionResult:
    """
    Wait for an execution to reach a terminal state and return the result.

    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier
        interval: Polling interval in seconds (default is 1.0)
        timeout: Maximum wait time in seconds (default is 3600 - 1 hour)

    Returns:
        The execution result object

    Raises:
        TimeoutError: If the execution times out
        ExecutionError: If the execution ends as "cancelled" or "failed"

    Example:
        result = wait_for_execution_result(client, execution_id, interval=2.0)
        print(result.outcome, result.reasoning)
    """
    return client.wait_for_execution_result(execution_id, interval, timeout)


def upload_execution_files(
    client: AsteroidClient,
    execution_id: str,
    files: List[Union[bytes, str, Tuple[str, bytes]]],
    default_filename: str = "file.txt"
) -> UploadExecutionFiles200Response:
    """
    Upload files to an execution.

    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier
        files: List of files to upload
        default_filename: Default filename to use when file is provided as bytes

    Returns:
        The upload response containing message and file IDs

    Example:
        # Create a simple text file with "Hello World!" content
        hello_content = "Hello World!".encode()
        response = upload_execution_files(client, execution_id, [hello_content])
        print(f"Uploaded files: {response.file_ids}")

        # Or specify filename with content
        files = [('hello.txt', "Hello World!".encode())]
        response = upload_execution_files(client, execution_id, files)
    """
    return client.upload_execution_files(execution_id, files, default_filename)


def get_browser_session_recording(client: AsteroidClient, execution_id: str) -> str:
    """
    Get the browser session recording URL for a completed execution.

    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier

    Returns:
        The URL of the browser session recording

    Example:
        recording_url = get_browser_session_recording(client, execution_id)
        print(f"Recording available at: {recording_url}")
    """
    return client.get_browser_session_recording(execution_id)

def get_agent_profiles(client: AsteroidClient, organization_id: Optional[str] = None) -> List[AgentProfile]:
    """
    Get a list of agent profiles.
    Args:
        client: The AsteroidClient instance
        organization_id: The organization identifier (optional) Returns all agent profiles if no organization_id is provided.
    Returns:
        A list of agent profiles
    Raises:
        Exception: If the agent profiles request fails
    Example:
        profiles = get_agent_profiles(client, "org-123")
    """
    return client.get_agent_profiles(organization_id)
def get_agent_profile(client: AsteroidClient, profile_id: str) -> AgentProfile:
    """
    Get an agent profile by ID.
    Args:
        client: The AsteroidClient instance
        profile_id: The ID of the agent profile
    Returns:
        The agent profile
    Raises:
        Exception: If the agent profile request fails
    Example:
        profile = get_agent_profile(client, "profile_id")
    """
    return client.get_agent_profile(profile_id)
def create_agent_profile(client: AsteroidClient, request: CreateAgentProfileRequest) -> AgentProfile:
    """
    Create an agent profile.
    Args:
        client: The AsteroidClient instance
        request: The request object
    Returns:
        The agent profile
    Raises:
        Exception: If the agent profile creation fails
    Example:
        request = CreateAgentProfileRequest(
            name="My Agent Profile",
            description="This is my agent profile",
            organization_id="org-123",
            proxy_cc=CountryCode.US,
            proxy_type=ProxyType.RESIDENTIAL,
            captcha_solver_active=True,
            sticky_ip=True,
            credentials=[Credential(name="user", data="password")]
        )
        profile = create_agent_profile(client, request)
    """
    return client.create_agent_profile(request)
def update_agent_profile(client: AsteroidClient, profile_id: str, request: UpdateAgentProfileRequest) -> AgentProfile:
    """
    Update an agent profile with the provided request.
    Args:
        client: The AsteroidClient instance
        profile_id: The ID of the agent profile
        request: The request object
    Returns:
        The agent profile
    Raises:
        Exception: If the agent profile update fails
    Example:
        request = UpdateAgentProfileRequest(
            name="My Agent Profile",
            description="This is my agent profile",
            organization_id="org-123",
        )
        profile = update_agent_profile(client, "profile_id", request)
    """
    return client.update_agent_profile(profile_id, request)
def delete_agent_profile(client: AsteroidClient, profile_id: str) -> DeleteAgentProfile200Response:
    """
    Delete an agent profile.
    Args:
        client: The AsteroidClient instance
        profile_id: The ID of the agent profile
    Returns:
        The agent profile
    Raises:
        Exception: If the agent profile deletion fails
    Example:
        profile_deleted =delete_agent_profile(client, "profile_id")
    """
    return client.delete_agent_profile(profile_id)

def get_credentials_public_key(client: AsteroidClient) -> str:
    """
    Get the public key for encrypting credentials.

    Args:
        client: The AsteroidClient instance

    Returns:
        PEM-formatted RSA public key string

    Example:
        public_key = get_credentials_public_key(client)
    """
    return client.get_credentials_public_key()

# --- V2 ---

def get_last_n_execution_activities(client: AsteroidClient, execution_id: str, n: int) -> List[ExecutionActivity]:
    """
    Get the last N execution activities for a given execution ID, sorted by their timestamp in descending order.
    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier
        n: The number of activities to return
    Returns:
        A list of execution activities
    Raises:
        Exception: If the execution activities request fails
    Example:
        activities = get_last_n_execution_activities(client, "execution_id", 10)
    """
    return client.get_last_n_execution_activities(execution_id, n)

def add_message_to_execution(client: AsteroidClient, execution_id: str, message: str) -> None:
    """
    Add a message to an execution.
    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier
        message: The message to add
    Returns:
        None
    Raises:
        Exception: If the message addition fails
    Example:
        add_message_to_execution(client, "execution_id", "Hello, world!")
    """
    return client.add_message_to_execution(execution_id, message)

# Re-export common types for convenience
__all__ = [
    'AsteroidClient',
    'create_client',
    'execute_agent',
    'get_execution_status',
    'get_execution_result',
    'wait_for_execution_result',
    'upload_execution_files',
    'get_browser_session_recording',
    'get_agent_profiles',
    'get_agent_profile',
    'create_agent_profile',
    'update_agent_profile',
    'delete_agent_profile',
    'get_credentials_public_key',
    'AsteroidAPIError',
    'ExecutionError',
    'TimeoutError'
]
