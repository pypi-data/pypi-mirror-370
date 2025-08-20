from .GrpcClientBase import GrpcClientBase
from ..protos.VisionWorkerService_pb2_grpc import VisionWorkerServiceStub
from ..protos.VisionWorkerService_pb2 import SystemUsageRequest, GPUUsage
import logging


class SystemUsageClient(GrpcClientBase):
    def __init__(self, server_host: str, server_port: int = 50051):
        """
        Initialize the system usage client.

        Args:
            server_host (str): The server hostname or IP address.
            server_port (int): The server port. Default is 50051.
        """
        super().__init__(server_host, server_port)

        try:
            self.connect(VisionWorkerServiceStub)
        except Exception as e:
            logging.error(f"Failed to connect to gRPC server: {e}")
            self.stub = None

    def send_system_usage(self, device_id: str, cpu_usage: float, ram_usage: dict, gpu_usage: list, latency: float, token: str) -> dict:
        """
        Send system usage data to the server using token authentication.

        Args:
            device_id (str): The unique device ID.
            cpu_usage (float): CPU usage percentage.
            ram_usage (dict): RAM usage details.
            gpu_usage (list): GPU usage details.
            latency (float): Measured network latency in milliseconds.
            token (str): Authentication token for the worker.

        Returns:
            dict: A dictionary containing the result of sending system usage.
        """
        if not self.stub:
            return {"success": False, "message": "gRPC connection is not established."}

        try:
            # Prepare the request
            request = SystemUsageRequest(
                device_id=device_id,
                cpu_usage=cpu_usage,
                ram_usage_percent=ram_usage.get("percent", 0.0),
                ram_total=ram_usage.get("total", 0),
                ram_used=ram_usage.get("used", 0),
                ram_free=ram_usage.get("free", 0),
                latency_ms=latency, 
                token=token,
                gpu=[
                    GPUUsage(
                        gpu_index=gpu.get("gpu_index", 0),
                        gpu_usage_percent=gpu.get("gpu_usage_percent", 0.0),
                        memory_usage_percent=gpu.get("memory_usage_percent", 0.0),
                        temperature_celsius=gpu.get("temperature_celsius", 0.0),
                        total_memory=gpu.get("total_memory", 0),
                        used_memory=gpu.get("used_memory", 0),
                        free_memory=gpu.get("free_memory", 0),
                    )
                    for gpu in (gpu_usage or [])  # Handle None or empty list
                ],
            )

            # Call the SendSystemUsage RPC
            response = self.handle_rpc(self.stub.SendSystemUsage, request)

            if response and response.success:
                return {"success": True, "message": response.message}

            return {"success": False, "message": response.message if response else "Unknown error"}

        except Exception as e:
            logging.error(f"Error sending system usage: {e}")
            return {"success": False, "message": f"Error occurred: {e}"}
