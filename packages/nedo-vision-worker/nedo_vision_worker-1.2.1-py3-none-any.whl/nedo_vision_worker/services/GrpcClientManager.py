import logging
import threading
from typing import Dict, Type, Optional
from .GrpcClientBase import GrpcClientBase

logger = logging.getLogger(__name__)

class GrpcClientManager:
    """
    Centralized gRPC client manager that reuses connections and provides singleton access to clients.
    This optimizes resource usage by sharing connections among multiple workers.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(GrpcClientManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the client manager."""
        if not hasattr(self, '_initialized'):
            self._clients: Dict[str, GrpcClientBase] = {}
            self._clients_lock = threading.RLock()
            self._server_host = None
            self._server_port = 50051
            self._initialized = True
    
    def configure(self, server_host: str, server_port: int = 50051):
        """
        Configure the manager with server connection details.
        
        Args:
            server_host (str): The gRPC server host
            server_port (int): The gRPC server port
        """
        with self._clients_lock:
            self._server_host = server_host
            self._server_port = server_port
            logger.info(f"🔧 [GrpcClientManager] Configured for server: {server_host}:{server_port}")
    
    def get_client(self, client_class: Type[GrpcClientBase], client_key: Optional[str] = None) -> GrpcClientBase:
        """
        Get a shared client instance, creating it if it doesn't exist.
        
        Args:
            client_class: The client class to instantiate
            client_key: Optional unique key for the client (defaults to class name)
            
        Returns:
            GrpcClientBase: The shared client instance
        """
        if not self._server_host:
            raise ValueError("GrpcClientManager not configured. Call configure() first.")
        
        key = client_key or client_class.__name__
        
        with self._clients_lock:
            if key not in self._clients:
                logger.info(f"🚀 [GrpcClientManager] Creating new shared client: {key}")
                client = client_class(self._server_host, self._server_port)
                self._clients[key] = client
            else:
                logger.debug(f"♻️ [GrpcClientManager] Reusing existing client: {key}")
            
            return self._clients[key]
    
    def close_client(self, client_key: str):
        """
        Close and remove a specific client.
        
        Args:
            client_key (str): The key of the client to close
        """
        with self._clients_lock:
            if client_key in self._clients:
                try:
                    self._clients[client_key].close()
                    logger.info(f"🔌 [GrpcClientManager] Closed client: {client_key}")
                except Exception as e:
                    logger.warning(f"⚠️ [GrpcClientManager] Error closing client {client_key}: {e}")
                finally:
                    del self._clients[client_key]
    
    def close_all_clients(self):
        """Close all managed clients."""
        with self._clients_lock:
            for key in list(self._clients.keys()):
                self.close_client(key)
            logger.info("🔌 [GrpcClientManager] All clients closed")
    
    def get_active_clients(self) -> Dict[str, str]:
        """
        Get information about active clients.
        
        Returns:
            Dict[str, str]: Dictionary mapping client keys to their class names
        """
        with self._clients_lock:
            return {key: client.__class__.__name__ for key, client in self._clients.items()}
    
    def reconnect_all_clients(self):
        """Reconnect all managed clients (useful after network issues)."""
        with self._clients_lock:
            reconnected = 0
            for key, client in self._clients.items():
                try:
                    if hasattr(client, 'connect') and hasattr(client, 'stub'):
                        # Get the stub class from the existing client
                        stub_class = type(client.stub)
                        client.connect(stub_class)
                        reconnected += 1
                        logger.info(f"🔄 [GrpcClientManager] Reconnected client: {key}")
                except Exception as e:
                    logger.warning(f"⚠️ [GrpcClientManager] Failed to reconnect client {key}: {e}")
            
            logger.info(f"🔄 [GrpcClientManager] Reconnected {reconnected}/{len(self._clients)} clients")
    
    @classmethod
    def get_instance(cls) -> 'GrpcClientManager':
        """Get the singleton instance."""
        return cls()
    
    @classmethod
    def get_shared_client(cls, client_class: Type[GrpcClientBase], client_key: Optional[str] = None) -> GrpcClientBase:
        """
        Convenience method to get a shared client without explicitly getting the manager instance.
        
        Args:
            client_class: The client class to instantiate
            client_key: Optional unique key for the client
            
        Returns:
            GrpcClientBase: The shared client instance
        """
        return cls.get_instance().get_client(client_class, client_key)
