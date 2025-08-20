import logging
from .GrpcClientBase import GrpcClientBase
from ..protos.DatasetSourceService_pb2_grpc import DatasetSourceServiceStub
from ..protos.DatasetSourceService_pb2 import (
    GetDatasetSourceListRequest,
    SendDatasetFrameRequest
)

logger = logging.getLogger(__name__)

class DatasetSourceClient(GrpcClientBase):
    def __init__(self, server_host: str, server_port: int = 50051):
        """
        Initialize the DatasetSource client.

        Args:
            server_host (str): The server hostname or IP address.
            server_port (int): The server port. Default is 50051.
        """
        super().__init__(server_host, server_port)

        try:
            self.connect(DatasetSourceServiceStub)
        except Exception as e:
            logging.error(f"Failed to connect to gRPC server: {e}")
            self.stub = None

    def get_dataset_source_list(self, token: str) -> dict:
        """
        Get dataset source list from the server using token authentication.

        Args:
            token (str): Authentication token for the worker.

        Returns:
            dict: A dictionary containing the result and dataset source list.
        """
        if not self.stub:
            return {"success": False, "message": "gRPC connection is not established."}

        try:
            request = GetDatasetSourceListRequest(token=token)
            response = self.handle_rpc(self.stub.GetDatasetSourceList, request)

            if response and response.success:
                return {"success": True, "message": response.message, "data": response.data}

            return {"success": False, "message": response.message if response else "Unknown error"}

        except Exception as e:
            logging.error(f"Error fetching dataset source list: {e}")
            return {"success": False, "message": f"Error occurred: {e}"}

    def send_dataset_frame(self, dataset_source_id: str, uuid: str, image: bytes, timestamp: int, token: str) -> dict:
        """
        Send a dataset frame to the server using token authentication.

        Args:
            dataset_source_id (str): The ID of the dataset source.
            uuid (str): Unique identifier for the frame.
            image (bytes): The image data as bytes.
            timestamp (int): Unix timestamp of the frame.
            token (str): Authentication token for the worker.

        Returns:
            dict: A dictionary containing the result of sending the frame.
        """
        if not self.stub:
            return {"success": False, "message": "gRPC connection is not established."}

        try:
            request = SendDatasetFrameRequest(
                dataset_source_id=dataset_source_id,
                uuid=uuid,
                image=image,
                timestamp=timestamp,
                token=token
            )
            response = self.handle_rpc(self.stub.SendDatasetFrame, request)

            if response and response.success:
                return {"success": True, "message": response.message}

            return {"success": False, "message": response.message if response else "Unknown error"}

        except Exception as e:
            logging.error(f"Error sending dataset frame: {e}")
            return {"success": False, "message": f"Error occurred: {e}"} 