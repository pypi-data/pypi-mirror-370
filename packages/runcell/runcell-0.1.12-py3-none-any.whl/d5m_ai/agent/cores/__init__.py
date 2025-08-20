"""
Core AI agent functionality.

This module contains all AI-related features including:
- Agent creation and management
- Tool execution interfaces
- Shell command execution with safety checks
- Event handling for streaming responses
"""

import os
import sys
from pathlib import Path

# Environment-based module loading (same pattern as chat and edit handlers)
D5M_ENV = os.environ.get("D5M_ENV", "production")

from .agent_core import AgentEventHandler, ToolExecutor
from .shell_executor import ShellExecutor, PermissionHandler

__all__ = [
    'AgentCore',
    'AgentEventHandler', 
    'ToolExecutor',
    'ShellExecutor',
    'PermissionHandler'
]
