"""LangChain Auth SDK.

A Python client for OAuth authentication.
"""

from __future__ import annotations

from typing import List, Optional

import httpx

# Optional LangGraph imports
try:
    from langgraph.types import interrupt
    from langgraph.runtime import get_runtime
    from langgraph.config import get_config
except ImportError:
    # Create dummy functions that will fail if called
    def interrupt(data):
        raise ImportError("LangGraph is not installed. Install with: pip install 'langchain-auth[langgraph]'")
    def get_runtime():
        raise ImportError("LangGraph is not installed. Install with: pip install 'langchain-auth[langgraph]'")


def in_langgraph_context() -> bool:
    """Check if we're running inside a LangGraph context."""
    try:
        _runtime = get_runtime()
        return True
    except Exception as e:
        return False


class OAuthProvider:
    """OAuth provider configuration."""
    
    def __init__(
        self, 
        id: str = None,
        provider_id: str = None, 
        name: str = None,
        client_id: str = None,
        auth_url: str = None,
        token_url: str = None,
        is_active: bool = True,
        created_at: str = None,
        updated_at: str = None
    ):
        self.id = id
        self.provider_id = provider_id
        self.name = name
        self.client_id = client_id
        self.auth_url = auth_url
        self.token_url = token_url
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
    
    def __str__(self):
        return f"OAuthProvider(provider_id='{self.provider_id}', name='{self.name}')"
    
    def __repr__(self):
        return self.__str__()


class AuthResult:
    """Result from authentication attempt."""
    
    def __init__(self, token: str = None, auth_required: bool = False, auth_url: str = None, auth_id: str = None):
        self.token = token
        self.auth_required = auth_required  
        self.auth_url = auth_url
        self.auth_id = auth_id
        self.needs_auth = auth_required and not token
    
    def __str__(self):
        if self.token:
            return f"AuthResult(token='***', needs_auth=False)"
        elif self.needs_auth:
            return f"AuthResult(needs_auth=True, auth_url='{self.auth_url}')"
        else:
            return f"AuthResult(needs_auth=False)"
    
    def __repr__(self):
        return self.__str__()


class Client:
    """LangChain Auth client for OAuth."""
    
    API_PREFIX = "/v2/auth"

    def __init__(self, api_key: Optional[str] = None, api_url: str = "https://api.host.langchain.com"):
        self.api_url = api_url
        self.api_key = api_key or ""

    async def authenticate(
        self,
        provider: str,
        scopes: list[str],
        user_id: str,
        agent_scoped: Optional[bool] = None,
        agent_id: Optional[str] = None,
    ) -> AuthResult:
        """Authenticate with OAuth provider and return auth result.
        
        This method handles the full OAuth flow:
        - If in LangGraph context: throws interrupt for user to complete auth
        - If not in LangGraph context: returns AuthResult immediately with auth URL
        
        Args:
            provider: OAuth provider name
            scopes: List of required scopes  
            user_id: User ID for user-scoped tokens (required)
            agent_scoped: Whether to use agent-scoped tokens. If None, defaults to True in LangGraph context, False otherwise
            agent_id: Specific agent ID for agent-scoped tokens (optional, auto-detected in LangGraph if not provided)
            
        Returns:
            AuthResult with token (if available) or auth_url (if auth needed)
        """
        in_langgraph = in_langgraph_context()

        if agent_id:
            # If agent_id is provided, it's always agent-scoped
            if agent_scoped is False:
                raise ValueError("Cannot set agent_scoped=False when providing agent_id")
            agent_scoped = True
        elif agent_scoped is None:
            agent_scoped = in_langgraph  # Default: True in LangGraph, False outside
        
        if agent_scoped and not in_langgraph and not agent_id:
            raise ValueError("When agent_scoped=True outside LangGraph context, agent_id must be provided")
        
        # Determine the agent_id for the API call
        api_agent_id = None
        if agent_scoped:
            if agent_id:
                api_agent_id = agent_id
            elif in_langgraph:
                config = get_config()
                api_agent_id = config.get('configurable', {}).get('assistant_id')
                if not api_agent_id:
                    raise ValueError("Cannot determine agent_id for agent-scoped token")
            else:
                # This should be caught by validation above, but just in case
                raise ValueError("Cannot determine agent_id for agent-scoped token")
        
        # Check server for existing token (works for both first run and resume)
        async with httpx.AsyncClient(follow_redirects=True) as client:
            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key
            
            payload = {
                "user_id": user_id,
                "agent_id": api_agent_id,
                "provider": provider,
                "scopes": scopes,
            }
            
            response = await client.post(
                f"{self.api_url}{self.API_PREFIX}/authenticate",
                json=payload,
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            auth_response = response.json()
        
        # If token exists, return it (handles both first run and successful resume)
        if auth_response.get("status") == "completed":
            return AuthResult(token=auth_response["token"])
        
        # No token found - need OAuth
        auth_url = auth_response["url"]
        auth_id = auth_response["auth_id"]
        
        if in_langgraph:
            interrupt({
                "message": f"OAuth authentication required for provider '{provider}'.",
                "auth_url": auth_url,
                "provider": provider,
                "scopes": scopes,
            })
            
            # Only reached on resume - but if we get here, OAuth wasn't completed
            raise ValueError(f"OAuth authentication not completed. Please visit {auth_url} and complete authentication before resuming.")
        
        else:
            return AuthResult(
                auth_required=True,
                auth_url=auth_url,
                auth_id=auth_id
            )

    async def wait_for_completion(self, auth_id: str, timeout: int = 300) -> AuthResult:
        """Wait for OAuth authentication to be completed.
        
        Polls the server until the user completes OAuth flow or timeout is reached.
        Useful after authenticate() returns an auth_url.
        
        Args:
            auth_id: Auth ID returned from authenticate()
            timeout: Max time to wait for completion in seconds
            
        Returns:
            AuthResult with token if completed
            
        Raises:
            TimeoutError: If authentication not completed within timeout
            Exception: If authentication failed
        """
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout + 10) as client:
            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key
            
            response = await client.get(
                f"{self.api_url}{self.API_PREFIX}/wait/{auth_id}?timeout={timeout}",
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            completion_response = response.json()
        
        if completion_response.get("status") == "completed":
            return AuthResult(token=completion_response["token"])
        elif completion_response.get("status") == "timeout":
            raise TimeoutError(f"OAuth authentication timed out after {timeout} seconds")
        else:
            raise Exception(f"OAuth authentication failed: {completion_response}")

    async def create_oauth_provider(
        self,
        provider_id: str,
        name: str,
        client_id: str,
        client_secret: str,
        auth_url: str,
        token_url: str,
    ) -> OAuthProvider:
        """Create a new OAuth provider configuration.
        
        Args:
            provider_id: Unique identifier for the provider (e.g., 'github', 'google')
            name: Human-readable name for the provider
            client_id: OAuth client ID from the provider
            client_secret: OAuth client secret from the provider
            auth_url: Authorization URL for the OAuth flow
            token_url: Token exchange URL for the OAuth flow
            
        Returns:
            OAuthProvider instance with the created configuration
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key
            
            payload = {
                "provider_id": provider_id,
                "name": name,
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_url": auth_url,
                "token_url": token_url,
            }
            
            response = await client.post(
                f"{self.api_url}{self.API_PREFIX}/providers",
                json=payload,
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            provider_data = response.json()
        
        return OAuthProvider(
            id=provider_data["id"],
            provider_id=provider_data["provider_id"],
            name=provider_data["name"],
            client_id=provider_data["client_id"],
            auth_url=provider_data["auth_url"],
            token_url=provider_data["token_url"],
            is_active=provider_data.get("is_active", True),
            created_at=provider_data.get("created_at"),
            updated_at=provider_data.get("updated_at"),
        )

    async def list_oauth_providers(self) -> List[OAuthProvider]:
        """List all OAuth provider configurations.
        
        Returns:
            List of OAuthProvider instances
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key
            
            response = await client.get(
                f"{self.api_url}{self.API_PREFIX}/providers",
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            providers_data = response.json()
        
        return [
            OAuthProvider(
                id=provider["id"],
                provider_id=provider["provider_id"],
                name=provider["name"],
                client_id=provider["client_id"],
                auth_url=provider["auth_url"],
                token_url=provider["token_url"],
                is_active=provider.get("is_active", True),
                created_at=provider.get("created_at"),
                updated_at=provider.get("updated_at"),
            )
            for provider in providers_data
        ]

    async def close(self):
        pass
