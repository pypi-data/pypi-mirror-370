import asyncio
import os
import subprocess
import shlex
import uuid


class ShellExecutor:
    def __init__(self):
        self.dangerous_patterns = [
            'rm -rf', 'rm -r', 'rmdir', 'del', 'format', 'fdisk',
            'mkfs', 'dd if=', 'dd of=', '> /dev/', 'shutdown', 'reboot',
            'halt', 'poweroff', 'init 0', 'init 6', 'kill -9', 'killall',
            'chmod 777', 'chmod -R 777', 'chown -R', 'passwd', 'su -',
            'sudo su', 'sudo rm', 'sudo chmod', 'sudo chown', '&&', '||',
            ';', '|', '>', '>>', '<', 'curl', 'wget', 'nc ', 'netcat',
            'python -c', 'python3 -c', 'eval', 'exec', 'import os'
        ]
        
        self.safe_commands = [
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

    def _is_dangerous_command(self, command):
        """Check if a command contains dangerous patterns."""
        command_lower = command.lower().strip()
        
        for pattern in self.dangerous_patterns:
            if pattern in command_lower:
                return True, pattern
        return False, None

    def _is_safe_command(self, command):
        """Check if a command is in the safe commands list."""
        command_parts = shlex.split(command.lower())
        if not command_parts:
            return False, "Empty command"
            
        base_command = command_parts[0]
        
        # Allow git, npm, pip, conda, docker, kubectl with subcommands
        if base_command in ['git', 'npm', 'pip', 'conda', 'docker', 'kubectl']:
            if len(command_parts) < 2:
                return False, f"{base_command} requires a subcommand"
            full_command = f"{base_command} {command_parts[1]}"
            if full_command not in [cmd for cmd in self.safe_commands if cmd.startswith(base_command)]:
                return False, f"{full_command} is not in the allowed commands list"
        elif base_command not in [cmd.split()[0] for cmd in self.safe_commands]:
            return False, f"Command '{base_command}' is not in the allowed commands list"
        
        return True, None

    async def request_permission(self, handler, command, dangerous_pattern):
        """Request user permission for dangerous commands."""
        request_id = str(uuid.uuid4())
        
        # Create a waiter for the permission response
        permission_waiter = asyncio.get_running_loop().create_future()
        
        # Store the waiter temporarily
        original_waiter = handler.waiter
        handler.waiter = permission_waiter
        
        try:
            # Send permission request to frontend
            await handler._safe_write_message({
                "type": "shell_permission_request",
                "command": command,
                "dangerous_pattern": dangerous_pattern,
                "request_id": request_id,
                "connection_id": handler.connection_id,
            })
            
            # Wait for user response (with timeout)
            try:
                permission_response = await asyncio.wait_for(permission_waiter, timeout=90.0)
                return permission_response and permission_response.get("allowed") == True
            except asyncio.TimeoutError:
                return False
        finally:
            # Restore original waiter
            handler.waiter = original_waiter

    async def execute_command(self, handler, command: str) -> str:
        """
        Execute shell commands directly on the server with security checks and user permission for dangerous commands.
        """
        # Safety check - identify potentially dangerous commands
        is_dangerous, dangerous_pattern = self._is_dangerous_command(command)
        
        # If dangerous command detected, ask for user confirmation
        if is_dangerous:
            permission_granted = await self.request_permission(handler, command, dangerous_pattern)
            if not permission_granted:
                return f"Command execution cancelled by user. Command was: {command}"
        
        # Additional safety: only allow specific safe commands (for non-dangerous commands)
        if not is_dangerous:
            is_safe, error_msg = self._is_safe_command(command)
            if not is_safe:
                return f"Error: {error_msg}"
        
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