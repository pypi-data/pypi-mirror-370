import subprocess
import shlex
import os
from typing import Dict, Any


class ShellExecutor:
    """
    Handles shell command execution with safety checks and permission management.
    This module contains all shell-related business logic.
    """
    
    # Dangerous command patterns that require user permission
    DANGEROUS_PATTERNS = [
        'rm -rf', 'rm -r', 'rmdir', 'del', 'format', 'fdisk',
        'mkfs', 'dd if=', 'dd of=', '> /dev/', 'shutdown', 'reboot',
        'halt', 'poweroff', 'init 0', 'init 6', 'kill -9', 'killall',
        'chmod 777', 'chmod -R 777', 'chown -R', 'passwd', 'su -',
        'sudo su', 'sudo rm', 'sudo chmod', 'sudo chown', '&&', '||',
        ';', '|', '>', '>>', '<', 'curl', 'wget', 'nc ', 'netcat',
        'python -c', 'python3 -c', 'eval', 'exec', 'import os'
    ]
    
    # Safe commands that are allowed without permission
    SAFE_COMMANDS = [
        'ls', 'dir', 'pwd', 'whoami', 'id', 'date', 'uptime', 'uname',
        'df', 'du', 'free', 'ps', 'top', 'htop', 'which', 'where',
        'cat', 'head', 'tail', 'wc', 'grep', 'find', 'locate',
        'echo', 'env', 'printenv', 'history', 'file', 'stat',
        'mount', 'lsblk', 'lscpu', 'lsmem', 'lsusb', 'lspci',
        'ifconfig', 'ip', 'netstat', 'ss', 'ping', 'traceroute',
        'git status', 'git log', 'git branch', 'git diff',
        'npm list', 'pip list', 'pip show', 'conda list',
        'docker ps', 'docker images', 'kubectl get', 'pip', 'pip install', 'streamlit', 'streamlit run', 'chmod'
    ]
    
    def __init__(self, permission_handler=None):
        """
        Initialize shell executor.
        
        Args:
            permission_handler: Handler for requesting user permissions for dangerous commands
        """
        self.permission_handler = permission_handler
    
    def analyze_command_safety(self, command: str) -> Dict[str, Any]:
        """
        Analyze command safety and return analysis results.
        
        Returns:
            Dict with keys: is_dangerous, dangerous_pattern, is_safe_command
        """
        command_lower = command.lower().strip()
        
        # Check for dangerous patterns
        dangerous_pattern = None
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern in command_lower:
                dangerous_pattern = pattern
                break
        
        is_dangerous = dangerous_pattern is not None
        
        # Check if it's a safe command (for non-dangerous commands)
        is_safe_command = False
        if not is_dangerous:
            is_safe_command = self._is_safe_command(command_lower)
        
        return {
            "is_dangerous": is_dangerous,
            "dangerous_pattern": dangerous_pattern,
            "is_safe_command": is_safe_command
        }
    
    def _is_safe_command(self, command_lower: str) -> bool:
        """Check if a command is in the safe commands list."""
        try:
            command_parts = shlex.split(command_lower)
            if not command_parts:
                return False
            
            base_command = command_parts[0]
            
            # Allow git, npm, pip, conda, docker, kubectl with subcommands
            if base_command in ['git', 'npm', 'pip', 'conda', 'docker', 'kubectl']:
                if len(command_parts) < 2:
                    return False
                full_command = f"{base_command} {command_parts[1]}"
                return any(cmd.startswith(base_command) and cmd == full_command 
                          for cmd in self.SAFE_COMMANDS)
            else:
                return any(cmd.split()[0] == base_command for cmd in self.SAFE_COMMANDS)
        except Exception:
            return False
    
    async def execute_command(self, command: str) -> str:
        """
        Execute a shell command with safety checks.
        
        Args:
            command: Shell command to execute
            
        Returns:
            Command output or error message
        """
        # Analyze command safety
        safety_analysis = self.analyze_command_safety(command)
        
        # Handle dangerous commands
        if safety_analysis["is_dangerous"]:
            if not self.permission_handler:
                return f"Command contains dangerous pattern '{safety_analysis['dangerous_pattern']}' and no permission handler is available."
            
            # Request permission
            permission_granted = await self.permission_handler.request_permission(
                command, safety_analysis["dangerous_pattern"]
            )
            
            if not permission_granted:
                return f"Command execution cancelled by user. Command was: {command}"
        
        # Handle non-dangerous commands that aren't in safe list
        elif not safety_analysis["is_safe_command"]:
            command_parts = shlex.split(command.lower()) if command else []
            base_command = command_parts[0] if command_parts else "unknown"
            return f"Error: Command '{base_command}' is not in the allowed commands list"
        
        # Execute the command
        return await self._execute_safe_command(command)
    
    async def _execute_safe_command(self, command: str) -> str:
        """Execute a command that has passed safety checks."""
        try:
            print(f"[SHELL] Executing command: {command}")
            
            # Execute the command with timeout and capture output
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=90,  # 30 second timeout
                cwd=os.getcwd()  # Run in current working directory
            )
            
            # Combine stdout and stderr
            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}"
            if result.stderr:
                if output:
                    output += f"\n\nSTDERR:\n{result.stderr}"
                else:
                    output += f"STDERR:\n{result.stderr}"
            
            if result.returncode != 0:
                output += f"\n\nReturn code: {result.returncode}"
            
            if not output.strip():
                output = "Command executed successfully (no output)"
            
            print(f"[SHELL] Command completed with return code: {result.returncode}")
            return output
            
        except subprocess.TimeoutExpired:
            print(f"[SHELL] Command timed out: {command}")
            return f"Error: Command timed out after 30 seconds"
        except subprocess.CalledProcessError as e:
            print(f"[SHELL] Command failed: {e}")
            return f"Error: Command failed with return code {e.returncode}\nSTDERR: {e.stderr}"
        except Exception as e:
            print(f"[SHELL] Unexpected error: {e}")
            return f"Error: Unexpected error occurred: {str(e)}"


class PermissionHandler:
    """Interface for handling permission requests for dangerous commands."""
    
    async def request_permission(self, command: str, dangerous_pattern: str) -> bool:
        """
        Request user permission for a dangerous command.
        
        Args:
            command: The command to execute
            dangerous_pattern: The dangerous pattern detected
            
        Returns:
            True if permission granted, False otherwise
        """
        raise NotImplementedError 