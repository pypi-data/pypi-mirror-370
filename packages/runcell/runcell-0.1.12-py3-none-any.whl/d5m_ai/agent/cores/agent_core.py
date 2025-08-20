from typing import Optional, Any

class AgentEventHandler:
    """Interface for handling agent events during streaming."""
    
    async def on_text_chunk(self, chunk: str, content_index: Optional[int] = None):
        """Handle text chunk from agent."""
        pass
    
    async def on_tool_call(self, tool_name: str, call_id: str, args: Any, content_index: int):
        """Handle tool call from agent."""
        pass
    
    async def on_tool_output(self, call_id: str, output: str, content_index: int):
        """Handle tool output from agent."""
        pass
    
    async def on_completion(self):
        """Handle completion of agent run."""
        pass
    
    async def on_max_turns_exceeded(self, message: str):
        """Handle max turns exceeded error."""
        pass
    
    async def on_error(self, error_message: str):
        """Handle general error."""
        pass


class ToolExecutor:
    """Interface for tool execution."""
    
    async def cell_execute(self, code: str) -> str:
        """Execute code in a cell."""
        raise NotImplementedError
    
    async def shell_execute(self, command: str) -> str:
        """Execute shell command."""
        raise NotImplementedError
    
    async def edit_cell(self, cell_index: int, code: str, rerun: bool = False) -> str:
        """Edit a cell."""
        raise NotImplementedError
    
    async def rerun_all_cells(self) -> str:
        """Rerun all cells."""
        raise NotImplementedError
    
    async def interpret_image(self, image_url: str) -> str:
        """Analyze and interpret an image."""
        raise NotImplementedError
    
    async def insert_markdown_cell(self, cell_index: int, content: str) -> str:
        """Insert a new markdown cell at the specified index in the notebook."""
        raise NotImplementedError
    
    async def read_file(self, file_path: str, start_row_index: int = 0, end_row_index: int = 200) -> str:
        """Read content from a file with optional row range specification."""
        raise NotImplementedError 