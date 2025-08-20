import logging
from ..repositories.RestrictedAreaRepository import RestrictedAreaRepository
from .GrpcClientBase import GrpcClientBase
from ..protos.HumanDetectionService_pb2_grpc import HumanDetectionGRPCServiceStub
from ..protos.HumanDetectionService_pb2 import (
    UpsertHumanDetectionBatchRequest,
    UpsertHumanDetectionRequest,
)

logger = logging.getLogger(__name__)

class RestrictedAreaClient(GrpcClientBase):
    def __init__(self, server_host: str, server_port: int = 50051):
        """
        Initialize the Restricted Area Violation Client.

        Args:
            server_host (str): The server hostname or IP address.
            server_port (int): The server port. Default is 50051.
        """
        super().__init__(server_host, server_port)

        try:
            self.connect(HumanDetectionGRPCServiceStub)
        except Exception as e:
            logger.error(f"Failed to connect to gRPC server: {e}")
            self.stub = None

        self.repository = RestrictedAreaRepository()

    @staticmethod
    def read_image_as_binary(image_path: str) -> bytes:
        """
        Reads an image file and returns its binary content.

        Args:
            image_path (str): Path to the image file.

        Returns:
            bytes: Binary content of the image.
        """
        with open(image_path, 'rb') as image_file:
            return image_file.read()

    def send_upsert_batch(self, worker_id: str, worker_source_id: str, violation_data: list, token: str) -> dict:
        """
        Sends a batch of restricted area violation records to the server using token authentication.

        Args:
            worker_id (str): The worker ID for the violation.
            worker_source_id (str): The worker source ID for the violation.
            violation_data (list): A list of dictionaries representing the violations.
            token (str): Authentication token for the worker.

        Returns:
            dict: A dictionary containing the result of the batch request.
        """
        if not self.stub:
            return {"success": False, "message": "gRPC connection is not established."}

        try:
            human_detection_requests = []

            for data in violation_data:
                image_binary = self.read_image_as_binary(data['image'])
                image_tile_binary = self.read_image_as_binary(data['image_tile'])

                request = UpsertHumanDetectionRequest(
                    person_id=data['person_id'],
                    worker_id=worker_id,
                    worker_source_id=data['worker_source_id'],
                    image=image_binary,
                    image_tile=image_tile_binary,
                    worker_timestamp=data['worker_timestamp'],
                    confidence_score=data['confidence_score'],
                    b_box_x1=data['b_box_x1'],
                    b_box_y1=data['b_box_y1'],
                    b_box_x2=data['b_box_x2'],
                    b_box_y2=data['b_box_y2'],
                    token=token,
                )

                human_detection_requests.append(request)

            batch_request = UpsertHumanDetectionBatchRequest(
                human_detection_requests=human_detection_requests,
                token=token
            )

            response = self.handle_rpc(self.stub.UpsertBatch, batch_request)

            if response and response.success:
                self.repository.delete_records_from_db(violation_data)
                return {"success": True, "message": response.message}

            return {"success": False, "message": response.message if response else "Unknown error"}

        except Exception as e:
            logger.error(f"Error sending batch restricted area violation data: {e}")
            return {"success": False, "message": f"Error occurred: {e}"}
