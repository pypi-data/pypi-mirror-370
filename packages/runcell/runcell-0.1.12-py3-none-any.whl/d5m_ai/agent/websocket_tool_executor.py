import asyncio
import uuid

from .cores import ToolExecutor, ShellExecutor, PermissionHandler

class WebSocketToolExecutor(ToolExecutor):
    """
    Tool executor implementation that bridges to WebSocket handler.
    This handles the infrastructure concerns of communicating with the frontend.
    """
    
    def __init__(self, handler):
        self.handler = handler
        # Create shell executor with permission handler
        self.shell_executor = ShellExecutor(WebSocketPermissionHandler(handler))
    
    async def cell_execute(self, code: str) -> str:
        """Execute code in a cell via WebSocket."""
        request_id = str(uuid.uuid4())
        self.handler.current_request_id = request_id

        # Prepare a brand-new waiter
        if self.handler.waiter and not self.handler.waiter.done():
            self.handler.waiter.cancel()
        self.handler.waiter = asyncio.get_running_loop().create_future()

        # Send the execution request to the browser
        try:
            await self.handler._safe_write_message({
                "type": "cell_execute",
                "code": code,
                "request_id": request_id,
                "connection_id": self.handler.connection_id,
            })
        except Exception as e:
            raise RuntimeError(f"Failed to send cell execution request: {e}")

        # Await the result (or timeout)
        try:
            result = await asyncio.wait_for(self.handler.waiter, timeout=90.0)
        except asyncio.TimeoutError:
            result = "Error: No result received from code execution (timeout)"
        finally:
            self.handler.waiter = None

        return result
    
    async def shell_execute(self, command: str) -> str:
        """Execute shell command via shell executor."""
        return await self.shell_executor.execute_command(command)
    
    async def edit_cell(self, cell_index: int, code: str, rerun: bool = False, request_id: str = None) -> str:
        """Edit a cell via WebSocket."""
        if request_id is None:
            request_id = str(uuid.uuid4())
        self.handler.current_request_id = request_id

        # Prepare a brand-new waiter
        if self.handler.waiter and not self.handler.waiter.done():
            self.handler.waiter.cancel()
        self.handler.waiter = asyncio.get_running_loop().create_future()

        # Send the edit cell request to the browser
        try:
            await self.handler._safe_write_message({
                "type": "edit_cell",
                "cell_index": cell_index,
                "code": code,
                "rerun": rerun,
                "request_id": request_id,
                "connection_id": self.handler.connection_id,
            })
        except Exception as e:
            raise RuntimeError(f"Failed to send edit cell request: {e}")

        # Await the result (or timeout)
        try:
            result = await asyncio.wait_for(self.handler.waiter, timeout=90.0)
        except asyncio.TimeoutError:
            result = "Error: No result received from cell edit (timeout)"
        finally:
            self.handler.waiter = None

        return result
    
    async def rerun_all_cells(self, request_id: str = None) -> str:
        """Rerun all cells via WebSocket with permission check."""
        # Always ask for user permission since this can overwrite existing outputs
        if request_id is None:
            request_id = str(uuid.uuid4())
        
        # Create a waiter for the permission response
        permission_waiter = asyncio.get_running_loop().create_future()
        
        # Store the waiter temporarily
        original_waiter = self.handler.waiter
        self.handler.waiter = permission_waiter
        
        try:
            # Send permission request to frontend
            await self.handler._safe_write_message({
                "type": "rerun_all_cells_permission_request",
                "message": "Rerun all cells will execute all cells from top to bottom and may overwrite existing outputs. Do you want to proceed?",
                "request_id": request_id,
                "connection_id": self.handler.connection_id,
            })
            
            # Wait for user response (with timeout)
            try:
                permission_response = await asyncio.wait_for(permission_waiter, timeout=120.0)
                if not permission_response or permission_response.get("allowed") != True:
                    return "Rerun all cells cancelled by user. This operation can overwrite existing cell outputs."
            except asyncio.TimeoutError:
                return "Rerun all cells timed out waiting for user permission."
        finally:
            # Restore original waiter
            self.handler.waiter = original_waiter

        # If permission granted, proceed with the rerun all cells request
        request_id = str(uuid.uuid4())
        self.handler.current_request_id = request_id

        # Prepare a brand-new waiter for the actual execution
        if self.handler.waiter and not self.handler.waiter.done():
            self.handler.waiter.cancel()
        self.handler.waiter = asyncio.get_running_loop().create_future()

        # Send the rerun all cells request to the browser
        try:
            await self.handler._safe_write_message({
                "type": "rerun_all_cells",
                "request_id": request_id,
                "connection_id": self.handler.connection_id,
            })
        except Exception as e:
            raise RuntimeError(f"Failed to send rerun all cells request: {e}")

        # Await the result (or timeout)
        try:
            result = await asyncio.wait_for(self.handler.waiter, timeout=120.0)  # Longer timeout for all cells
        except asyncio.TimeoutError:
            result = "Error: No result received from rerun all cells (timeout)"
        finally:
            self.handler.waiter = None

        return result

    async def interpret_image(self, image_url: str) -> str:
        """Interpret an image using a vision-capable LLM."""
        return "Error: interpret_image tool should be handled by the remote backend, not the local executor"

    async def insert_markdown_cell(self, cell_index: int, content: str, request_id: str = None) -> str:
        """Insert a markdown cell via WebSocket."""
        if request_id is None:
            request_id = str(uuid.uuid4())
        self.handler.current_request_id = request_id

        # Prepare a brand-new waiter
        if self.handler.waiter and not self.handler.waiter.done():
            self.handler.waiter.cancel()
        self.handler.waiter = asyncio.get_running_loop().create_future()

        # Send the insert markdown cell request to the browser
        try:
            await self.handler._safe_write_message({
                "type": "insert_markdown_cell",
                "cell_index": cell_index,
                "content": content,
                "request_id": request_id,
                "connection_id": self.handler.connection_id,
            })
        except Exception as e:
            raise RuntimeError(f"Failed to send insert markdown cell request: {e}")

        # Await the result (or timeout)
        try:
            result = await asyncio.wait_for(self.handler.waiter, timeout=30.0)
        except asyncio.TimeoutError:
            result = "Error: No result received from insert markdown cell (timeout)"
        finally:
            self.handler.waiter = None

        return result

    async def read_file(self, file_path: str, start_row_index: int = 0, end_row_index: int = 200) -> str:
        """Read content from a file with optional row range specification."""
        try:
            # Validate arguments
            if not file_path:
                return "Error: file_path is required"
                
            # Read file content with row range support
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    
                # Handle row range
                total_lines = len(lines)
                
                # Handle negative end_row_index (read to end of file)
                if end_row_index == -1:
                    end_row_index = total_lines - 1
                    
                # Validate row indices
                start_row_index = max(0, start_row_index)
                end_row_index = min(end_row_index, total_lines - 1)
                
                if start_row_index > end_row_index:
                    return f"Error: start_row_index ({start_row_index}) is greater than end_row_index ({end_row_index})"
                elif start_row_index >= total_lines:
                    return f"Error: start_row_index ({start_row_index}) is beyond file length ({total_lines} lines)"
                else:
                    # Extract the specified range of lines
                    selected_lines = lines[start_row_index:end_row_index + 1]
                    content = ''.join(selected_lines)
                    
                    # Add metadata about the file and range
                    metadata = f"File: {file_path}\n"
                    metadata += f"Total lines: {total_lines}\n"
                    metadata += f"Showing lines {start_row_index + 1}-{min(end_row_index + 1, total_lines)} (1-indexed)\n"
                    metadata += "=" * 50 + "\n"
                    
                    return metadata + content
                    
            except FileNotFoundError:
                return f"Error: File '{file_path}' not found"
            except PermissionError:
                return f"Error: Permission denied reading file '{file_path}'"
            except UnicodeDecodeError:
                return f"Error: File '{file_path}' contains binary data or unsupported encoding"
            except Exception as read_error:
                return f"Error reading file '{file_path}': {str(read_error)}"
                
        except Exception as e:
            return f"Error in read_file tool: {str(e)}"


class WebSocketPermissionHandler(PermissionHandler):
    """Permission handler that uses WebSocket to request user permissions."""
    
    def __init__(self, handler):
        self.handler = handler
    
    async def request_permission(self, command: str, dangerous_pattern: str) -> bool:
        """Request permission via WebSocket."""
        request_id = str(uuid.uuid4())
        
        # Create a waiter for the permission response
        permission_waiter = asyncio.get_running_loop().create_future()
        
        # Store the waiter temporarily
        original_waiter = self.handler.waiter
        self.handler.waiter = permission_waiter
        
        try:
            # Send permission request to frontend
            await self.handler._safe_write_message({
                "type": "shell_permission_request",
                "command": command,
                "dangerous_pattern": dangerous_pattern,
                "request_id": request_id,
                "connection_id": self.handler.connection_id,
            })
            
            # Wait for user response (with timeout)
            try:
                permission_response = await asyncio.wait_for(permission_waiter, timeout=60.0)
                return permission_response and permission_response.get("allowed") == True
            except asyncio.TimeoutError:
                # Send timeout notification to frontend
                await self.handler._safe_write_message({
                    "type": "shell_permission_timeout",
                    "request_id": request_id,
                    "command": command,
                    "connection_id": self.handler.connection_id,
                })
                return False
        finally:
            # Restore original waiter
            self.handler.waiter = original_waiter 