"""
FFmpeg utilities for Jetson compatibility and RTSP stream handling.

This module provides common FFmpeg configurations and utilities that work
reliably on Jetson devices with FFmpeg 4.4.1 and newer versions.
"""

import logging
import subprocess
import re
from typing import Dict, Any, Tuple


def get_ffmpeg_version() -> Tuple[int, int, int]:
    """
    Get the FFmpeg version as a tuple of (major, minor, patch).
    
    Returns:
        Tuple[int, int, int]: Version tuple (major, minor, patch)
    """
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            # Extract version from output like "ffmpeg version n7.1.1" or "ffmpeg version 4.4.1"
            match = re.search(r'ffmpeg version n?(\d+)\.(\d+)\.(\d+)', result.stdout)
            if match:
                return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except Exception as e:
        logging.warning(f"Could not determine FFmpeg version: {e}")
    
    # Default to a reasonable version if detection fails
    return (4, 4, 1)


def get_rtsp_ffmpeg_options() -> Dict[str, Any]:
    """
    Get FFmpeg options optimized for RTSP streams with version compatibility.
    
    These options work across different FFmpeg versions:
    - FFmpeg 4.4.x: Uses stimeout
    - FFmpeg 5.x+: Uses timeout 
    - FFmpeg 7.x+: Uses timeout
    
    Returns:
        Dict[str, Any]: FFmpeg input options for RTSP streams
    """
    version = get_ffmpeg_version()
    major, minor, patch = version
    
    # Base options that work across all versions
    options = {
        "rtsp_transport": "tcp",
        "fflags": "nobuffer+genpts", 
        "max_delay": "5000000",  # Max buffering delay
        "buffer_size": "1024000",  # Input buffer size
        "avoid_negative_ts": "make_zero"  # Handle timestamp issues
    }
    
    # Add version-specific timeout option
    if major == 4 and minor == 4:
        # FFmpeg 4.4.x uses stimeout
        options["stimeout"] = "5000000"
        logging.debug("Using stimeout for FFmpeg 4.4.x")
    else:
        # FFmpeg 5.x+ uses timeout (microseconds)
        options["timeout"] = "5000000"
        logging.debug(f"Using timeout for FFmpeg {major}.{minor}.{patch}")
    
    return options


def get_rtsp_probe_options() -> list:
    """
    Get ffprobe command line options for RTSP streams with version compatibility.
    
    Returns:
        list: Command line options to insert into ffprobe command
    """
    version = get_ffmpeg_version()
    major, minor, patch = version
    
    base_options = ["-rtsp_transport", "tcp"]
    
    # Add version-specific timeout option
    if major == 4 and minor == 4:
        # FFmpeg 4.4.x uses stimeout
        return base_options + ["-stimeout", "5000000"]
    else:
        # FFmpeg 5.x+ uses timeout
        return base_options + ["-timeout", "5000000"]


def log_ffmpeg_version_info():
    """Log information about FFmpeg compatibility."""
    version = get_ffmpeg_version()
    major, minor, patch = version
    
    logging.info(f"Detected FFmpeg version: {major}.{minor}.{patch}")
    
    if major == 4 and minor == 4:
        logging.info("Using 'stimeout' parameter for FFmpeg 4.4.x compatibility")
    else:
        logging.info(f"Using 'timeout' parameter for FFmpeg {major}.{minor}.{patch}")
    
    logging.info("RTSP configuration optimized for embedded devices")


def get_stream_timeout_duration(stream_type: str) -> int:
    """
    Get appropriate timeout duration for different stream types.
    
    Args:
        stream_type (str): Type of stream (rtsp, hls, direct, etc.)
        
    Returns:
        int: Timeout duration in seconds
    """
    timeouts = {
        "rtsp": 30,     # RTSP streams may take longer to connect
        "hls": 20,      # HLS streams need time for manifest download
        "direct": 10,   # Direct device access should be faster
        "video_file": 5 # Local files should be very fast
    }
    return timeouts.get(stream_type, 15)  # Default 15 seconds
