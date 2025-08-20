from pydantic import BaseModel, Field
from typing import List
from jupyter_server.extension.application import ExtensionApp
from jupyter_server.base.handlers import APIHandler as BaseAPIHandler
from jupyter_server.base.handlers import JupyterHandler
from tornado import web
import json
import ssl
import certifi
import aiohttp
import os

# Import token handler utility for user authentication
from d5m_ai.auth.token_handler import get_current_user_token_string

# Remote server configuration
D5M_REMOTE_HOST = os.getenv("D5M_REMOTE_HOST", "service.runcell.dev")

# Construct the full URL
if D5M_REMOTE_HOST.startswith("localhost"):
    REMOTE_BACKEND_URL = f"http://{D5M_REMOTE_HOST}"
else:
    REMOTE_BACKEND_URL = f"https://{D5M_REMOTE_HOST}"

class ImageAnalysisResponse(BaseModel):
    insights: str = Field(description="Insights about the visualization")
    suggestions: List[str] = Field(description="List of next-step code suggestions")

class VisualizationAnalysisHandler(BaseAPIHandler):
    
    def _get_user_token(self) -> str:
        """Get user token from saved OAuth token (same pattern as other handlers)."""
        token = get_current_user_token_string()
        if not token:
            print("[VIZ-PROXY] ❌ No user token found. User needs to authenticate.")
        else:
            print("[VIZ-PROXY] ✅ User token found")
        return token
    
    @web.authenticated
    async def post(self):
        try:
            print("VisualizationAnalysisHandler")
            print("Received visualization analysis request")
            
            # Get user token for authentication
            user_token = self._get_user_token()
            if not user_token:
                self.set_status(401)
                self.write(json.dumps({"error": "Authentication required. Please log in."}))
                return
            
            # Parse JSON body correctly
            data = json.loads(self.request.body.decode("utf-8"))
            image_base64 = data.get("imageBase64")
            previous_cells_code = data.get("previousCellsCode", "")

            if not image_base64:
                self.set_status(400)
                self.write(json.dumps({"error": "No image data provided"}))
                return

            # Prepare payload for remote server
            payload = {
                "imageBase64": image_base64,
                "previousCellsCode": previous_cells_code
            }

            # Forward request to remote server with user token authentication
            try:
                remote_url = f"{REMOTE_BACKEND_URL}/visualization_analysis"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {user_token}"  # Forward user token instead of access key
                }
                
                print(f"[VIZ-PROXY] Forwarding authenticated request to: {remote_url}")
                
                # Create SSL context with proper certificate verification
                try:
                    ssl_context = ssl.create_default_context(cafile=certifi.where())
                    print(f"[VIZ-PROXY] Using certifi certificate bundle for SSL verification")
                except Exception as e:
                    print(f"[VIZ-PROXY] Failed to create SSL context with certifi: {e}")
                    # Fallback to default SSL context
                    ssl_context = ssl.create_default_context()
                
                # Create connector with SSL context
                connector = aiohttp.TCPConnector(ssl=ssl_context)
                
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.post(remote_url, json=payload, headers=headers) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            self.set_status(response.status)
                            self.write(json.dumps({"error": f"Remote server error: {error_text}"}))
                            return
                        
                        response_data = await response.json()
                        self.set_header("Content-Type", "application/json")
                        self.write(json.dumps(response_data))
                        print("[VIZ-PROXY] Response forwarded successfully")

            except aiohttp.ClientError as e:
                print(f"[VIZ-PROXY] Network error: {e}")
                self.set_status(500)
                self.write(json.dumps({"error": f"Failed to connect to remote server: {str(e)}"}))
            except Exception as e:
                print(f"[VIZ-PROXY] Unexpected error: {e}")
                self.set_status(500)
                self.write(json.dumps({"error": f"Proxy error: {str(e)}"}))

        except Exception as e:
            print(f"[VIZ-PROXY] Handler error: {e}")
            self.set_status(500)
            self.write(json.dumps({"error": str(e)}))
