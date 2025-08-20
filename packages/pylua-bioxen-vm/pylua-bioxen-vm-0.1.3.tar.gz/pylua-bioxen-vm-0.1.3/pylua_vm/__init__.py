"""
pylua-bioxen-vm: A Python library for orchestrating networked Lua virtual machines.
This library provides process-isolated Lua VMs managed from Python with built-in
networking capabilities using LuaSocket and full interactive terminal support.
Perfect for distributed computing, microservices, game servers, and sandboxed scripting.
"""

from .lua_process import LuaProcess
from .vm_manager import VMManager, VMCluster
from .interactive_session import InteractiveSession, SessionManager
from .networking import NetworkedLuaVM, LuaScriptTemplate, validate_port, validate_host
from .exceptions import (
    LuaVMError,
    LuaProcessError, 
    NetworkingError,
    LuaNotFoundError,
    LuaSocketNotFoundError,
    VMConnectionError,
    VMTimeoutError,
    ScriptGenerationError,
    InteractiveSessionError,
    AttachError,
    DetachError,
    PTYError,
    SessionNotFoundError,
    SessionAlreadyExistsError,
    SessionStateError,
    IOThreadError,
    ProcessRegistryError,
    VMManagerError
)

__version__ = "0.2.0"
__author__ = "pylua-bioxen-vm contributors"  
__email__ = ""
__description__ = "Process-isolated networked Lua VMs with interactive terminal support"
__url__ = "https://github.com/yourusername/pylua-bioxen-vm"

__all__ = [
    "LuaProcess",
    "NetworkedLuaVM", 
    "VMManager",
    "VMCluster",
    "InteractiveSession",
    "SessionManager",
    "LuaScriptTemplate",
    "validate_port",
    "validate_host",
    "LuaVMError",
    "LuaProcessError",
    "NetworkingError", 
    "LuaNotFoundError",
    "LuaSocketNotFoundError",
    "VMConnectionError",
    "VMTimeoutError",
    "ScriptGenerationError",
    "InteractiveSessionError",
    "AttachError", 
    "DetachError",
    "PTYError",
    "SessionNotFoundError",
    "SessionAlreadyExistsError",
    "SessionStateError",
    "IOThreadError",
    "ProcessRegistryError",
    "VMManagerError",
    "__version__",
    "create_vm",
    "create_manager",
    "create_interactive_manager",
    "create_interactive_session"
]


# Convenience function for quick VM creation
def create_vm(vm_id: str = "default", networked: bool = False, lua_executable: str = "lua") -> LuaProcess:
    if networked:
        return NetworkedLuaVM(name=vm_id, lua_executable=lua_executable)
    else:
        return LuaProcess(name=vm_id, lua_executable=lua_executable)

def create_manager(max_workers: int = 10, lua_executable: str = "lua") -> VMManager:
    return VMManager(max_workers=max_workers, lua_executable=lua_executable)

def create_interactive_manager(max_workers: int = 10, lua_executable: str = "lua") -> VMManager:
    return VMManager(max_workers=max_workers, lua_executable=lua_executable)

def create_interactive_session(vm_id: str = "interactive", networked: bool = False, 
                             lua_executable: str = "lua", auto_attach: bool = True) -> InteractiveSession:
    manager = VMManager(lua_executable=lua_executable)
    return manager.create_interactive_vm(vm_id, networked=networked, auto_attach=auto_attach)