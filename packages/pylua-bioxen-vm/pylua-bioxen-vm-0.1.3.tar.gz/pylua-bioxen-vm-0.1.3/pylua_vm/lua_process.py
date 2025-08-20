"""
Core Lua process management for individual VM instances.
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Union, Dict, Any
from .exceptions import (
    LuaProcessError, 
    LuaNotFoundError, 
    ScriptGenerationError
)
from .interactive_session import InteractiveSession


class LuaProcess:
    """
    Manages a single Lua interpreter subprocess.
    
    This class handles the execution of Lua code through subprocess calls,
    supporting both string execution and script file execution.
    """
    
    def __init__(self, name: str = "LuaVM", lua_executable: str = "lua"):
        """
        Initialize a Lua process manager.
        
        Args:
            name: Human-readable name for this VM instance
            lua_executable: Path to Lua interpreter (default: "lua")
        """
        self.name = name
        self.lua_executable = lua_executable
        self._temp_scripts = []  # Track temporary script files for cleanup
        self._interactive_session: Optional[InteractiveSession] = None
        
        # Verify Lua is available
        self._verify_lua_available()
    # --- Interactive Session Methods ---
    def start_interactive_session(self):
        """Start a persistent interactive Lua interpreter session."""
        if self._interactive_session and self._interactive_session.is_running():
            raise LuaProcessError("Interactive session already running")
        self._interactive_session = InteractiveSession(lua_executable=self.lua_executable, name=self.name)
        self._interactive_session.start()

    def stop_interactive_session(self):
        """Stop the interactive Lua interpreter session."""
        if self._interactive_session:
            self._interactive_session.stop()
            self._interactive_session = None

    def send_input(self, input_str: str):
        """Send input to the interactive Lua interpreter session."""
        if not self._interactive_session or not self._interactive_session.is_running():
            raise LuaProcessError("Interactive session not running")
        self._interactive_session.send_input(input_str)

    def read_output(self, timeout: float = 0.1) -> Optional[str]:
        """Read output from the interactive Lua interpreter session."""
        if not self._interactive_session or not self._interactive_session.is_running():
            raise LuaProcessError("Interactive session not running")
        return self._interactive_session.read_output(timeout=timeout)

    def is_interactive_running(self) -> bool:
        """Check if the interactive session is running."""
        return self._interactive_session is not None and self._interactive_session.is_running()
    
    def _verify_lua_available(self) -> None:
        """Check if Lua interpreter is available in PATH."""
        try:
            result = subprocess.run(
                [self.lua_executable, "-v"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode != 0:
                raise LuaNotFoundError(f"Lua interpreter check failed: {result.stderr}")
        except FileNotFoundError:
            raise LuaNotFoundError(f"Lua executable '{self.lua_executable}' not found in PATH")
        except subprocess.TimeoutExpired:
            raise LuaNotFoundError(f"Lua executable '{self.lua_executable}' did not respond")
    
    def execute_string(self, lua_code: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute a Lua code string.
        
        Args:
            lua_code: Lua code to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Dict with keys: 'stdout', 'stderr', 'return_code', 'success'
        """
        if not lua_code.strip():
            raise ValueError("Lua code cannot be empty")
        
        command = [self.lua_executable, "-e", lua_code]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout
            )
            return {
                'stdout': result.stdout.strip() if result.stdout else "",
                'stderr': result.stderr.strip() if result.stderr else "",
                'return_code': result.returncode,
                'success': result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            raise LuaProcessError(f"Lua execution timed out after {timeout} seconds")
        except Exception as e:
            raise LuaProcessError(f"Failed to execute Lua code: {e}")
    
    def execute_file(self, script_path: Union[str, Path], timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute a Lua script file.
        
        Args:
            script_path: Path to Lua script file
            timeout: Maximum execution time in seconds
            
        Returns:
            Dict with keys: 'stdout', 'stderr', 'return_code', 'success'
        """
        script_path = Path(script_path)
        
        if not script_path.exists():
            raise FileNotFoundError(f"Lua script not found: {script_path}")
        
        if not script_path.is_file():
            raise ValueError(f"Path is not a file: {script_path}")
        
        command = [self.lua_executable, str(script_path)]
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout
            )
            
            return {
                'stdout': result.stdout.strip() if result.stdout else "",
                'stderr': result.stderr.strip() if result.stderr else "",
                'return_code': result.returncode,
                'success': result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            raise LuaProcessError(f"Lua script execution timed out after {timeout} seconds")
        except Exception as e:
            raise LuaProcessError(f"Failed to execute Lua script: {e}")
    
    def execute_temp_script(self, lua_code: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Create a temporary Lua script and execute it.
        
        Useful for complex multi-line Lua code that's easier to manage as a file.
        
        Args:
            lua_code: Lua code to write to temporary script
            timeout: Maximum execution time in seconds
            
        Returns:
            Dict with keys: 'stdout', 'stderr', 'return_code', 'success'
        """
        try:
            # Create temporary script file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.lua',
                delete=False,
                encoding='utf-8'
            ) as temp_file:
                temp_file.write(lua_code)
                temp_script_path = Path(temp_file.name)
            
            # Track for cleanup
            self._temp_scripts.append(temp_script_path)
            
            # Execute the temporary script
            result = self.execute_file(temp_script_path, timeout=timeout)
            
            # Clean up immediately after execution
            self._cleanup_temp_script(temp_script_path)
            
            return result
            
        except Exception as e:
            raise ScriptGenerationError(f"Failed to create/execute temporary script: {e}")
    
    def _cleanup_temp_script(self, script_path: Path) -> None:
        """Clean up a specific temporary script file."""
        try:
            if script_path.exists():
                script_path.unlink()
            if script_path in self._temp_scripts:
                self._temp_scripts.remove(script_path)
        except Exception as e:
            print(f"Warning: Could not remove temporary script {script_path}: {e}", file=sys.stderr)
    
    def cleanup(self) -> None:
        """Clean up all temporary script files."""
        for script_path in self._temp_scripts[:]:  # Copy list to avoid modification during iteration
            self._cleanup_temp_script(script_path)
        if self._interactive_session:
            self._interactive_session.stop()
            self._interactive_session = None
    
    def __del__(self):
        """Ensure cleanup on object destruction."""
        self.cleanup()
    
    def __repr__(self):
        return f"LuaProcess(name='{self.name}', lua_executable='{self.lua_executable}')"