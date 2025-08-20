"""
Proxy handler for AI chat functionality.

This handler acts as a proxy between the frontend and the remote backend server.
It forwards chat requests to the remote backend and streams responses back to the frontend.

The remote backend handles all AI processing, while this proxy handles:
- User token-based authentication (replaces access key system)
- Request forwarding with user authentication
- Response streaming 
- CORS handling
- Error handling
- Credit-related error messaging
"""

import asyncio
import aiohttp
import logging
import json
import os
import ssl
import certifi
from typing import Dict, Any, Optional
from jupyter_server.base.handlers import APIHandler
from tornado import web

from ..utils import build_remote_backend_url
from ..auth.token_handler import get_current_user_token_string

logging.basicConfig(level=logging.INFO)


class AIChatProxyHandler(APIHandler):
    """Proxy handler for AI chat requests that forwards to remote backend."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get remote backend URL using unified URL builder
        self.remote_backend_url = build_remote_backend_url("chat").replace("/chat", "")
        
        logging.info(f"[CHAT-PROXY] Initialized with remote backend: {self.remote_backend_url}")
        logging.info("[CHAT-PROXY] Token authentication enabled - will forward tokens to remote backend")
    
    async def get_user_token(self) -> Optional[str]:
        """
        Extract user token from local file or request.
        
        Priority order:
        1. Local file token (saved when OAuth succeeds)
        2. Request headers/cookies (fallback for compatibility)
        
        Returns:
            User token if found, None otherwise
        """
        # **PRIORITY 1: Check local file token (saved when OAuth succeeds)**
        local_token = get_current_user_token_string()
        if local_token:
            logging.info(f"[CHAT-PROXY] ✅ Found token in local file (length: {len(local_token)})")
            return local_token
        
        logging.info("[CHAT-PROXY] No token found in local file, checking request headers/cookies...")
        
        # Debug: Log all available headers and cookies for troubleshooting
        logging.info(f"[CHAT-PROXY] DEBUG - Request headers: {dict(self.request.headers)}")
        logging.info(f"[CHAT-PROXY] DEBUG - Available cookies: {list(self.cookies.keys())}")
        
        # Check for plugin auth token specifically
        plugin_token = self.get_cookie("plugin_auth_token_v2")
        if plugin_token:
            logging.info(f"[CHAT-PROXY] DEBUG - Found plugin_auth_token_v2: {plugin_token[:20]}...")
        else:
            logging.info("[CHAT-PROXY] DEBUG - No plugin_auth_token_v2 cookie found")
            
        # Check each Supabase token type
        for cookie_name in self.cookies.keys():
            if cookie_name.startswith("sb-") and "auth-token" in cookie_name:
                cookie_value = self.cookies[cookie_name]
                token_value = cookie_value.value if hasattr(cookie_value, 'value') else str(cookie_value)
                logging.info(f"[CHAT-PROXY] DEBUG - {cookie_name}: {token_value[:20]}...")
        
        # Check Authorization header
        auth_header = self.request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
            logging.info("[CHAT-PROXY] Found token in Authorization header")
            return token
        
        # Check X-User-Token header
        user_token = self.request.headers.get("X-User-Token", "")
        if user_token:
            logging.info("[CHAT-PROXY] Found token in X-User-Token header")
            return user_token
        
        # Look for actual Supabase auth tokens that are present in the cookies
        supabase_token_patterns = [
            "sb-",  # Supabase tokens start with sb-
            "plugin_auth_token_v2",
            "auth_token", 
            "user_token",
            "jwt_token"
        ]
        
        # **PRIORITY 1: Plugin Auth Token (JWT format expected by localhost:3000)**
        plugin_token = self.get_cookie("plugin_auth_token_v2")
        if plugin_token and plugin_token.startswith("eyJ") and plugin_token.count('.') == 2:
            logging.info(f"[CHAT-PROXY] ✅ Found valid JWT plugin_auth_token_v2 (length: {len(plugin_token)})")
            return plugin_token
        elif plugin_token:
            logging.warning(f"[CHAT-PROXY] ⚠️ plugin_auth_token_v2 exists but doesn't look like JWT: {plugin_token[:20]}...")
        
        # **PRIORITY 2: Other JWT tokens in cookies**
        for cookie_name in ["auth_token", "user_token", "jwt_token"]:
            token_cookie = self.get_cookie(cookie_name)
            if token_cookie and token_cookie.startswith("eyJ") and token_cookie.count('.') == 2:
                logging.info(f"[CHAT-PROXY] ✅ Found JWT token in cookie: {cookie_name} (length: {len(token_cookie)})")
                return token_cookie
            elif token_cookie:
                logging.warning(f"[CHAT-PROXY] ⚠️ {cookie_name} exists but not JWT format: {token_cookie[:20]}...")
        
        # **FALLBACK: Supabase tokens (likely incompatible with localhost:3000)**
        for cookie_name, cookie_value in self.cookies.items():
            if (cookie_name.startswith("sb-") and 
                "auth-token" in cookie_name and 
                "code-verifier" not in cookie_name):
                token_value = cookie_value.value if hasattr(cookie_value, 'value') else str(cookie_value)
                logging.warning(f"[CHAT-PROXY] ⚠️ Using Supabase token as fallback: {cookie_name} - likely incompatible with localhost:3000")
                logging.warning(f"[CHAT-PROXY] Consider setting D5M_TEST_USER_TOKEN environment variable with a valid JWT")
                return token_value
        
        # Check for token in query parameters (fallback, not recommended for production)
        token_param = self.get_argument("token", None)
        if token_param:
            logging.info("[CHAT-PROXY] Found token in query parameters")
            return token_param
        
        # Check request body for token (in case frontend sends it in the body)
        try:
            body_data = json.loads(self.request.body.decode("utf-8"))
            if "user_token" in body_data:
                logging.info("[CHAT-PROXY] Found token in request body")
                return body_data["user_token"]
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        
        # Log detailed debugging information
        logging.warning("[CHAT-PROXY] No user token found in request")
        logging.warning(f"[CHAT-PROXY] Available Supabase cookies: {[name for name in self.cookies.keys() if name.startswith('sb-')]}")
        
        return None
    
    def get_test_token_from_env(self) -> Optional[str]:
        """
        Get test token from environment variable for development/testing.
        
        This is a temporary method to facilitate testing without frontend integration.
        Remove this in production.
        
        Returns:
            Test token if available
        """
        test_token = os.environ.get("D5M_TEST_USER_TOKEN")
        if test_token:
            # Validate that test token is a JWT
            if test_token.startswith("eyJ") and test_token.count('.') == 2:
                logging.warning("[CHAT-PROXY] ✅ Using valid JWT test token from D5M_TEST_USER_TOKEN")
                logging.warning("[CHAT-PROXY] This should only be used for testing!")
                return test_token
            else:
                logging.error(f"[CHAT-PROXY] ❌ D5M_TEST_USER_TOKEN is not a valid JWT format: {test_token[:20]}...")
                logging.error("[CHAT-PROXY] JWT should start with 'eyJ' and have exactly 2 dots")
                return None
        return None
    

        
    @web.authenticated
    async def post(self):
        """Handle POST requests by forwarding to remote backend with user authentication."""
        try:
            # Step 1: Get user token (no verification - let remote backend handle that)
            user_token = await self.get_user_token()
            
            # Fallback to test token if no token found (for development/testing)
            if not user_token:
                user_token = self.get_test_token_from_env()
            
            if not user_token:
                self.set_status(401)
                self.finish(json.dumps({
                    "error": "No authentication token provided. Please log in or set D5M_TEST_USER_TOKEN environment variable for testing.",
                    "status": "auth_required",
                    "debug_info": {
                        "frontend_integration_needed": True,
                        "suggestions": [
                            "Set D5M_TEST_USER_TOKEN environment variable for testing",
                            "Frontend should send token in Authorization header: 'Bearer <token>'",
                            "Frontend should send token in X-User-Token header",
                            "Check if Supabase auth tokens are available in cookies"
                        ]
                    }
                }))
                return
            
            logging.info(f"[CHAT-PROXY] Found user token, forwarding to remote backend")
            
            # Step 2: Parse request body
            body_data = json.loads(self.request.body.decode("utf-8"))
            messages = body_data.get("messages", [])
            code_cells = body_data.get("code_cells", [])
            stream = body_data.get("stream", True)
            model = body_data.get("model", "anthropic/claude-3-5-sonnet-20241022")
            
            logging.info(f"[CHAT-PROXY] Forwarding chat request: model={model}, stream={stream}")
            
            if not messages:
                self.set_status(400)
                self.finish(json.dumps({"error": "No messages provided"}))
                return

            # Step 3: Forward request to remote backend with user token
            await self._forward_to_remote_backend(body_data, stream, user_token)
            
        except Exception as e:
            logging.error(f"[CHAT-PROXY] Error handling chat request: {e}")
            self.set_status(500)
            self.finish(json.dumps({
                "error": str(e),
                "status": "error"
            }))

    async def _forward_to_remote_backend(self, body_data: Dict[str, Any], stream: bool, user_token: str):
        """Forward request to remote backend and handle response."""
        try:
            remote_url = f"{self.remote_backend_url}/chat"
            
            # Prepare headers with user authentication
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {user_token}'
            }
            logging.debug("[CHAT-PROXY] Adding user token to remote backend request")
            
            # Create SSL context with proper certificate verification
            try:
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                logging.debug("[CHAT-PROXY] Using certifi certificate bundle for SSL verification")
            except Exception as e:
                logging.warning(f"[CHAT-PROXY] Failed to create SSL context with certifi: {e}")
                # Fallback to default SSL context
                ssl_context = ssl.create_default_context()
            
            # Create connector with SSL context
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    remote_url,
                    json=body_data,
                    headers=headers
                ) as response:
                    
                    if response.status != 200:
                        # Handle error response
                        error_text = await response.text()
                        logging.error(f"[CHAT-PROXY] Remote backend error {response.status}: {error_text}")
                        
                        # Try to parse error as JSON for better error handling
                        try:
                            error_data = json.loads(error_text)
                            error_status = error_data.get("status", "error")
                            error_message = error_data.get("error", error_text)
                            
                            # Handle specific error types
                            if response.status == 401:
                                # Authentication error
                                self.set_status(401)
                                self.finish(json.dumps({
                                    "error": "Authentication failed. Please log in again.",
                                    "status": "auth_error"
                                }))
                            elif response.status == 402:
                                # Insufficient credits
                                self.set_status(402)
                                self.finish(json.dumps({
                                    "error": error_message,
                                    "status": "insufficient_credits"
                                }))
                            else:
                                # Other errors
                                self.set_status(response.status)
                                self.finish(json.dumps({
                                    "error": error_message,
                                    "status": error_status
                                }))
                        except json.JSONDecodeError:
                            # Fallback for non-JSON error responses
                            self.set_status(response.status)
                            self.finish(json.dumps({
                                "error": f"Remote backend error: {error_text}",
                                "status": "error"
                            }))
                        return
                    
                    if stream:
                        # Handle streaming response
                        await self._handle_streaming_response(response)
                    else:
                        # Handle non-streaming response
                        response_data = await response.json()
                        self.finish(json.dumps(response_data))
                        
        except aiohttp.ClientConnectorError as e:
            logging.error(f"[CHAT-PROXY] Cannot connect to remote backend at {self.remote_backend_url}: {e}")
            self.set_status(503)
            self.finish(json.dumps({
                "error": f"Cannot connect to chat remote backend. Please ensure the remote backend server is running at {self.remote_backend_url}",
                "status": "error"
            }))
        except Exception as e:
            logging.error(f"[CHAT-PROXY] Error forwarding to remote backend: {e}")
            self.set_status(500)
            self.finish(json.dumps({
                "error": str(e),
                "status": "error"
            }))

    async def _handle_streaming_response(self, response: aiohttp.ClientResponse):
        """Handle streaming response from remote backend."""
        try:
            # Set up streaming response headers (exactly like original handler)
            self.set_header("Content-Type", "text/event-stream")
            self.set_header("Cache-Control", "no-cache")
            self.set_header("Connection", "keep-alive")
            
            logging.info("[CHAT-PROXY] Starting to stream response from remote backend")
            
            # Read response content as chunks and forward exactly
            async for chunk in response.content.iter_chunks():
                if chunk[0]:  # chunk[0] is the actual data
                    chunk_data = chunk[0]
                    
                    # Forward the chunk exactly as received
                    self.write(chunk_data)
                    await self.flush()
                    
                    # Check if this chunk contains the completion event
                    chunk_text = chunk_data.decode('utf-8', errors='ignore')
                    if 'data: ' in chunk_text and '"status": "done"' in chunk_text:
                        logging.info("[CHAT-PROXY] Streaming completed")
                        # Don't call finish() - let the function end naturally like original
                        break
                        
        except Exception as e:
            logging.error(f"[CHAT-PROXY] Error during streaming: {e}")
            # Send error event to frontend
            error_data = json.dumps({'error': str(e), 'status': 'error'})
            self.write(f"data: {error_data}\n\n")
            await self.flush()

    async def options(self):
        """Handle CORS preflight requests."""
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_status(200)


# For backward compatibility, also export as AIChatHandler
AIChatHandler = AIChatProxyHandler 