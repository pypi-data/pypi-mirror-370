"""
High-level VM manager for orchestrating multiple Lua VMs.

This module provides the main interface for creating, managing, and coordinating
multiple networked Lua VMs.
"""

import threading
import time
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, Future

from .lua_process import LuaProcess
from .networking import NetworkedLuaVM

"""
High-level VM manager for orchestrating multiple Lua VMs with interactive terminal support.
"""

import threading
import time
import fnmatch
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, Future

from .lua_process import LuaProcess
from .networking import NetworkedLuaVM
from .interactive_session import InteractiveSession, SessionManager
from .exceptions import (
    VMManagerError, 
    ProcessRegistryError,
    InteractiveSessionError,
    SessionNotFoundError,
    SessionAlreadyExistsError
)


class VMManager:
    """
    High-level manager for multiple Lua VMs.
    
    Handles creation, lifecycle management, and coordination of Lua VMs
    with support for both basic and networked VMs, plus full interactive
    terminal capabilities similar to a hypervisor.
    """
    
    def __init__(self, max_workers: int = 10, lua_executable: str = "lua"):
        """
        Initialize the VM manager.
        
        Args:
            max_workers: Maximum number of concurrent VM executions
            lua_executable: Path to Lua interpreter
        """
        self.max_workers = max_workers
        self.lua_executable = lua_executable
        
        # VM and execution tracking
        self.vms: Dict[str, LuaProcess] = {}
        self.futures: Dict[str, Future] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Interactive session management
        self.session_manager = SessionManager()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Process registry for persistent VMs
        self._persistent_vms: Dict[str, Dict[str, Any]] = {}

    # ==================== CORE VM MANAGEMENT ====================
    def create_vm(self, vm_id: str, networked: bool = False, persistent: bool = False) -> LuaProcess:
        """
        Create a new Lua VM.
        
        Args:
            vm_id: Unique identifier for the VM
            networked: Whether to create a networked VM with socket support
            persistent: Whether this VM should be registered for interactive sessions
        Returns:
            The created VM instance
        """
        if vm_id in self.vms:
            raise ValueError(f"VM with ID '{vm_id}' already exists")
        with self._lock:
            if networked:
                vm = NetworkedLuaVM(name=vm_id, lua_executable=self.lua_executable)
            else:
                vm = LuaProcess(name=vm_id, lua_executable=self.lua_executable)
            self.vms[vm_id] = vm
            # Register for interactive sessions if persistent
            if persistent:
                self._register_persistent_vm(vm_id, networked)
            return vm
    def get_vm(self, vm_id: str) -> Optional[LuaProcess]:
        """Get a VM by ID."""
        return self.vms.get(vm_id)
    def list_vms(self) -> List[str]:
        """Get list of all VM IDs."""
        return list(self.vms.keys())
    def remove_vm(self, vm_id: str) -> bool:
        """
        Remove a VM and clean up its resources.
        """
        with self._lock:
            # Detach any active interactive sessions
            try:
                self.detach_from_vm(vm_id)
            except:
                pass
            # Remove from session manager
            self.session_manager.remove_session(vm_id)
            # Remove from persistent registry
            self._persistent_vms.pop(vm_id, None)
            # Clean up VM
            vm = self.vms.pop(vm_id, None)
            if vm:
                vm.cleanup()
                # Cancel any running futures for this VM
                future = self.futures.pop(vm_id, None)
                if future and not future.done():
                    future.cancel()
                return True
            return False
    # ==================== PERSISTENT VM REGISTRY ====================
    def _register_persistent_vm(self, vm_id: str, networked: bool) -> None:
        """Register a VM in the persistent registry."""
        self._persistent_vms[vm_id] = {
            'created_at': time.time(),
            'networked': networked,
            'interactive_capable': True,
            'session_active': False
        }
    def list_persistent_vms(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all persistent VMs.
        """
        with self._lock:
            result = {}
            for vm_id, metadata in self._persistent_vms.items():
                session = self.session_manager.get_session(vm_id)
                result[vm_id] = {
                    **metadata,
                    'session_attached': session.is_attached() if session else False,
                    'process_running': session.is_running() if session else False,
                    'vm_exists': vm_id in self.vms
                }
            return result
    def get_vm_info(self, vm_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific VM.
        """
        if vm_id not in self.vms:
            return None
        vm = self.vms[vm_id]
        session = self.session_manager.get_session(vm_id)
        persistent_info = self._persistent_vms.get(vm_id, {})
        return {
            'vm_id': vm_id,
            'vm_name': vm.name,
            'vm_type': 'networked' if isinstance(vm, NetworkedLuaVM) else 'basic',
            'persistent': vm_id in self._persistent_vms,
            'session_exists': session is not None,
            'session_attached': session.is_attached() if session else False,
            'process_running': session.is_running() if session else False,
            'interactive_capable': vm_id in self._persistent_vms,
            **persistent_info
        }
    # ==================== INTERACTIVE SESSION MANAGEMENT ====================
    def attach_to_vm(self, vm_id: str, output_callback: Optional[Callable[[str], None]] = None) -> InteractiveSession:
        """
        Attach to a VM's interactive session (hypervisor-like interface).
        """
        vm = self.get_vm(vm_id)
        if not vm:
            raise SessionNotFoundError(f"VM '{vm_id}' not found")
        with self._lock:
            # Get or create session
            session = self.session_manager.get_session(vm_id)
            if not session:
                session = self.session_manager.create_session(vm_id, vm)
            # Attach to session
            session.attach(output_callback)
            # Update persistent registry
            if vm_id in self._persistent_vms:
                self._persistent_vms[vm_id]['session_active'] = True
            return session
    def detach_from_vm(self, vm_id: str) -> None:
        """
        Detach from a VM's interactive session (keeps VM running).
        """
        session = self.session_manager.get_session(vm_id)
        if session:
            session.detach()
            # Update persistent registry
            if vm_id in self._persistent_vms:
                self._persistent_vms[vm_id]['session_active'] = False
    def send_input(self, vm_id: str, input_str: str) -> None:
        """
        Send input to a VM's interactive session.
        """
        session = self.session_manager.get_session(vm_id)
        if not session:
            raise SessionNotFoundError(f"No interactive session for VM '{vm_id}'")
        session.send_command(input_str)
    def read_output(self, vm_id: str, timeout: Optional[float] = 0.1) -> str:
        """
        Read output from a VM's interactive session.
        """
        session = self.session_manager.get_session(vm_id)
        if not session:
            raise SessionNotFoundError(f"No interactive session for VM '{vm_id}'")
        return session.read_output(timeout=timeout)
    def execute_interactive_command(self, vm_id: str, command: str, timeout: float = 5.0) -> str:
        """
        Execute a command in an interactive session and wait for output.
        """
        session = self.session_manager.get_session(vm_id)
        if not session:
            raise SessionNotFoundError(f"No interactive session for VM '{vm_id}'")
        return session.execute_and_wait(command, timeout=timeout)
    def list_interactive_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        List all active interactive sessions.
        """
        return self.session_manager.list_sessions()
    def terminate_vm_session(self, vm_id: str) -> None:
        """
        Terminate a VM's interactive session and stop the process.
        """
        session = self.session_manager.get_session(vm_id)
        if session:
            session.terminate()
            self.session_manager.remove_session(vm_id)
            # Update persistent registry
            if vm_id in self._persistent_vms:
                self._persistent_vms[vm_id]['session_active'] = False
    # ==================== HYPERVISOR-LIKE OPERATIONS ====================
    def create_interactive_vm(self, vm_id: str, networked: bool = False, auto_attach: bool = True) -> InteractiveSession:
        """
        Create a VM specifically for interactive use (hypervisor-like).
        """
        # Create VM as persistent
        vm = self.create_vm(vm_id, networked=networked, persistent=True)
        if auto_attach:
            return self.attach_to_vm(vm_id)
        else:
            # Create session but don't attach
            return self.session_manager.create_session(vm_id, vm)
    def clone_vm_session(self, source_vm_id: str, target_vm_id: str) -> InteractiveSession:
        """
        Clone a VM's configuration to create a new interactive session.
        """
        source_vm = self.get_vm(source_vm_id)
        if not source_vm:
            raise SessionNotFoundError(f"Source VM '{source_vm_id}' not found")
        # Determine if source is networked
        networked = isinstance(source_vm, NetworkedLuaVM)
        return self.create_interactive_vm(target_vm_id, networked=networked, auto_attach=True)
    def bulk_create_interactive_cluster(self, cluster_id: str, vm_count: int, 
                                      networked: bool = True) -> Dict[str, InteractiveSession]:
        """
        Create a cluster of interactive VMs.
        """
        sessions = {}
        for i in range(vm_count):
            vm_id = f"{cluster_id}_{i:03d}"
            session = self.create_interactive_vm(vm_id, networked=networked, auto_attach=False)
            sessions[vm_id] = session
        return sessions
    def broadcast_to_interactive_sessions(self, vm_pattern: str, command: str) -> Dict[str, str]:
        """
        Broadcast a command to all interactive sessions matching a pattern.
        """
        matching_sessions = {}
        all_sessions = self.session_manager.list_sessions()
        for vm_id in all_sessions:
            if fnmatch.fnmatch(vm_id, vm_pattern):
                session = self.session_manager.get_session(vm_id)
                if session and session.is_attached():
                    matching_sessions[vm_id] = session
        if not matching_sessions:
            raise ValueError(f"No attached sessions found matching pattern: {vm_pattern}")
        results = {}
        for vm_id, session in matching_sessions.items():
            try:
                output = session.execute_and_wait(command, timeout=5.0)
                results[vm_id] = output
            except Exception as e:
                results[vm_id] = f"Error: {e}"
        return results
    # ==================== BACKWARD COMPATIBLE METHODS ====================
    def execute_vm_async(self, vm_id: str, lua_code: str, 
                        timeout: Optional[float] = None) -> Future:
        """
        Execute Lua code on a VM asynchronously (backward compatible).
        """
        vm = self.get_vm(vm_id)
        if not vm:
            raise ValueError(f"VM '{vm_id}' not found")
        def execute():
            return vm.execute_string(lua_code, timeout=timeout)
        future = self.executor.submit(execute)
        self.futures[vm_id] = future
        return future
    def execute_vm_sync(self, vm_id: str, lua_code: str, 
                       timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute Lua code on a VM synchronously (backward compatible).
        """
        vm = self.get_vm(vm_id)
        if not vm:
            raise ValueError(f"VM '{vm_id}' not found")
        return vm.execute_string(lua_code, timeout=timeout)
    def start_server_vm(self, vm_id: str, port: int, 
                       timeout: Optional[float] = None) -> Future:
        """Start a VM as a socket server asynchronously."""
        vm = self.get_vm(vm_id)
        if not vm or not isinstance(vm, NetworkedLuaVM):
            raise ValueError(f"Networked VM '{vm_id}' not found")
        def start_server():
            return vm.start_server(port, timeout=timeout)
        future = self.executor.submit(start_server)
        self.futures[vm_id] = future
        return future
    def start_client_vm(self, vm_id: str, host: str, port: int, 
                       message: str = "Hello from client!", 
                       timeout: Optional[float] = None) -> Future:
        """Start a VM as a socket client asynchronously."""
        vm = self.get_vm(vm_id)
        if not vm or not isinstance(vm, NetworkedLuaVM):
            raise ValueError(f"Networked VM '{vm_id}' not found")
        def start_client():
            return vm.start_client(host, port, message, timeout=timeout)
        future = self.executor.submit(start_client)
        self.futures[vm_id] = future
        return future
    def start_p2p_vm(self, vm_id: str, local_port: int,
                     peer_host: Optional[str] = None, peer_port: Optional[int] = None,
                     run_duration: int = 30, timeout: Optional[float] = None) -> Future:
        """Start a VM in P2P mode asynchronously."""
        vm = self.get_vm(vm_id)
        if not vm or not isinstance(vm, NetworkedLuaVM):
            raise ValueError(f"Networked VM '{vm_id}' not found")
        def start_p2p():
            return vm.start_p2p(local_port, peer_host, peer_port, run_duration, timeout=timeout)
        future = self.executor.submit(start_p2p)
        self.futures[vm_id] = future
        return future
    # ==================== UTILITY AND MANAGEMENT METHODS ====================
    def wait_for_vm(self, vm_id: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Wait for an asynchronous VM operation to complete."""
        future = self.futures.get(vm_id)
        if not future:
            raise ValueError(f"No running operation found for VM '{vm_id}'")
        return future.result(timeout=timeout)
    def cancel_vm(self, vm_id: str) -> bool:
        """Cancel a running VM operation."""
        future = self.futures.get(vm_id)
        if future and not future.done():
            return future.cancel()
        return False
    def get_vm_status(self, vm_id: str) -> Optional[str]:
        """Get the status of a VM's current operation."""
        future = self.futures.get(vm_id)
        if not future:
            return None
        if future.cancelled():
            return 'cancelled'
        elif future.done():
            return 'done'
        else:
            return 'running'
    def create_vm_cluster(self, cluster_id: str, vm_count: int, 
                         networked: bool = True) -> List[str]:
        """Create a cluster of VMs with consistent naming."""
        vm_ids = []
        for i in range(vm_count):
            vm_id = f"{cluster_id}_{i:03d}"
            self.create_vm(vm_id, networked=networked)
            vm_ids.append(vm_id)
        return vm_ids
    def setup_p2p_cluster(self, cluster_id: str, vm_count: int, 
                         base_port: int = 8080, run_duration: int = 60) -> List[Future]:
        """Set up a P2P cluster where each VM connects to the next one in a ring."""
        if vm_count < 2:
            raise ValueError("P2P cluster requires at least 2 VMs")
        # Create VMs if they don't exist
        vm_ids = []
        for i in range(vm_count):
            vm_id = f"{cluster_id}_{i:03d}"
            if vm_id not in self.vms:
                self.create_vm(vm_id, networked=True)
            vm_ids.append(vm_id)
        # Start P2P VMs in a ring topology
        futures = []
        for i, vm_id in enumerate(vm_ids):
            local_port = base_port + i
            # Connect to the next VM in the ring
            next_i = (i + 1) % vm_count
            peer_port = base_port + next_i
            future = self.start_p2p_vm(
                vm_id, 
                local_port, 
                peer_host="localhost", 
                peer_port=peer_port,
                run_duration=run_duration
            )
            futures.append(future)
        return futures
    def broadcast_to_cluster(self, cluster_pattern: str, lua_code: str,
                           timeout: Optional[float] = None) -> Dict[str, Future]:
        """Broadcast Lua code execution to all VMs matching a pattern."""
        matching_vms = [vm_id for vm_id in self.vms.keys() 
                       if fnmatch.fnmatch(vm_id, cluster_pattern)]
        if not matching_vms:
            raise ValueError(f"No VMs found matching pattern: {cluster_pattern}")
        futures = {}
        for vm_id in matching_vms:
            future = self.execute_vm_async(vm_id, lua_code, timeout=timeout)
            futures[vm_id] = future
        return futures
    def wait_for_cluster(self, futures: Dict[str, Future], 
                        timeout: Optional[float] = None) -> Dict[str, Dict[str, Any]]:
        """Wait for multiple VM operations to complete."""
        results = {}
        for vm_id, future in futures.items():
            try:
                results[vm_id] = future.result(timeout=timeout)
            except Exception as e:
                results[vm_id] = {
                    'error': str(e),
                    'success': False,
                    'stdout': '',
                    'stderr': str(e),
                    'return_code': -1
                }
        return results
    def get_cluster_status(self, cluster_pattern: str) -> Dict[str, str]:
        """Get status of all VMs matching a pattern."""
        status = {}
        for vm_id in self.vms.keys():
            if fnmatch.fnmatch(vm_id, cluster_pattern):
                status[vm_id] = self.get_vm_status(vm_id) or 'idle'
        return status
    def cleanup_cluster(self, cluster_pattern: str) -> int:
        """Remove all VMs matching a pattern."""
        matching_vms = [vm_id for vm_id in self.vms.keys() 
                       if fnmatch.fnmatch(vm_id, cluster_pattern)]
        removed_count = 0
        for vm_id in matching_vms:
            if self.remove_vm(vm_id):
                removed_count += 1
        return removed_count
    def shutdown_all(self) -> None:
        """Shutdown all VMs and clean up resources."""
        # Cancel all running futures
        for future in self.futures.values():
            if not future.done():
                future.cancel()
        # Clean up all interactive sessions
        self.session_manager.cleanup_all()
        # Clean up all VMs
        for vm in self.vms.values():
            vm.cleanup()
        # Clear collections
        self.vms.clear()
        self.futures.clear()
        self._persistent_vms.clear()
        # Shutdown executor
        self.executor.shutdown(wait=True)
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the VM manager state."""
        running_count = sum(1 for status in [self.get_vm_status(vm_id) for vm_id in self.vms.keys()]
                          if status == 'running')
        networked_count = sum(1 for vm in self.vms.values() 
                            if isinstance(vm, NetworkedLuaVM))
        session_stats = self.session_manager.list_sessions()
        attached_sessions = sum(1 for info in session_stats.values() if info.get('attached', False))
        return {
            'total_vms': len(self.vms),
            'networked_vms': networked_count,
            'basic_vms': len(self.vms) - networked_count,
            'persistent_vms': len(self._persistent_vms),
            'interactive_sessions': len(session_stats),
            'attached_sessions': attached_sessions,
            'running_operations': running_count,
            'completed_operations': len([f for f in self.futures.values() if f.done()]),
            'max_workers': self.max_workers,
            'lua_executable': self.lua_executable
        }
    def __enter__(self):
        """Context manager entry."""
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.shutdown_all()
    def __repr__(self):
        return (f"VMManager(vms={len(self.vms)}, "
                f"interactive_sessions={len(self.session_manager.list_sessions())}, "
                f"max_workers={self.max_workers})")

# Keep the existing VMCluster class for backward compatibility
class VMCluster:
    """
    Helper class for managing a group of related VMs.
    
    Provides a higher-level interface for common cluster operations.
    """
    def __init__(self, manager: VMManager, cluster_id: str, vm_ids: List[str]):
        self.manager = manager
        self.cluster_id = cluster_id
        self.vm_ids = vm_ids
    def broadcast(self, lua_code: str, timeout: Optional[float] = None) -> Dict[str, Future]:
        """Broadcast code execution to all VMs in cluster."""
        futures = {}
        for vm_id in self.vm_ids:
            future = self.manager.execute_vm_async(vm_id, lua_code, timeout=timeout)
            futures[vm_id] = future
        return futures
    def wait_all(self, futures: Dict[str, Future], 
                timeout: Optional[float] = None) -> Dict[str, Dict[str, Any]]:
        """Wait for all cluster operations to complete."""
        return self.manager.wait_for_cluster(futures, timeout=timeout)
    def get_status(self) -> Dict[str, str]:
        """Get status of all VMs in cluster."""
        return {vm_id: self.manager.get_vm_status(vm_id) or 'idle' 
                for vm_id in self.vm_ids}
    def cleanup(self) -> int:
        """Remove all VMs in this cluster."""
        removed = 0
        for vm_id in self.vm_ids:
            if self.manager.remove_vm(vm_id):
                removed += 1
        return removed
    def __len__(self):
        return len(self.vm_ids)
    def __repr__(self):
        return f"VMCluster(id='{self.cluster_id}', vms={len(self.vm_ids)})"
        return futures
    
    def wait_all(self, futures: Dict[str, Future], 
                timeout: Optional[float] = None) -> Dict[str, Dict[str, Any]]:
        """Wait for all cluster operations to complete."""
        return self.manager.wait_for_cluster(futures, timeout=timeout)
    
    def get_status(self) -> Dict[str, str]:
        """Get status of all VMs in cluster."""
        return {vm_id: self.manager.get_vm_status(vm_id) or 'idle' 
                for vm_id in self.vm_ids}
    
    def cleanup(self) -> int:
        """Remove all VMs in this cluster."""
        removed = 0
        for vm_id in self.vm_ids:
            if self.manager.remove_vm(vm_id):
                removed += 1
        return removed
    
    def __len__(self):
        return len(self.vm_ids)
    
    def __repr__(self):
        return f"VMCluster(id='{self.cluster_id}', vms={len(self.vm_ids)})"