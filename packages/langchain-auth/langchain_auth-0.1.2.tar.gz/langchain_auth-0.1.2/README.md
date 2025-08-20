# LangChain Auth

A Python SDK for OAuth authentication with LangChain Auth Server.

## Installation

```bash
pip install langchain-auth
```

## Usage

### Managing OAuth Providers

```python
from langchain_auth import Client

client = Client(api_key="your-api-key")

# List existing providers
providers = await client.list_oauth_providers()
print(f"Found {len(providers)} providers")

# Create a new GitHub provider
github_provider = await client.create_oauth_provider(
    provider_id="github",
    name="GitHub",
    client_id="your-github-client-id",
    client_secret="your-github-client-secret",
    auth_url="https://github.com/login/oauth/authorize",
    token_url="https://github.com/login/oauth/access_token",
)

await client.close()
```

### Authenticating a client from within LangGraph

When used within a LangGraph context, the client automatically handles OAuth interrupts:

```python
from langchain_auth import Client

client = Client(api_key="your-api-key")

# This will throw a LangGraph interrupt if OAuth is needed
auth_result = await client.authenticate(
    provider="google",
    scopes=["https://www.googleapis.com/auth/drive"],
    user_id=state["user_id"]
)
print(auth_result.token)

```

### Authenticating a client outside of LangGraph

```python
from langchain_auth import Client

client = Client(api_key="your-api-key")

# Authenticate with Google
auth_result = await client.authenticate(
    provider="google",
    scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    user_id="test_user"
)

if auth_result.needs_auth:
    print(f"Visit: {auth_result.auth_url}")
    # Wait for user to complete OAuth
    completed_result = await client.wait_for_completion(
        auth_id=auth_result.auth_id,
        timeout=300
    )
    print(f"Token: {completed_result.token}")
else:
    print(f"Token: {auth_result.token}")

await client.close()

```

## Features

- **OAuth 2.0 Flow**: Complete OAuth authentication flow with popular providers
- **LangGraph Integration**: Automatic OAuth interrupts in LangGraph workflows
- **Provider Management**: Create and manage OAuth provider configurations
- **Token Management**: Automatic token storage and retrieval
- **Multiple Scopes**: Support for requesting specific OAuth scopes
- **Agent-Scoped Tokens**: Support for both user-scoped and agent-scoped authentication
