import subprocess
import logging
import time
import os
from urllib.parse import urlparse

class RTSPtoRTMPStreamer:
    def __init__(self, rtsp_url, rtmp_url, stream_key, fps=30, resolution="1280x720", duration=120):
        """
        Initialize the streamer.

        Args:
            rtsp_url (str): The RTSP stream URL (e.g., from an IP camera).
            rtmp_url (str): The RTMP server URL (without stream key).
            stream_key (str): The unique stream key for RTMP.
            fps (int): Frames per second for output stream.
            resolution (str): Resolution of the output stream.
            duration (int): Duration in seconds to stream.
        """
        self.rtsp_url = rtsp_url
        self.rtmp_url = f"{rtmp_url}/{stream_key}"
        self.fps = fps
        self.resolution = resolution
        self.duration = duration
        self.stream_key = stream_key
        self.process = None

    def _detect_stream_type(self, url):
        """Detect the type of input stream."""
        parsed_url = urlparse(url)
        return "rtsp" if parsed_url.scheme == "rtsp" else "unknown"
    
    def start_stream(self):
        """Start streaming RTSP to RTMP using FFmpeg without logs."""
        if self._detect_stream_type(self.rtsp_url) == "unknown":
            logging.error(f"❌ [APP] Invalid RTSP URL: {self.rtsp_url}")
            return

        logging.info(f"📡 [APP] Starting RTSP to RTMP stream: {self.rtsp_url} → {self.rtmp_url} for {self.duration} seconds")

        # FFmpeg command
        ffmpeg_command = [
            "ffmpeg",
            "-rtsp_transport", "tcp",  # 🚀 Use TCP
            "-fflags", "nobuffer",  # 🚀 Reduce internal buffering
            "-flags", "low_delay",  # 🚀 Enable low-latency mode
            "-strict", "experimental",
            "-i", self.rtsp_url,

            # ✅ Video Encoding (Fastest possible)
            "-c:v", "libx264",
            "-preset", "ultrafast",  # 🚀 Reduce CPU usage
            "-tune", "zerolatency",  # 🚀 Optimize for real-time streaming
            "-x264-params", "keyint=40:min-keyint=40",  # 🚀 Keyframe optimization
            "-r", "25",  # ⏳ Limit FPS to 20 (prevents excessive encoding load)
            "-b:v", "1500k",  # ✅ Lower bitrate to improve performance
            "-maxrate", "2000k",  # ✅ Set max bitrate
            "-bufsize", "4000k",  # ✅ Reduce buffer latency
            "-g", "25",  # ✅ Reduce GOP size for faster keyframes
            "-vf", "scale='min(1024,iw)':-2",  # ✅ Resize width to max 800px

            # ❌ Disable Audio (Avoid unnecessary encoding overhead)
            "-an",

            # ✅ Output RTMP Stream
            "-f", "flv",
            self.rtmp_url
        ]

        try:
            with open(os.devnull, "w") as devnull:
                self.process = subprocess.Popen(
                    ffmpeg_command,
                    stdout=devnull,  # Redirect stdout to null
                    stderr=devnull,  # Redirect stderr to null
                    text=True
                )

            logging.info("✅ [APP] FFmpeg process started successfully.")

            start_time = time.time()
            while self.process.poll() is None:
                if time.time() - start_time > self.duration:
                    logging.info(f"⏳ [APP] Streaming duration {self.duration}s reached. Stopping stream...")
                    self.stop_stream()
                    break
                time.sleep(1)

        except Exception as e:
            logging.error(f"🚨 [APP] Failed to start FFmpeg: {e}")
            self.stop_stream()
    
    def stop_stream(self):
        """Stop the streaming process."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            logging.info("FFmpeg process terminated.")
