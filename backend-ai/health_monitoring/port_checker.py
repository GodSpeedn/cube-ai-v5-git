"""
Port availability and network connectivity utilities.
"""
import socket
import asyncio
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class PortChecker:
    """Utility class for checking port availability and connectivity."""
    
    @staticmethod
    def is_port_available(port: int, host: str = "localhost") -> bool:
        """Check if a port is available (not in use)."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result != 0  # Port is available if connection fails
        except Exception as e:
            logger.debug(f"Error checking port {port} availability: {str(e)}")
            return False
    
    @staticmethod
    def is_port_open(port: int, host: str = "localhost", timeout: float = 5.0) -> bool:
        """Check if a port is open and accepting connections."""
        # Try IPv4 first
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                if result == 0:
                    return True
        except Exception as e:
            logger.debug(f"Error checking port {port} connectivity (IPv4): {str(e)}")
        
        # Try IPv6 if IPv4 failed
        try:
            with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex(("::1", port))
                if result == 0:
                    return True
        except Exception as e:
            logger.debug(f"Error checking port {port} connectivity (IPv6): {str(e)}")
        
        return False
    
    @staticmethod
    async def wait_for_port(port: int, host: str = "localhost", 
                           timeout: float = 30.0, check_interval: float = 1.0) -> bool:
        """Wait for a port to become available (accepting connections)."""
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            if PortChecker.is_port_open(port, host, timeout=1.0):
                return True
            await asyncio.sleep(check_interval)
        
        return False
    
    @staticmethod
    def find_available_port(start_port: int = 8000, end_port: int = 9000, 
                           host: str = "localhost") -> Optional[int]:
        """Find an available port in the given range."""
        for port in range(start_port, end_port + 1):
            if PortChecker.is_port_available(port, host):
                return port
        return None
    
    @staticmethod
    def get_port_info(port: int, host: str = "localhost") -> Tuple[bool, Optional[str]]:
        """Get detailed information about a port."""
        try:
            # Check if port is open
            is_open = PortChecker.is_port_open(port, host, timeout=2.0)
            
            if is_open:
                return True, "Port is open and accepting connections"
            else:
                return False, "Port is not accepting connections"
                
        except Exception as e:
            return False, f"Error checking port: {str(e)}"