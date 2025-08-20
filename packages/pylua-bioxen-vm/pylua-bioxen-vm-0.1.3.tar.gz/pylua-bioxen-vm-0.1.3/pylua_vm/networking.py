"""
Networking functionality for Lua VM socket communication.

This module provides templates and utilities for creating networked Lua VMs
that can communicate via sockets using LuaSocket.
"""

from typing import Optional, Dict, Any
from .lua_process import LuaProcess
from .exceptions import NetworkingError, VMConnectionError, LuaSocketNotFoundError


class NetworkedLuaVM(LuaProcess):
    """
    Lua VM with built-in networking capabilities using LuaSocket.
    
    Extends LuaProcess with methods for server, client, and P2P communication modes.
    """
    
    def __init__(self, name: str = "NetworkedLuaVM", lua_executable: str = "lua"):
        super().__init__(name, lua_executable)
        self._verify_luasocket()
    
    def _verify_luasocket(self) -> None:
        """Check if LuaSocket is available."""
        test_code = 'require("socket"); print("LuaSocket available")'
        result = self.execute_string(test_code, timeout=5)
        
        if not result['success'] or "LuaSocket available" not in result['stdout']:
            raise LuaSocketNotFoundError(
                "LuaSocket not found. Install with: luarocks install luasocket"
            )
    
    def start_server(self, port: int, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Start a Lua socket server that accepts one client connection.
        
        Args:
            port: Port number to bind to (1024-65535)
            timeout: Maximum execution time in seconds
            
        Returns:
            Execution result dict
        """
        if not (1024 <= port <= 65535):
            raise ValueError("Port must be between 1024 and 65535")
        
        server_code = f"""
        local socket = require("socket")
        local server = socket.bind("*", {port})
        if not server then
            io.stderr:write("Lua Server: Failed to bind to port {port}\\n")
            os.exit(1)
        end
        print("Lua Server: Listening on port {port}...")
        local client = server:accept()
        print("Lua Server: Client connected from " .. client:getpeername())
        client:send("Hello from Lua Server! What's your message?\\n")
        local data, err = client:receive()
        if data then
            print("Lua Server: Received from client: " .. data)
        else
            io.stderr:write("Lua Server: Error receiving data or client disconnected: " .. tostring(err) .. "\\n")
        end
        client:close()
        server:close()
        print("Lua Server: Connection closed.")
        """
        
        return self.execute_temp_script(server_code, timeout=timeout)
    
    def start_client(self, host: str, port: int, message: str = "Hello from Lua Client!", 
                    timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Start a Lua socket client that connects to a server.
        
        Args:
            host: Server hostname or IP address
            port: Server port number
            message: Message to send to server
            timeout: Maximum execution time in seconds
            
        Returns:
            Execution result dict
        """
        if not (1024 <= port <= 65535):
            raise ValueError("Port must be between 1024 and 65535")
        
        if not host.strip():
            raise ValueError("Host cannot be empty")
        
        # Escape the message for Lua string
        escaped_message = message.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        
        client_code = f"""
        local socket = require("socket")
        local client, err = socket.connect("{host}", {port})
        if not client then
            io.stderr:write("Lua Client: Failed to connect to {host}:{port}: " .. tostring(err) .. "\\n")
            os.exit(1)
        end
        print("Lua Client: Connected to server at {host}:{port}")
        local response, err_recv = client:receive()
        if response then
            print("Lua Client: Received from server: " .. response)
        else
            io.stderr:write("Lua Client: Error receiving initial message from server: " .. tostring(err_recv) .. "\\n")
        end
        client:send("{escaped_message}\\n")
        print("Lua Client: Sent message: '{escaped_message}'")
        client:close()
        print("Lua Client: Connection closed.")
        """
        
        return self.execute_temp_script(client_code, timeout=timeout)
    
    def start_p2p(self, local_port: int, peer_host: Optional[str] = None, 
                  peer_port: Optional[int] = None, run_duration: int = 30,
                  send_interval: int = 5, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Start a P2P Lua VM that both listens for connections and can connect to peers.
        
        Args:
            local_port: Port to listen on for incoming connections
            peer_host: Optional peer hostname/IP to connect to
            peer_port: Optional peer port to connect to
            run_duration: How long to run the P2P VM (seconds)
            send_interval: How often to send heartbeat messages (seconds)
            timeout: Maximum execution time in seconds
            
        Returns:
            Execution result dict
        """
        if not (1024 <= local_port <= 65535):
            raise ValueError("Local port must be between 1024 and 65535")
        
        if peer_port is not None and not (1024 <= peer_port <= 65535):
            raise ValueError("Peer port must be between 1024 and 65535")
        
        # Generate peer connection code if peer specified
        peer_connect_code = ""
        if peer_host and peer_port:
            peer_connect_code = f"""
            local peer_client, peer_err = socket.connect("{peer_host}", {peer_port})
            if peer_client then
                peer_client:settimeout(0.1) -- Non-blocking for peer client
                print("P2P VM: Connected to peer at {peer_host}:{peer_port}")
                table.insert(sockets_to_monitor, peer_client)
                peer_client:send("Hello from P2P VM on port {local_port}!\\n")
            else
                io.stderr:write("P2P VM: Failed to connect to peer {peer_host}:{peer_port}: " .. tostring(peer_err) .. "\\n")
            end
            """
        
        p2p_code = f"""
        local socket = require("socket")

        local local_port = {local_port}
        local server_socket = socket.bind("*", local_port)
        if not server_socket then
            io.stderr:write("P2P VM: Failed to bind to local port " .. local_port .. "\\n")
            os.exit(1)
        end
        server_socket:settimeout(0.1) -- Non-blocking for server socket
        print("P2P VM: Listening on local port " .. local_port .. "...")

        local sockets_to_monitor = {{server_socket}}
        local connected_peers = {{}} -- To store active client connections

        {peer_connect_code}

        local last_send_time = os.clock()
        local send_interval = {send_interval}

        local run_duration = {run_duration}
        local start_time = os.clock()

        while os.clock() - start_time < run_duration do
            local readable_sockets, writable_sockets, err = socket.select(sockets_to_monitor, nil, 0.1)

            if err then
                io.stderr:write("P2P VM: socket.select error: " .. tostring(err) .. "\\n")
                break
            end

            for i, sock in ipairs(readable_sockets) do
                if sock == server_socket then
                    -- New incoming connection (server role)
                    local new_client = server_socket:accept()
                    if new_client then
                        new_client:settimeout(0.1) -- Non-blocking for new client
                        local peer_ip, peer_port = new_client:getpeername()
                        print("P2P VM: Accepted connection from " .. peer_ip .. ":" .. peer_port)
                        table.insert(sockets_to_monitor, new_client)
                        connected_peers[new_client] = true
                        new_client:send("Welcome to P2P VM on port " .. local_port .. "!\\n")
                    else
                        io.stderr:write("P2P VM: Error accepting new client: " .. tostring(new_client) .. "\\n")
                    end
                else
                    -- Data from an existing connection
                    local data, recv_err, partial = sock:receive()
                    if data then
                        print("P2P VM: Received from " .. sock:getpeername() .. ": " .. data)
                    elseif recv_err == "timeout" then
                        -- No data, just a timeout, continue
                    else
                        -- Connection closed or error
                        print("P2P VM: Connection from " .. sock:getpeername() .. " closed or error: " .. tostring(recv_err))
                        sock:close()
                        -- Remove socket from monitoring list
                        for k, v in ipairs(sockets_to_monitor) do
                            if v == sock then
                                table.remove(sockets_to_monitor, k)
                                break
                            end
                        end
                        connected_peers[sock] = nil
                    end
                end
            end

            -- Send periodic messages to connected peers
            if os.clock() - last_send_time > send_interval then
                for sock in pairs(connected_peers) do
                    local success, send_err = sock:send("P2P VM " .. local_port .. ": Heartbeat at " .. os.clock() .. "\\n")
                    if not success then
                        io.stderr:write("P2P VM: Error sending to " .. sock:getpeername() .. ": " .. tostring(send_err) .. "\\n")
                    end
                end
                last_send_time = os.clock()
            end
        end

        print("P2P VM: Shutting down after " .. run_duration .. " seconds.")
        for sock in pairs(connected_peers) do
            sock:close()
        end
        server_socket:close()
        """
        
        return self.execute_temp_script(p2p_code, timeout=timeout)


def validate_port(port: int) -> None:
    """Validate that a port number is in the valid range."""
    if not (1024 <= port <= 65535):
        raise ValueError("Port must be between 1024 and 65535")


def validate_host(host: str) -> None:
    """Basic validation for host string."""
    if not host or not host.strip():
        raise ValueError("Host cannot be empty")


class LuaScriptTemplate:
    """
    Utility class for generating common Lua networking script patterns.
    """
    
    @staticmethod
    def simple_echo_server(port: int) -> str:
        """Generate a simple echo server script."""
        return f"""
        local socket = require("socket")
        local server = socket.bind("*", {port})
        server:listen(5)
        print("Echo server listening on port {port}")
        
        while true do
            local client = server:accept()
            local line, err = client:receive()
            if line then
                client:send("Echo: " .. line .. "\\n")
            end
            client:close()
        end
        """
    
    @staticmethod  
    def heartbeat_client(host: str, port: int, interval: int = 1, count: int = 10) -> str:
        """Generate a heartbeat client script."""
        return f"""
        local socket = require("socket")
        local client = socket.connect("{host}", {port})
        
        for i = 1, {count} do
            client:send("Heartbeat " .. i .. "\\n")
            local response = client:receive()
            print("Received: " .. (response or "nil"))
            socket.sleep({interval})
        end
        
        client:close()
        """