import grpc
import time
import logging
import json
import subprocess
import ffmpeg
import fractions
from urllib.parse import urlparse
from .GrpcClientBase import GrpcClientBase
from .SharedDirectDeviceClient import SharedDirectDeviceClient
from ..util.FFmpegUtil import get_rtsp_ffmpeg_options, get_rtsp_probe_options
from ..protos.VisionWorkerService_pb2_grpc import VideoStreamServiceStub
from ..protos.VisionWorkerService_pb2 import VideoFrame


class VideoStreamClient(GrpcClientBase):
    def __init__(self, server_host: str, server_port: int = 50051):
        """Initialize the video stream client."""
        super().__init__(server_host, server_port)
        self.shared_device_client = SharedDirectDeviceClient()

    def _detect_stream_type(self, url):
        if isinstance(url, str) and url.isdigit():
            return "direct"
        
        parsed_url = urlparse(url)
        if parsed_url.scheme == "rtsp":
            return "rtsp"
        elif parsed_url.scheme in ["http", "https"] and url.endswith(".m3u8"):
            return "hls"
        else:
            return "unknown"

    def _get_video_properties(self, url, stream_type):
        try:
            if stream_type == "direct":
                # Use the shared device client for direct devices
                width, height, fps, pixel_format = self.shared_device_client.get_video_properties(url)
                return width, height, fps, pixel_format
            
            probe_cmd = [
                "ffprobe",
                "-i", url,
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate,pix_fmt",
                "-of", "json",
                "-v", "quiet"
            ]

            if stream_type == "rtsp":
                probe_options = get_rtsp_probe_options()
                # Insert options at the beginning (after ffprobe)
                for i, option in enumerate(probe_options):
                    probe_cmd.insert(1 + i, option)

            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            probe_data = json.loads(result.stdout)

            if "streams" in probe_data and len(probe_data["streams"]) > 0:
                stream = probe_data["streams"][0]
                width = int(stream["width"])
                height = int(stream["height"])
                fps = float(fractions.Fraction(stream["r_frame_rate"]))  # Safe FPS conversion
                pixel_format = stream["pix_fmt"]
                return width, height, fps, pixel_format

        except Exception as e:
            logging.error(f"Error extracting video properties: {e}")

        return None, None, None, None

    def _get_bytes_per_pixel(self, pixel_format):
        pixel_map = {"rgb24": 3, "yuv420p": 1.5, "gray": 1}
        return pixel_map.get(pixel_format, 3)

    def _generate_frames(self, url, worker_id, uuid, stream_duration):
        stream_type = self._detect_stream_type(url)
        if stream_type == "unknown":
            logging.error(f"Unsupported stream type: {url}")
            return

        width, height, fps, pixel_format = self._get_video_properties(url, stream_type)
        if not width or not height or not fps:
            logging.error("Failed to retrieve stream properties.")
            return

        bytes_per_pixel = self._get_bytes_per_pixel(pixel_format)
        frame_size = int(width * height * bytes_per_pixel)
        frame_interval = 1.0 / fps
        start_time = time.time()
        empty_frame_count = 0

        logging.info(f"Streaming {stream_type.upper()} from: {url} for {stream_duration} seconds...")

        if stream_type == "direct":
            # Use the shared device client for direct devices
            try:
                ffmpeg_input = self.shared_device_client.create_ffmpeg_input(url, width, height, fps)
            except Exception as e:
                logging.error(f"Failed to create ffmpeg input for direct device: {e}")
                return
        elif stream_type == "rtsp":
            rtsp_options = get_rtsp_ffmpeg_options()
            ffmpeg_input = ffmpeg.input(url, **rtsp_options)
        elif stream_type == "hls":
            ffmpeg_input = (
                ffmpeg
                .input(url, format="hls", analyzeduration="10000000", probesize="10000000")
            )
        else:
            logging.error(f"Unsupported stream type: {url}")
            return

        process = (
            ffmpeg_input
            .output("pipe:", format="rawvideo", pix_fmt=pixel_format, vsync="passthrough")
            .overwrite_output()  # Replaces `global_args()` for avoiding conflicts
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )

        try:
            while time.time() - start_time < stream_duration:
                frame_bytes = process.stdout.read(frame_size)

                if not frame_bytes:
                    empty_frame_count += 1
                    logging.warning(f"Empty frame received ({empty_frame_count}), retrying...")

                    if empty_frame_count > 5:
                        logging.error("Too many empty frames, stopping stream...")
                        break
                    continue

                empty_frame_count = 0
                yield VideoFrame(
                    worker_id=worker_id,
                    uuid=uuid,
                    frame_data=frame_bytes,
                    timestamp=int(time.time() * 1000),
                )

                time.sleep(frame_interval)

        except Exception as e:
            logging.error(f"Streaming error: {e}")

        finally:
            # Release device access for direct devices
            if stream_type == "direct":
                self.shared_device_client.release_device_access(url)
            
            try:
                stderr_output = process.stderr.read().decode()
                if stderr_output.strip():  # Only log if there's actual error content
                    logging.error(f"FFmpeg stderr for {stream_type} stream: {stderr_output}")
            except Exception as e:
                logging.warning(f"Could not read FFmpeg stderr: {e}")
            
            process.terminate()
            process.wait()

    def stream_video(self, worker_id, uuid, url, stream_duration):
        """
        Stream video frames from RTSP or HLS to gRPC server.

        Args:
            worker_id (str): Worker ID
            uuid (str): Unique stream session ID
            url (str): Stream URL (RTSP or HLS)
            stream_duration (int): Duration in seconds to stream
        """
        self.connect(VideoStreamServiceStub)  # Ensure connection and stub are established

        try:
            for response in self.stub.StreamVideo(self._generate_frames(url, worker_id, uuid, stream_duration)):
                if response.success:
                    logging.info(f"Frame sent successfully: {response.message}")
                else:
                    logging.error(f"Frame rejected: {response.message}")

        except grpc.RpcError as e:
            logging.error(f"gRPC error: {e.code()} - {e.details()}")  # Log more details
        except Exception as e:
            logging.error(f"Unexpected streaming error: {e}")
