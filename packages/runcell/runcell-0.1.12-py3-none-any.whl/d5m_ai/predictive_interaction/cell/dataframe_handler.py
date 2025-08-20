from jupyter_server.base.handlers import APIHandler as BaseAPIHandler
from tornado import web
import json
import pandas as pd
import numpy as np
import os
import ssl
import certifi
import aiohttp
from pydantic import BaseModel, Field
from typing import List, Optional
from d5m_ai.utils.package_version import get_packages_version

# Import token handler for user authentication
from d5m_ai.auth.token_handler import get_current_user_token_string

# Remote server configuration
D5M_REMOTE_HOST = os.getenv("D5M_REMOTE_HOST", "service.runcell.dev")

# Construct the full URL
if D5M_REMOTE_HOST.startswith("localhost"):
    REMOTE_BACKEND_URL = f"http://{D5M_REMOTE_HOST}"
else:
    REMOTE_BACKEND_URL = f"https://{D5M_REMOTE_HOST}"

class SuggestionList(BaseModel):
    suggestions: List[str] = Field(description="List of code suggestions")


class PredictiveInteractionCellHandler(BaseAPIHandler):
    
    def _get_user_token(self) -> Optional[str]:
        """
        Get user token using existing token handler utility.
        This reuses the same authentication infrastructure as other handlers.
        """
        return get_current_user_token_string()
    
    @web.authenticated
    async def post(self):
        try:
            print("[PREDICTIVE-PROXY] Processing predictive interaction request")
            
            # Get user token using token handler utility
            user_token = self._get_user_token()
            if not user_token:
                self.set_status(401)
                self.finish(json.dumps({
                    "error": "No authentication token provided. Please log in.",
                    "status": "auth_required"
                }))
                return
            
            # Parse JSON body correctly
            data = json.loads(self.request.body.decode("utf-8"))
            df_data = data.get("dataframe")
            previous_cells_code = data.get("previousCellsCode")
            stream_mode = data.get("streamMode", False)

            if not df_data:
                self.set_status(400)
                self.write(json.dumps({"error": "No dataframe data provided"}))
                return

            # Convert to pandas DataFrame using headers and data
            df = pd.DataFrame(df_data["data"], columns=df_data["headers"])

            # Replace out-of-range float values (NaN, inf, -inf) with None for JSON serialization
            df_clean = df.replace([np.nan, np.inf, -np.inf], None)

            # Get metadata
            metadata = {
                "shape": df_clean.shape,
                "columns": df_clean.columns.tolist(),
                "dtypes": df_clean.dtypes.astype(str).to_dict(),
                "sample": df_clean.head(10).to_dict("records"),
            }

            # Prepare payload for remote server
            payload = {
                "dataframe": {
                    "headers": df_data["headers"],
                    "data": df_data["data"]
                },
                "previousCellsCode": previous_cells_code,
                "streamMode": stream_mode,
                "packagesVersion": get_packages_version()
            }

            # Forward request to remote server
            try:
                remote_url = f"{REMOTE_BACKEND_URL}/predictive_interaction"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {user_token}"
                }
                
                print(f"[PREDICTIVE-PROXY] Forwarding authenticated request to: {remote_url}")
                
                if stream_mode:
                    # Set up streaming response headers
                    self.set_header("Content-Type", "text/event-stream")
                    self.set_header("Cache-Control", "no-cache")
                    self.set_header("Connection", "keep-alive")
                    
                    # Send metadata immediately from proxy (like original version)
                    self.write(f"data: {json.dumps({'type': 'metadata', 'data': metadata})}\n\n")
                    await self.flush()
                    
                    # Make streaming request to remote server
                    # Create SSL context with proper certificate verification
                    try:
                        ssl_context = ssl.create_default_context(cafile=certifi.where())
                        print(f"[PREDICTIVE-PROXY] Using certifi certificate bundle for SSL verification")
                    except Exception as e:
                        print(f"[PREDICTIVE-PROXY] Failed to create SSL context with certifi: {e}")
                        # Fallback to default SSL context
                        ssl_context = ssl.create_default_context()
                    
                    # Create connector with SSL context
                    connector = aiohttp.TCPConnector(ssl=ssl_context)
                    
                    async with aiohttp.ClientSession(connector=connector) as session:
                        async with session.post(remote_url, json=payload, headers=headers) as response:
                            if response.status != 200:
                                error_text = await response.text()
                                
                                # Try to parse error as JSON for better error handling
                                try:
                                    error_data = json.loads(error_text)
                                    error_status = error_data.get("status", "error")
                                    error_message = error_data.get("error", error_text)
                                    
                                    # Handle specific error types
                                    if response.status == 401:
                                        error_event = json.dumps({
                                            'type': 'error', 
                                            'data': "Authentication failed. Please log in again."
                                        })
                                        self.write(f"data: {error_event}\n\n")
                                    elif response.status == 402:
                                        error_event = json.dumps({
                                            'type': 'error', 
                                            'data': error_message
                                        })
                                        self.write(f"data: {error_event}\n\n")
                                    else:
                                        error_event = json.dumps({'type': 'error', 'data': error_message})
                                        self.write(f"data: {error_event}\n\n")
                                except json.JSONDecodeError:
                                    # Fallback for non-JSON error responses
                                    error_event = json.dumps({'type': 'error', 'data': f"Remote server error: {error_text}"})
                                    self.write(f"data: {error_event}\n\n")
                                
                                await self.flush()
                                self.finish()
                                return
                            
                            # Stream the response from remote server to client
                            # Forward all content exactly as received to preserve SSE format
                            async for chunk in response.content:
                                if chunk:
                                    self.write(chunk)
                                    await self.flush()
                    
                    self.finish()
                    print("[PREDICTIVE-PROXY] Streaming response forwarded successfully")
                else:
                    # Non-streaming request
                    # Create SSL context with proper certificate verification
                    try:
                        ssl_context = ssl.create_default_context(cafile=certifi.where())
                        print(f"[PREDICTIVE-PROXY] Using certifi certificate bundle for SSL verification (non-streaming)")
                    except Exception as e:
                        print(f"[PREDICTIVE-PROXY] Failed to create SSL context with certifi: {e}")
                        # Fallback to default SSL context
                        ssl_context = ssl.create_default_context()
                    
                    # Create connector with SSL context
                    connector = aiohttp.TCPConnector(ssl=ssl_context)
                    
                    async with aiohttp.ClientSession(connector=connector) as session:
                        async with session.post(remote_url, json=payload, headers=headers) as response:
                            if response.status != 200:
                                error_text = await response.text()
                                
                                # Try to parse error as JSON for better error handling
                                try:
                                    error_data = json.loads(error_text)
                                    error_status = error_data.get("status", "error")
                                    error_message = error_data.get("error", error_text)
                                    
                                    # Handle specific error types
                                    if response.status == 401:
                                        self.set_status(401)
                                        self.finish(json.dumps({
                                            "error": "Authentication failed. Please log in again.",
                                            "status": "auth_error"
                                        }))
                                    elif response.status == 402:
                                        self.set_status(402)
                                        self.finish(json.dumps({
                                            "error": error_message,
                                            "status": "insufficient_credits"
                                        }))
                                    else:
                                        self.set_status(response.status)
                                        self.finish(json.dumps({
                                            "error": error_message,
                                            "status": error_status
                                        }))
                                except json.JSONDecodeError:
                                    # Fallback for non-JSON error responses
                                    self.set_status(response.status)
                                    self.finish(json.dumps({"error": f"Remote server error: {error_text}"}))
                                return
                            
                            response_data = await response.json()
                            self.set_header("Content-Type", "application/json")
                            self.write(json.dumps(response_data, allow_nan=False))
                            print("[PREDICTIVE-PROXY] Non-streaming response forwarded successfully")

            except aiohttp.ClientError as e:
                print(f"[PREDICTIVE-PROXY] Network error: {e}")
                if stream_mode:
                    error_event = json.dumps({'type': 'error', 'data': f"Failed to connect to remote server: {str(e)}"})
                    self.write(f"data: {error_event}\n\n")
                    await self.flush()
                    self.finish()
                else:
                    self.set_status(500)
                    self.write(json.dumps({"error": f"Failed to connect to remote server: {str(e)}"}))
            except Exception as e:
                print(f"[PREDICTIVE-PROXY] Unexpected error: {e}")
                if stream_mode:
                    error_event = json.dumps({'type': 'error', 'data': f"Proxy error: {str(e)}"})
                    self.write(f"data: {error_event}\n\n")
                    await self.flush()
                    self.finish()
                else:
                    self.set_status(500)
                    self.write(json.dumps({"error": f"Proxy error: {str(e)}"}))

        except Exception as e:
            print(f"[PREDICTIVE-PROXY] Handler error: {e}")
            self.set_status(500)
            self.write(json.dumps({"error": str(e)}))

