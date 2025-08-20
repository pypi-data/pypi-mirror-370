import logging
from .GrpcClientBase import GrpcClientBase
from ..protos.PPEDetectionService_pb2_grpc import PPEDetectionGRPCServiceStub
from ..protos.PPEDetectionService_pb2 import UpsertPPEDetectionBatchRequest, UpsertPPEDetectionRequest, PPEDetectionLabelRequest
from ..repositories.PPEDetectionRepository import PPEDetectionRepository 

logger = logging.getLogger(__name__)

class PPEDetectionClient(GrpcClientBase):
    def __init__(self, server_host: str, server_port: int = 50051):
        """
        Initialize the PPE Detection Batch Client.

        Args:
            server_host (str): The server hostname or IP address.
            server_port (int): The server port. Default is 50051.
        """
        super().__init__(server_host, server_port)

        try:
            self.connect(PPEDetectionGRPCServiceStub)
        except Exception as e:
            logger.error(f"Failed to connect to gRPC server: {e}")
            self.stub = None
        
        self.repository = PPEDetectionRepository()

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

    def send_upsert_batch(self, worker_id: str, worker_source_id: str, detection_data: list, token: str) -> dict:
        """
        Sends a batch of PPE detection requests to the server using token authentication.

        Args:
            worker_id (str): The worker ID for the detection.
            worker_source_id (str): The worker source ID for the detection.
            detection_data (list): A list of dictionaries containing PPE detection data.
            token (str): Authentication token for the worker.

        Returns:
            dict: A dictionary containing the result of sending the batch request.
        """
        if not self.stub:
            return {"success": False, "message": "gRPC connection is not established."}

        try:
            # Prepare the list of UpsertPPEDetectionRequest messages
            ppe_detection_requests = []
            for data in detection_data:
                image_binary = self.read_image_as_binary(data['image'])
                image_tile_binary = self.read_image_as_binary(data['image_tile'])

                ppe_detection_labels = [
                    PPEDetectionLabelRequest(
                        code=label['code'],
                        confidence_score=label['confidence_score'],
                        b_box_x1=label['b_box_x1'],
                        b_box_y1=label['b_box_y1'],
                        b_box_x2=label['b_box_x2'],
                        b_box_y2=label['b_box_y2'],
                    )
                    for label in data['ppe_detection_labels']
                ]
                source = data['worker_source_id']
                request = UpsertPPEDetectionRequest(
                    person_id=data['person_id'],
                    worker_id=worker_id,
                    worker_source_id=source,
                    image=image_binary,
                    image_tile=image_tile_binary,
                    worker_timestamp=data['worker_timestamp'],
                    ppe_detection_labels=ppe_detection_labels,
                    token=token
                )
                ppe_detection_requests.append(request)

            # Create the UpsertPPEDetectionBatchRequest
            batch_request = UpsertPPEDetectionBatchRequest(
                ppe_detection_requests=ppe_detection_requests,
                token=token
            )

            # Call the UpsertBatch RPC
            response = self.handle_rpc(self.stub.UpsertBatch, batch_request)
            
            if response and response.success:
                self.repository.delete_records_from_db(detection_data)
                return {"success": True, "message": response.message}

            return {"success": False, "message": response.message if response else "Unknown error"}

        except Exception as e:
            logger.error(f"Error sending batch PPE detection: {e}")
            return {"success": False, "message": f"Error occurred: {e}"}
