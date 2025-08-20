import subprocess
import logging
import os

class FileToRTMPStreamer:
    def __init__(self, video_path, rtmp_url, stream_key, fps=30, resolution="1280x720", loop=False):
        """
        Initialize the file streamer.

        Args:
            video_path (str): Path to the local video file.
            rtmp_url (str): The RTMP server URL (without stream key).
            stream_key (str): The unique stream key for RTMP.
            fps (int): Frames per second for output stream.
            resolution (str): Resolution of the output stream.
            loop (bool): Loop the video until manually stopped.
        """
        self.video_path = video_path
        self.rtmp_url = f"{rtmp_url}/{stream_key}"
        self.fps = fps
        self.resolution = resolution
        self.loop = loop
        self.stream_key = stream_key
        self.process = None

    def start_stream(self):
        """Start streaming video file to RTMP using FFmpeg."""
        if not os.path.exists(self.video_path):
            logging.error(f"❌ [APP] Video file not found: {self.video_path}")
            return

        logging.info(f"📼 [APP] Starting file stream: {self.video_path} → {self.rtmp_url}")

        # FFmpeg command
        ffmpeg_command = [
            "ffmpeg",
            "-re",  # Read input at native frame rate
            "-stream_loop", "-1" if self.loop else "0",  # Loop if needed
            "-i", self.video_path,

            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-tune", "zerolatency",
            "-r", str(self.fps),
            "-b:v", "1500k",
            "-maxrate", "2000k",
            "-bufsize", "4000k",
            "-g", str(self.fps),
            "-vf", f"scale={self.resolution}",

            "-an",  # Disable audio

            "-f", "flv",
            self.rtmp_url
        ]

        try:
            with open(os.devnull, "w") as devnull:
                self.process = subprocess.Popen(
                    ffmpeg_command,
                    stdout=devnull,
                    stderr=devnull,
                    text=True
                )

            logging.info("✅ [APP] FFmpeg file stream process started successfully.")
            self.process.wait()  # Block until process is terminated

        except Exception as e:
            logging.error(f"🚨 [APP] Failed to start FFmpeg file stream: {e}")
            self.stop_stream()

    def stop_stream(self):
        """Stop the streaming process."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            logging.info("🛑 [APP] FFmpeg file stream process terminated.")
