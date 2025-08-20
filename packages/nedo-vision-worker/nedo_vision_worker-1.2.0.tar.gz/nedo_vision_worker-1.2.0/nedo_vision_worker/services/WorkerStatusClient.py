import logging
import grpc
from ..protos.VisionWorkerService_pb2 import UpdateWorkerStatusRequest
from ..protos.VisionWorkerService_pb2_grpc import VisionWorkerServiceStub
from .GrpcClientBase import GrpcClientBase
import time

logger = logging.getLogger(__name__)

class WorkerStatusClient(GrpcClientBase):
    def __init__(self, server_host: str, server_port: int = 50051):
        """
        Initialize the WorkerStatusClient for updating worker status.
        
        Args:
            server_host (str): The gRPC server host.
            server_port (int): The gRPC server port.
        """
        super().__init__(server_host, server_port)
        
        try:
            self.connect(VisionWorkerServiceStub)
        except Exception as e:
            logging.error(f"Failed to connect to gRPC server: {e}")
            self.stub = None
            

    def update_worker_status(self, worker_id: str, status_code: str, token: str) -> dict:
        """
        Update the status of a worker on the server using token authentication.
        
        Args:
            worker_id (str): The ID of the worker.
            status_code (str): The status code to report (e.g., "RUNNING", "STOPPED").
            token (str): Authentication token for the worker.
            
        Returns:
            dict: Result of the status update operation.
        """
        if not self.stub:
            return {"success": False, "message": "gRPC connection is not established."}
        
        try:    
            timestamp = int(time.time() * 1000)
            request = UpdateWorkerStatusRequest(
                worker_id=worker_id,
                status_code=status_code,
                timestamp=timestamp,
                token=token
            )
            
            response = self.handle_rpc(self.stub.UpdateStatus, request)
            
            if response and response.success:
                return {"success": True, "message": response.message}
                
            return {"success": False, "message": response.message if response else "Unknown error"}
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error while updating status for {worker_id}: {str(e)}")
            return {"success": False, "message": f"RPC error: {str(e)}"}
            
        except Exception as e:
            logger.error(f"Unexpected error while updating status for {worker_id}: {str(e)}")
            return {"success": False, "message": f"An unexpected error occurred: {str(e)}"}