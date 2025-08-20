import os
import time
import logging
import threading
import platform
import tempfile
from pathlib import Path
from typing import Dict, Optional

# Platform-specific imports
if platform.system().lower() == "windows":
    import msvcrt
else:
    import fcntl


class SystemWideDeviceCoordinator:
    """
    System-wide device coordinator that works across multiple processes/services.
    Uses file locks to coordinate device access between different services.
    """
    
    def __init__(self, lock_dir: str = None):
        # Use platform-appropriate temporary directory if none specified
        if lock_dir is None:
            system_temp = tempfile.gettempdir()
            lock_dir = os.path.join(system_temp, "nedo-vision-device-locks")
        
        self.lock_dir = Path(lock_dir)
        self.lock_dir.mkdir(exist_ok=True)
        self.active_locks: Dict[int, any] = {}
        self.lock = threading.Lock()
        
        logging.info(f"SystemWideDeviceCoordinator initialized with lock directory: {self.lock_dir}")
    
    def acquire_device_lock(self, device_index: int, timeout: float = 5.0) -> bool:
        """
        Acquire exclusive lock for a video device across all services.
        
        Args:
            device_index: The video device index (e.g., 0 for /dev/video0)
            timeout: Maximum time to wait for lock acquisition
            
        Returns:
            True if lock acquired successfully, False otherwise
        """
        lock_file_path = self.lock_dir / f"video_device_{device_index}.lock"
        
        try:
            # Open lock file
            lock_file = open(lock_file_path, 'w')
            lock_file.write(f"pid:{os.getpid()}\nservice:worker-service\ntime:{time.time()}\n")
            lock_file.flush()
            
            # Platform-specific locking
            if platform.system().lower() == "windows":
                return self._acquire_lock_windows(lock_file, device_index, timeout)
            else:
                return self._acquire_lock_unix(lock_file, device_index, timeout)
                
        except Exception as e:
            logging.error(f"❌ Error acquiring device lock for device {device_index}: {e}")
            return False
    
    def _acquire_lock_unix(self, lock_file, device_index: int, timeout: float) -> bool:
        """Acquire lock using POSIX fcntl (Linux/macOS)."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                
                # Lock acquired successfully
                with self.lock:
                    self.active_locks[device_index] = lock_file
                
                logging.info(f"✅ Acquired system-wide lock for video device {device_index}")
                return True
                
            except BlockingIOError:
                # Lock is held by another process, wait and retry
                time.sleep(0.1)
                continue
        
        # Timeout reached
        lock_file.close()
        logging.warning(f"⏱️ Timeout acquiring lock for video device {device_index}")
        return False
    
    def _acquire_lock_windows(self, lock_file, device_index: int, timeout: float) -> bool:
        """Acquire lock using Windows msvcrt (Windows)."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Try to lock the file
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                
                # Lock acquired successfully
                with self.lock:
                    self.active_locks[device_index] = lock_file
                
                logging.info(f"✅ Acquired system-wide lock for video device {device_index}")
                return True
                
            except OSError:
                # Lock is held by another process, wait and retry
                time.sleep(0.1)
                continue
        
        # Timeout reached
        lock_file.close()
        logging.warning(f"⏱️ Timeout acquiring lock for video device {device_index}")
        return False
    
    def release_device_lock(self, device_index: int):
        """Release the lock for a video device."""
        with self.lock:
            if device_index in self.active_locks:
                try:
                    lock_file = self.active_locks[device_index]
                    
                    # Platform-specific unlocking
                    if platform.system().lower() == "windows":
                        msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                    else:
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                    
                    lock_file.close()
                    del self.active_locks[device_index]
                    
                    logging.info(f"🔓 Released system-wide lock for video device {device_index}")
                    
                except Exception as e:
                    logging.error(f"❌ Error releasing device lock for device {device_index}: {e}")
    
    def is_device_locked(self, device_index: int) -> bool:
        """Check if a device is currently locked by any service."""
        lock_file_path = self.lock_dir / f"video_device_{device_index}.lock"
        
        if not lock_file_path.exists():
            return False
        
        try:
            test_file = open(lock_file_path, 'r')
            
            # Platform-specific lock testing
            if platform.system().lower() == "windows":
                try:
                    msvcrt.locking(test_file.fileno(), msvcrt.LK_NBLCK, 1)
                    msvcrt.locking(test_file.fileno(), msvcrt.LK_UNLCK, 1)
                    test_file.close()
                    return False  # Lock is available
                except OSError:
                    test_file.close()
                    return True  # Lock is held by another process
            else:
                try:
                    fcntl.flock(test_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    fcntl.flock(test_file.fileno(), fcntl.LOCK_UN)
                    test_file.close()
                    return False  # Lock is available
                except BlockingIOError:
                    test_file.close()
                    return True  # Lock is held by another process
                    
        except Exception:
            return False  # Assume available on error
    
    def get_device_lock_info(self, device_index: int) -> Optional[Dict]:
        """Get information about who is holding the device lock."""
        lock_file_path = self.lock_dir / f"video_device_{device_index}.lock"
        
        if not lock_file_path.exists():
            return None
        
        try:
            with open(lock_file_path, 'r') as f:
                content = f.read().strip()
                info = {}
                for line in content.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        info[key] = value
                return info
        except Exception:
            return None
    
    def cleanup_stale_locks(self, max_age: float = 300.0):
        """Clean up stale lock files older than max_age seconds."""
        current_time = time.time()
        
        for lock_file_path in self.lock_dir.glob("video_device_*.lock"):
            try:
                # Check if lock file is stale
                if current_time - lock_file_path.stat().st_mtime > max_age:
                    # Try to acquire lock to see if it's really stale
                    try:
                        with open(lock_file_path, 'r') as f:
                            test_file = open(lock_file_path, 'r')
                            fcntl.flock(test_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                            fcntl.flock(test_file.fileno(), fcntl.LOCK_UN)
                            test_file.close()
                            
                            # Lock is available, remove stale file
                            lock_file_path.unlink()
                            logging.info(f"🧹 Cleaned up stale lock file: {lock_file_path}")
                            
                    except BlockingIOError:
                        # Lock is still active, keep it
                        pass
                        
            except Exception as e:
                logging.warning(f"⚠️ Error checking stale lock {lock_file_path}: {e}")
    
    def shutdown(self):
        """Release all locks and cleanup."""
        logging.info("🛑 Shutting down SystemWideDeviceCoordinator")
        
        with self.lock:
            for device_index in list(self.active_locks.keys()):
                self.release_device_lock(device_index)


# Global instance
_system_coordinator = None
_coordinator_lock = threading.Lock()

def get_system_coordinator() -> SystemWideDeviceCoordinator:
    """Get the global system-wide device coordinator instance."""
    global _system_coordinator
    
    if _system_coordinator is None:
        with _coordinator_lock:
            if _system_coordinator is None:
                _system_coordinator = SystemWideDeviceCoordinator()
    
    return _system_coordinator
