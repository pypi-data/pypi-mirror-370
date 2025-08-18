# Asgardeo AI SDK

> ⚠️ WARNING: Asgardeo AI SDK is currently under development, is not intended for production use, and therefore has no official support.

Python SDK for Asgardeo AI agent authentication and on-behalf-of (OBO) token flows.



## Features
- **Agent Authentication**: Authenticate AI agents using agent credentials
- **On-Behalf-Of (OBO) Tokens**: Get user tokens on behalf of authenticated agents
- **Async/Await Support**: Full async implementation using httpx
- **Token Management**: Handle token exchange, refresh, and revocation
- **Authorization URLs**: Generate authorization URLs for user authentication flows

## Installation

Install from local development:

```bash
pip install -e .
```

## Quick Start

### Basic Setup

```python
import asyncio
from asgardeo import AsgardeoConfig
from asgardeo_ai import AgentAuthManager, AgentConfig

# Configure Asgardeo connection
config = AsgardeoConfig(
    base_url="https://api.asgardeo.io/t/your-organization",
    client_id="your_client_id", 
    redirect_uri="https://your-app.com/callback",
    client_secret="your_client_secret"
)

# Configure AI agent
agent_config = AgentConfig(
    agent_id="your_agent_id",
    agent_secret="your_agent_secret"
)

# Create auth manager
auth_manager = AgentAuthManager(config, agent_config)
```

### Agent Authentication

```python
async def main():
    async with AgentAuthManager(config, agent_config) as auth_manager:
        # Get token for the AI agent
        agent_token = await auth_manager.get_agent_token(["openid", "profile"])
        print(f"Agent access token: {agent_token.access_token}")

asyncio.run(main())
```

### User Authorization Flow

```python
async def user_auth_flow():
    async with AgentAuthManager(config, agent_config) as auth_manager:
        # Generate authorization URL for user
        scopes = ["openid", "profile", "email"]
        auth_url, state = auth_manager.get_authorization_url(scopes)
        
        print(f"Redirect user to: {auth_url}")
        
        # After user authorizes and you receive the auth code:
        # auth_code = "received_from_callback"
        
        # Get OBO token for the user
        obo_token = await auth_manager.get_obo_token(auth_code, scopes, agent_token)
        # print(f"User access token: {obo_token.access_token}")
```

## API Reference

### AgentAuthManager

Main class for handling agent authentication and OBO flows.

#### Methods

- `get_agent_token(scopes: Optional[List[str]] = None) -> OAuthToken`: Get access token for the agent
- `get_authorization_url(scopes: List[str], state: Optional[str] = None) -> Tuple[str, str]`: Generate authorization URL
- `get_obo_token(auth_code: str, agent_token: str, scopes: Optional[List[str]] = None) -> OAuthToken`: Exchange auth code for user token

### AgentConfig

Configuration for AI agent credentials.

- `agent_id: str`: Agent identifier
- `agent_secret: str`: Agent secret

## Requirements
- Python >= 3.10
- `httpx` (for async HTTP)
- `asgardeo` (base SDK)

## Development

```bash
# Install dependencies
poetry install

# Build
poetry build
```
