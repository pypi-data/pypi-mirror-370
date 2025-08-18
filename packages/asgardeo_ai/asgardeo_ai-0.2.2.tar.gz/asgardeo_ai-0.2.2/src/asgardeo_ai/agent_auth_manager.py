"""
Copyright (c) 2025, WSO2 LLC. (https://www.wso2.com).
WSO2 LLC. licenses this file to you under the Apache License,
Version 2.0 (the "License"); you may not use this file except
in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. See the License for the
specific language governing permissions and limitations
under the License.
"""

"""Agent-enhanced OAuth2 authentication manager for Asgardeo AI."""

import logging
import base64
import os
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlencode
from dataclasses import dataclass

from asgardeo import (
    AsgardeoConfig, 
    OAuthToken, 
    FlowStatus, 
    AsgardeoNativeAuthClient, 
    AsgardeoTokenClient,
    AuthenticationError,
    TokenError,
    ValidationError,
    generate_pkce_pair,
    generate_state,
    build_authorization_url
)

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for AI agent authentication."""
    
    agent_id: str
    agent_secret: str

class AgentAuthManager:
    """Agent-enhanced OAuth2 authentication manager for AI agents."""
    
    def __init__(
        self,
        config: AsgardeoConfig,
        agent_config: Optional[AgentConfig] = None,
        authorization_timeout: int = 300,
    ):
        """Initialize the agent auth manager.
        
        :param config: Asgardeo configuration
        :param agent_config: Optional agent-specific configuration
        :param authorization_timeout: Timeout for authorization operations
        """
        self.config = config
        self.agent_config = agent_config
        self.authorization_timeout = authorization_timeout
        self.token_client = AsgardeoTokenClient(config)

    async def get_agent_token(self, scopes: Optional[List[str]] = None) -> OAuthToken:
        """Get access token for the AI agent using agent credentials.
        
        :param scopes: List of OAuth scopes to request
        :return: OAuth token for the agent
        """
        if not self.agent_config:
            raise ValidationError("Agent configuration is required for agent authentication.")
        
        try:
            async with AsgardeoNativeAuthClient(self.config) as native_client:
                # Set custom scope if provided
                if scopes:
                    # Note: We need to modify the config temporarily
                    original_scope = self.config.scope
                    self.config.scope = ' '.join(scopes)
                
                # Start authentication flow
                code_verifier, code_challenge = generate_pkce_pair()
                params = {
                    "code_challenge": code_challenge,
                    "code_challenge_method": "S256",
                }
                init_response = await native_client.authenticate(params=params)
                
                if native_client.flow_status == FlowStatus.SUCCESS_COMPLETED:
                    auth_data = init_response.get('authData', {})
                elif native_client.flow_status == FlowStatus.INCOMPLETE:
                    # Find username/password authenticator
                    authenticators = native_client.next_step.get('authenticators', [])
                    username_auth = next(
                        (auth for auth in authenticators
                         if auth.get('authenticator') in ['Username & Password']),
                        None
                    )
                    if not username_auth:
                        raise AuthenticationError("No username/password authenticator found.")
                    
                    # Authenticate with agent credentials
                    auth_response = await native_client.authenticate(
                        authenticator_id=username_auth['authenticatorId'],
                        params={
                            'username': self.agent_config.agent_id,
                            'password': self.agent_config.agent_secret
                        }
                    )
                    
                    if native_client.flow_status == FlowStatus.SUCCESS_COMPLETED:
                        auth_data = auth_response.get('authData', {})
                    else:
                        raise AuthenticationError(f"Agent authentication failed with status: {native_client.flow_status}")
                else:
                    raise AuthenticationError(f"Unexpected authentication status: {native_client.flow_status}")

                code = auth_data.get('code')
                if not code:
                    raise TokenError("No authorization code received from authentication flow.")

                # Exchange code for token
                token = await self.token_client.get_token('authorization_code', code=code, code_verifier=code_verifier)
                
                # Restore original scope
                if scopes:
                    self.config.scope = original_scope
                    
                return token
        
        except (AuthenticationError, TokenError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Agent authentication failed: {e}")
            raise AuthenticationError(f"Agent authentication failed: {e}")

    def get_authorization_url(
        self,
        scopes: List[str],
        state: Optional[str] = None,
        resource: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[str, str]:
        """Generate authorization URL for user authentication.
        
        :param scopes: List of OAuth scopes to request
        :param state: Optional state parameter (generated if not provided)
        :param resource: Optional resource parameter
        :param kwargs: Additional parameters for the authorization URL
        :return: Tuple of (authorization_url, state)
        """
        if not state:
            state = generate_state()
            
        auth_params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "response_type": "code",
        }
        
        if resource:
            auth_params["resource"] = resource
            
        if self.agent_config:
            auth_params["requested_actor"] = self.agent_config.agent_id
            
        auth_params.update(kwargs)
        
        auth_url = build_authorization_url(
            f"{self.config.base_url}/oauth2/authorize",
            auth_params
        )
        return auth_url, state
    
    def get_authorization_url_with_pkce(
        self,
        scopes: List[str],
        state: Optional[str] = None,
        resource: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[str, str, str]:
        """Generate authorization URL for user authentication.
        
        :param scopes: List of OAuth scopes to request
        :param state: Optional state parameter (generated if not provided)
        :param resource: Optional resource parameter
        :param kwargs: Additional parameters for the authorization URL
        :return: Tuple of (authorization_url, state)
        """
        if not state:
            state = generate_state()

        code_verifier, code_challenge = generate_pkce_pair()    
            
        auth_params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "response_type": "code",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        
        if resource:
            auth_params["resource"] = resource
            
        if self.agent_config:
            auth_params["requested_actor"] = self.agent_config.agent_id
            
        auth_params.update(kwargs)
        
        auth_url = build_authorization_url(
            f"{self.config.base_url}/oauth2/authorize",
            auth_params
        )
        return auth_url, state, code_verifier    

    async def get_obo_token(
        self,
        auth_code: str,
        agent_token: str,
        scopes: Optional[List[str]] = None,
        code_verifier: Optional[str] = None
    ) -> OAuthToken:
        """Get on-behalf-of (OBO) token for user using authorization code.
        
        :param auth_code: Authorization code from user authentication
        :param scopes: Optional list of scopes to request
        :param agent_token: Optional agent token for delegation
        :return: OAuth token for the user
        """
        if not auth_code:
            raise ValidationError("Authorization code is required for OBO token exchange.")
        
        try:
            actor_token_val = agent_token.access_token if agent_token else None
            scope_str = ' '.join(scopes) if scopes else None
            
            token = await self.token_client.get_token(
                'authorization_code',
                code=auth_code,
                scope=scope_str,
                actor_token=actor_token_val,
                code_verifier=code_verifier
            )
            return token
            
        except (TokenError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"OBO token exchange failed: {e}")
            raise TokenError(f"OBO token exchange failed: {e}")

    async def revoke_token(
        self, 
        token: str, 
        token_type_hint: str = "access_token"
    ) -> bool:
        """Revoke an access or refresh token.
        
        :param token: Token to revoke
        :param token_type_hint: Type of token being revoked
        :return: True if revocation succeeded, False otherwise
        """
        try:
            return await self.token_client.revoke_token(token, token_type_hint)
        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            return False

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        return False

    # Backwards compatibility
    async def close(self):
        """Close the agent auth manager and cleanup resources."""
        await self.token_client.close()
