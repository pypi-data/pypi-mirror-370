from jupyter_server.base.handlers import APIHandler
import tornado.web as web
import os
import json
import uuid
from datetime import datetime
import asyncio
import logging
from typing import Dict, Any

from ..utils import build_remote_backend_url
from ..auth import get_current_user_token_string
import aiohttp

# Directory setup for history storage
HISTORY_DIR = os.path.join(os.path.expanduser('~'), '.d5m_ai', 'history')
HISTORY_DB_PATH = os.path.join(HISTORY_DIR, 'history_db.json')

# Create the history directory if it doesn't exist
os.makedirs(HISTORY_DIR, exist_ok=True)

# Initialize the history database if it doesn't exist
if not os.path.exists(HISTORY_DB_PATH):
    with open(HISTORY_DB_PATH, 'w') as f:
        json.dump([], f)

class AIChatHistoryListHandler(APIHandler):
    @web.authenticated
    async def get(self):
        """Get a list of all chat histories"""
        try:
            # Read the history database file
            with open(HISTORY_DB_PATH, 'r') as f:
                histories = json.load(f)
            
            # Sort histories by updatedAt in descending order (newest first)
            # Parse ISO format date strings for proper sorting
            def get_updated_at_datetime(history):
                updated_at = history.get("updatedAt", "")
                try:
                    return datetime.fromisoformat(updated_at)
                except (ValueError, TypeError):
                    # Return a very old date as fallback
                    return datetime.min
                    
            histories.sort(key=get_updated_at_datetime, reverse=True)
            
            # Return the list of histories
            self.finish(json.dumps({"histories": histories, "status": "success"}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": str(e), "status": "error"}))

class AIChatHistoryHandler(APIHandler):
    @web.authenticated
    async def get(self):
        """Get a specific chat history"""
        try:
            # Get history_id from query parameters
            history_id = self.get_query_argument("history_id", None)
            
            if not history_id:
                self.set_status(400)
                self.finish(json.dumps({"error": "History ID is required", "status": "error"}))
                return
                
            # Build the path to the history file
            history_file_path = os.path.join(HISTORY_DIR, f"{history_id}.json")
            
            # Check if the history file exists
            if not os.path.exists(history_file_path):
                self.set_status(404)
                self.finish(json.dumps({"error": "History not found", "status": "error"}))
                return
            
            # Read the history file
            with open(history_file_path, 'r') as f:
                history = json.load(f)
            
            # Return the history
            self.finish(json.dumps({"history": history, "status": "success"}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": str(e), "status": "error"}))
    
    @web.authenticated
    async def post(self):
        """Create a new chat history"""
        try:
            # Parse the request body
            body = json.loads(self.request.body.decode("utf-8"))
            
            # Get history_id from body or generate a new one
            history_id = body.get("history_id", str(uuid.uuid4()))
            
            # Get the title or use a default
            title = body.get("title", f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Create the history object
            now = datetime.now().isoformat()
            history = {
                "id": history_id,
                "title": title,
                "createdAt": now,
                "updatedAt": now,
                "messages": body.get("messages", [])
            }
            
            # Save the full history to a file
            history_file_path = os.path.join(HISTORY_DIR, f"{history_id}.json")
            with open(history_file_path, 'w') as f:
                json.dump(history, f)
            
            # Update the history database
            history_brief = {
                "id": history_id,
                "title": title,
                "createdAt": now,
                "updatedAt": now
            }
            
            with open(HISTORY_DB_PATH, 'r') as f:
                histories = json.load(f)
            
            histories.append(history_brief)
            
            with open(HISTORY_DB_PATH, 'w') as f:
                json.dump(histories, f)
            
            # Return the created history
            self.finish(json.dumps({"history": history, "status": "success"}))

            # Fire-and-forget remote backup (non-blocking, best-effort)
            try:
                asyncio.create_task(self._backup_history_remote(history))
            except Exception as e:
                logging.debug(f"[CHAT-HISTORY] Failed to schedule remote backup: {e}")
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": str(e), "status": "error"}))
    
    @web.authenticated
    async def put(self):
        """Update an existing chat history"""
        try:
            # Parse the request body
            body = json.loads(self.request.body.decode("utf-8"))
            history_id = body.get("history_id")
            
            if not history_id:
                self.set_status(400)
                self.finish(json.dumps({"error": "History ID is required", "status": "error"}))
                return
                
            # Build the path to the history file
            history_file_path = os.path.join(HISTORY_DIR, f"{history_id}.json")
            
            # Check if the history file exists
            if not os.path.exists(history_file_path):
                self.set_status(404)
                self.finish(json.dumps({"error": "History not found", "status": "error"}))
                return
            
            # Read the current history
            with open(history_file_path, 'r') as f:
                history = json.load(f)
            
            # Update the history
            title = body.get("title")
            messages = body.get("messages")
            
            now = datetime.now().isoformat()
            history["updatedAt"] = now
            
            if title:
                history["title"] = title
            
            if messages:
                history["messages"] = messages
            
            # Save the updated history
            with open(history_file_path, 'w') as f:
                json.dump(history, f)
            
            # Update the history database
            with open(HISTORY_DB_PATH, 'r') as f:
                histories = json.load(f)
            
            for i, h in enumerate(histories):
                if h["id"] == history_id:
                    histories[i]["title"] = history["title"]
                    histories[i]["updatedAt"] = now
                    break
            
            with open(HISTORY_DB_PATH, 'w') as f:
                json.dump(histories, f)
            
            # Return the updated history
            self.finish(json.dumps({"history": history, "status": "success"}))

            # Fire-and-forget remote backup (non-blocking, best-effort)
            try:
                asyncio.create_task(self._backup_history_remote(history))
            except Exception as e:
                logging.debug(f"[CHAT-HISTORY] Failed to schedule remote backup: {e}")
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": str(e), "status": "error"}))
    
    @web.authenticated
    async def delete(self):
        """Delete a chat history"""
        try:
            # Parse the request body
            body = json.loads(self.request.body.decode("utf-8"))
            history_id = body.get("history_id")
            
            if not history_id:
                self.set_status(400)
                self.finish(json.dumps({"error": "History ID is required", "status": "error"}))
                return
                
            # Build the path to the history file
            history_file_path = os.path.join(HISTORY_DIR, f"{history_id}.json")
            
            # Check if the history file exists
            if not os.path.exists(history_file_path):
                self.set_status(404)
                self.finish(json.dumps({"error": "History not found", "status": "error"}))
                return
            
            # Delete the history file
            os.remove(history_file_path)
            
            # Update the history database
            with open(HISTORY_DB_PATH, 'r') as f:
                histories = json.load(f)
            
            histories = [h for h in histories if h["id"] != history_id]
            
            with open(HISTORY_DB_PATH, 'w') as f:
                json.dump(histories, f)
            
            # Return success
            self.finish(json.dumps({"status": "success"}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": str(e), "status": "error"}))

    async def _backup_history_remote(self, history: Dict[str, Any]):
        """Send chat history to remote backup endpoint without impacting UX."""
        try:
            token = get_current_user_token_string()
            if not token:
                return

            # Build remote chat HTTP base and then join backup path
            chat_base = build_remote_backend_url("chat")  # e.g. https://host/chat
            # Replace trailing '/chat' with our backup path root
            if chat_base.endswith('/chat'):
                base = chat_base.rsplit('/chat', 1)[0]
            else:
                base = chat_base
            url = f"{base}/chat_history/backup"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }

            payload = {
                "id": history.get("id"),
                "title": history.get("title"),
                "createdAt": history.get("createdAt"),
                "updatedAt": history.get("updatedAt"),
                "messages": history.get("messages", []),
                "version": 1,
            }

            timeout = aiohttp.ClientTimeout(total=3)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    # Best-effort; don't raise for status
                    _ = await resp.text()
        except Exception:
            # Completely swallow errors to avoid UX impact
            pass