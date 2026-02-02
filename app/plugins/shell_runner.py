import subprocess
import shlex
import platform
import os

class ShellRunnerPlugin:
    """Plugin for running safe shell commands with Windows support"""
    
    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self._setup_whitelist()
    
    def _setup_whitelist(self):
        """Setup platform-specific whitelisted commands"""
        if self.is_windows:
            self.whitelisted_commands = {
                'dir', 'cd', 'echo', 'type', 'find', 'findstr', 
                'where', 'tree', 'mkdir', 'rmdir', 'copy', 'move',
                'whoami', 'hostname', 'systeminfo', 'tasklist',
                'python', 'python3', 'pip', 'cls', 'date', 'time'
            }
        else:
            self.whitelisted_commands = {
                'ls', 'pwd', 'whoami', 'echo', 'date', 
                'find', 'grep', 'wc', 'head', 'tail', 'cat',
                'mkdir', 'cd', 'python', 'python3', 'pip'
            }
    
    def run_shell_command(self, command: str) -> dict:
        """Execute a shell command if it's whitelisted"""
        if not command or not command.strip():
            return {
                "success": False,
                "error": "No command provided",
                "output": None
            }
        
        # Parse command to get the base command
        base_command = command.split()[0] if command.split() else ""
        
        if not self.is_command_safe(command):
            return {
                "success": False,
                "error": f"Command '{base_command}' is not whitelisted for safety reasons.",
                "output": None,
                "whitelisted_commands": list(self.whitelisted_commands)
            }
        
        try:
            # Use appropriate shell based on platform
            shell_cmd = command
            
            # Auto-translate common Unix commands to Windows equivalents
            if self.is_windows:
                shell_cmd = self._translate_unix_to_windows(command)
            
            # Execute the command safely
            result = subprocess.run(
                shell_cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30,  # 30 second timeout
                cwd=".",  # Current directory
                encoding='utf-8',
                errors='ignore'
            )
            
            # Create friendly message based on command
            friendly_message = self._create_friendly_message(command, result)
            
            return {
                "success": True,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode,
                "command_executed": shell_cmd,
                "friendly_message": friendly_message,
                "platform": "Windows" if self.is_windows else "Unix"
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 30 seconds",
                "output": None,
                "friendly_message": "❌ Command took too long to execute"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing command: {str(e)}",
                "output": None,
                "friendly_message": f"❌ Failed to execute command: {str(e)}"
            }
    
    def _translate_unix_to_windows(self, command: str) -> str:
        """Translate common Unix commands to Windows equivalents"""
        command_lower = command.lower()
        
        translations = {
            'ls': 'dir',
            'pwd': 'echo %CD%',
            'cat': 'type',
            'grep': 'findstr',
            'rm ': 'del ',  # Note: space to avoid matching 'rmdir'
            'cp ': 'copy ',
            'mv ': 'move ',
        }
        
        translated_cmd = command
        for unix_cmd, win_cmd in translations.items():
            if command_lower.startswith(unix_cmd):
                translated_cmd = command_lower.replace(unix_cmd, win_cmd, 1)
                break
        
        return translated_cmd
    
    def _create_friendly_message(self, original_command: str, result: subprocess.CompletedProcess) -> str:
        """Create user-friendly message based on command and result"""
        base_command = original_command.split()[0] if original_command.split() else ""
        
        if result.returncode == 0:
            if base_command in ['ls', 'dir']:
                item_count = len([line for line in result.stdout.split('\n') if line.strip()])
                return f"📁 Found {item_count} items in current directory"
            elif base_command in ['pwd', 'cd']:
                return f"📂 Current directory: {result.stdout.strip()}"
            elif base_command in ['whoami', 'hostname']:
                return f"👤 {result.stdout.strip()}"
            else:
                output_preview = result.stdout[:100] + "..." if len(result.stdout) > 100 else result.stdout
                return f"✅ Command executed successfully\n{output_preview.strip()}"
        else:
            if "is not recognized" in result.stderr:
                return f"❌ Command '{base_command}' not found. Try 'dir' instead of 'ls' on Windows."
            else:
                return f"❌ Command failed: {result.stderr.strip() or 'Unknown error'}"
    
    def is_command_safe(self, command: str) -> bool:
        """Check if a command is in the whitelist"""
        if not command or not command.strip():
            return False
            
        base_command = command.split()[0] if command.split() else ""
        
        # Also check if it's a translatable Unix command on Windows
        if self.is_windows and base_command in ['ls', 'pwd', 'cat', 'grep']:
            return True
            
        return base_command in self.whitelisted_commands
    
    def get_available_commands(self) -> list:
        """Return list of available whitelisted commands"""
        commands = sorted(list(self.whitelisted_commands))
        
        # Add Unix commands that will be auto-translated on Windows
        if self.is_windows:
            commands.extend(['ls', 'pwd', 'cat', 'grep'])
        
        return sorted(set(commands))