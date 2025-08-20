from .GrpcClientBase import GrpcClientBase
from ..protos.VisionWorkerService_pb2_grpc import ImageServiceStub
from ..protos.VisionWorkerService_pb2 import LastImageDateRequest, UploadImageRequest


class ImageUploadClient(GrpcClientBase):
    def __init__(self, server_host: str, server_port: int = 50051):
        """
        Initialize the image upload client.

        Args:
            server_host (str): The server hostname or IP address.
            server_port (int): The server port. Default is 50051.
        """
        super().__init__(server_host, server_port)

    def get_last_uploaded_date(self, device_id: str):
        """
        Retrieve the last uploaded image date from the server.

        Args:
            device_id (str): The unique device ID.

        Returns:
            dict: A dictionary containing the last upload date and additional information.
        """
        self.connect(ImageServiceStub)  # Ensure connection and stub are established

        try:
            # Prepare the request with the device_id
            request = LastImageDateRequest(device_id=device_id)
            response = self.handle_rpc(self.stub.GetLastImageDate, request)

            if response and response.success:
                return {
                    "success": True,
                    "last_uploaded_date": response.last_uploaded_date,
                    "message": response.message,
                }
            return {
                "success": False,
                "message": response.message if response else "Unknown error",
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def upload_image(self, device_id: str, metadata: str, image_path: str):
        """
        Upload an image to the server.

        Args:
            device_id (str): The unique device ID.
            metadata (str): Metadata as a JSON string.
            image_path (str): Path to the image file.

        Returns:
            dict: A dictionary containing the result of the upload operation.
        """
        self.connect(ImageServiceStub)  # Ensure connection and stub are established

        try:
            # Read the image file
            with open(image_path, "rb") as file:
                image_data = file.read()

            # Create the request
            request = UploadImageRequest(
                device_id=device_id,
                metadata=metadata,
                image_data=image_data,
            )

            # Call the RPC
            response = self.handle_rpc(self.stub.UploadImage, request)

            if response and response.success:
                return {"success": True, "message": response.message}
            return {"success": False, "message": response.message if response else "Unknown error"}
        except FileNotFoundError:
            return {"success": False, "message": f"File not found: {image_path}"}
        except Exception as e:
            return {"success": False, "message": str(e)}
