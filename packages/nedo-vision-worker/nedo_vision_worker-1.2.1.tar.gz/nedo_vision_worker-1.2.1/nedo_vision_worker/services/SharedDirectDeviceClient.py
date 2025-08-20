import logging
import threading
import time
import cv2
import platform
import ffmpeg
from typing import Dict
from .SystemWideDeviceCoordinator import get_system_coordinator


class SharedDirectDeviceClient:
    """
    Client for accessing shared direct video devices.
    Coordinates with other services to prevent 'device busy' errors.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.active_devices: Dict[int, Dict] = {}  # device_index -> device_info
        self.device_locks: Dict[int, threading.Lock] = {}
        self.main_lock = threading.Lock()
        
        logging.info("SharedDirectDeviceClient initialized")
    
    def _is_direct_device(self, url) -> tuple:
        """Check if source is a direct video device and return device index."""
        if isinstance(url, int):
            return True, url
        elif isinstance(url, str) and url.isdigit():
            return True, int(url)
        elif isinstance(url, str) and url.startswith('/dev/video'):
            try:
                device_index = int(url.replace('/dev/video', ''))
                return True, device_index
            except ValueError:
                pass
        return False, None
    
    def _get_device_path(self, device_index: int) -> str:
        """Get the appropriate device path based on the platform."""
        system = platform.system().lower()
        
        if system == "linux":
            return f"/dev/video{device_index}"
        elif system == "windows":
            return f"video={device_index}"
        elif system == "darwin":
            return f"{device_index}"
        else:
            logging.warning(f"Unsupported platform: {system}, using default")
            return str(device_index)
    
    def get_video_properties(self, url) -> tuple:
        """
        Get video properties for a direct device using cv2 instead of ffmpeg probe.
        This is safer for device access coordination.
        """
        is_device, device_index = self._is_direct_device(url)
        
        if not is_device:
            logging.error(f"URL {url} is not a direct video device")
            return None, None, None, "rgb24"
        
        with self.main_lock:
            # Check if device is already being accessed locally
            if device_index in self.active_devices:
                device_info = self.active_devices[device_index]
                return (
                    device_info['width'],
                    device_info['height'], 
                    device_info['fps'],
                    device_info['pixel_format']
                )
        
        # Check if device is locked by another service
        coordinator = get_system_coordinator()
        if coordinator.is_device_locked(device_index):
            lock_info = coordinator.get_device_lock_info(device_index)
            service = lock_info.get('service', 'unknown') if lock_info else 'unknown'
            logging.warning(f"⚠️ Device {device_index} is locked by {service}. Cannot probe properties.")
            # Return default properties for locked devices
            return 640, 480, 30.0, "rgb24"
        
        # Probe the device safely
        try:
            cap = cv2.VideoCapture(device_index)
            
            if not cap.isOpened():
                logging.error(f"Failed to open direct video device: {device_index}")
                return None, None, None, "rgb24"
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = float(cap.get(cv2.CAP_PROP_FPS))
            
            if fps <= 0 or fps > 240:
                fps = 30.0
            
            cap.release()
            
            # Store device info for future use
            with self.main_lock:
                self.active_devices[device_index] = {
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'pixel_format': 'rgb24',
                    'access_count': 0,
                    'last_access': time.time()
                }
                self.device_locks[device_index] = threading.Lock()
            
            logging.info(f"Probed device {device_index}: {width}x{height} @ {fps}fps")
            return width, height, fps, "rgb24"
            
        except Exception as e:
            logging.error(f"Error probing direct video device {device_index}: {e}")
            return None, None, None, "rgb24"
    
    def create_ffmpeg_input(self, url, width: int, height: int, fps: float):
        """
        Create an ffmpeg input for a direct device with proper coordination.
        """
        is_device, device_index = self._is_direct_device(url)
        
        if not is_device:
            raise ValueError(f"URL {url} is not a direct video device")
        
        # Increment access count
        with self.main_lock:
            if device_index not in self.active_devices:
                # This shouldn't happen if get_video_properties was called first
                logging.warning(f"Device {device_index} not in active devices, initializing...")
                self.get_video_properties(url)
            
            self.active_devices[device_index]['access_count'] += 1
            self.active_devices[device_index]['last_access'] = time.time()
            
            logging.info(f"Creating ffmpeg input for device {device_index} "
                        f"(access count: {self.active_devices[device_index]['access_count']})")
        
        system = platform.system().lower()
        
        try:
            if system == "linux":
                ffmpeg_input = (
                    ffmpeg
                    .input(f"/dev/video{device_index}", format="v4l2", 
                           framerate=fps, video_size=f"{width}x{height}")
                )
            elif system == "windows":
                ffmpeg_input = (
                    ffmpeg
                    .input(f"video={device_index}", format="dshow",
                           framerate=fps, video_size=f"{width}x{height}")
                )
            elif system == "darwin":
                ffmpeg_input = (
                    ffmpeg
                    .input(f"{device_index}", format="avfoundation",
                           framerate=fps, video_size=f"{width}x{height}")
                )
            else:
                raise ValueError(f"Unsupported platform for direct video streaming: {system}")
            
            return ffmpeg_input
            
        except Exception as e:
            # Decrement access count on error
            with self.main_lock:
                if device_index in self.active_devices:
                    self.active_devices[device_index]['access_count'] -= 1
            raise e
    
    def release_device_access(self, url):
        """
        Release access to a direct device.
        """
        is_device, device_index = self._is_direct_device(url)
        
        if not is_device:
            return
        
        with self.main_lock:
            if device_index in self.active_devices:
                self.active_devices[device_index]['access_count'] -= 1
                
                logging.info(f"Released device {device_index} access "
                            f"(remaining count: {self.active_devices[device_index]['access_count']})")
                
                # Clean up if no more access
                if self.active_devices[device_index]['access_count'] <= 0:
                    del self.active_devices[device_index]
                    if device_index in self.device_locks:
                        del self.device_locks[device_index]
                    logging.info(f"Cleaned up device {device_index} resources")
    
    def is_device_busy(self, url) -> bool:
        """
        Check if a device is currently being accessed.
        """
        is_device, device_index = self._is_direct_device(url)
        
        if not is_device:
            return False
        
        with self.main_lock:
            return (device_index in self.active_devices and 
                    self.active_devices[device_index]['access_count'] > 0)
    
    def get_device_access_count(self, url) -> int:
        """
        Get the current access count for a device.
        """
        is_device, device_index = self._is_direct_device(url)
        
        if not is_device:
            return 0
        
        with self.main_lock:
            if device_index in self.active_devices:
                return self.active_devices[device_index]['access_count']
            return 0
    
    def get_all_devices_info(self) -> Dict[int, Dict]:
        """Get information about all active devices."""
        with self.main_lock:
            return {
                device_index: {
                    'width': info['width'],
                    'height': info['height'],
                    'fps': info['fps'],
                    'pixel_format': info['pixel_format'],
                    'access_count': info['access_count'],
                    'last_access': info['last_access'],
                    'time_since_last_access': time.time() - info['last_access']
                }
                for device_index, info in self.active_devices.items()
            }
    
    def cleanup_stale_devices(self, max_idle_time: float = 300.0):
        """
        Clean up devices that haven't been accessed for a while.
        """
        current_time = time.time()
        stale_devices = []
        
        with self.main_lock:
            for device_index, info in self.active_devices.items():
                if (current_time - info['last_access']) > max_idle_time and info['access_count'] <= 0:
                    stale_devices.append(device_index)
            
            for device_index in stale_devices:
                del self.active_devices[device_index]
                if device_index in self.device_locks:
                    del self.device_locks[device_index]
                logging.info(f"Cleaned up stale device {device_index}")
    
    def shutdown(self):
        """Shutdown the client and clean up all resources."""
        logging.info("Shutting down SharedDirectDeviceClient")
        
        with self.main_lock:
            self.active_devices.clear()
            self.device_locks.clear()
