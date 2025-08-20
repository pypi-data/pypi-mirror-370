import logging
import os
from pathlib import Path
from ..database.DatabaseManager import _get_storage_paths
from ..models.worker_source import WorkerSourceEntity
from .GrpcClientBase import GrpcClientBase
from ..protos.WorkerSourceService_pb2_grpc import WorkerSourceServiceStub
from ..protos.WorkerSourceService_pb2 import (
    GetWorkerSourceListRequest,
    UpdateWorkerSourceRequest,
    DownloadSourceFileRequest
)
from ..repositories.WorkerSourceRepository import WorkerSourceRepository

logger = logging.getLogger(__name__)

class WorkerSourceClient(GrpcClientBase):
    def __init__(self, server_host: str, server_port: int = 50051):
        super().__init__(server_host, server_port)
        storage_paths = _get_storage_paths()
        self.source_file_path = storage_paths["files"] / "source_files"
        self.source_file_path.mkdir(parents=True, exist_ok=True)
        self.repo = WorkerSourceRepository()
        try:
            self.connect(WorkerSourceServiceStub)
        except Exception as e:
            logging.error(f"Failed to connect to gRPC server: {e}")
            self.stub = None

    def _get_path(self, file: str) -> Path:
        """Get the path to a local AI model file."""
        return self.source_file_path / os.path.basename(file)

    def sync_worker_sources(self, worker_id: str, token: str) -> dict:
        """Fetch and sync worker source list from gRPC service using token authentication."""
        if not self.stub:
            return {"success": False, "message": "gRPC connection is not established."}

        try:
            request = GetWorkerSourceListRequest(worker_id=worker_id, token=token)
            response = self.handle_rpc(self.stub.GetWorkerSourceList, request)

            if response and response.success:
                self._process_server_sources(response.data)
                return {"success": True, "message": response.message, "data": response.data}

            return {"success": False, "message": response.message if response else "Unknown error"}

        except Exception as e:
            logging.error(f"Error fetching worker source list: {e}")
            return {"success": False, "message": f"Error occurred: {e}"}
        
    def _process_server_sources(self, server_sources):
        """Process server sources, handling additions, updates, and deletions."""
        local_sources = {source.id: source for source in self.repo.get_all_worker_sources()}
        server_source_ids = set()
        
        new_sources = []
        updated_sources = []
        changed_records = []
        
        # Process each source from the server
        for source in server_sources:
            server_source_ids.add(source.id)
            existing_source = local_sources.get(source.id)

            if existing_source:
                self._handle_existing_source(source, existing_source, updated_sources, changed_records)
            else:
                self._handle_new_source(source, new_sources)
        
        # Handle sources that no longer exist on the server
        sources_to_delete = [
            source for source_id, source in local_sources.items()
            if source_id not in server_source_ids
        ]
        
        self._save_changes(new_sources, updated_sources, sources_to_delete, changed_records)

    def _handle_existing_source(self, source, existing_source, updated_sources, changed_records):
        """Handle source that exists locally but might need updates."""
        changes = []

        # Check for field changes and log them
        if existing_source.name != source.name:
            changes.append(f"name: '{existing_source.name}' → '{source.name}'")
        if existing_source.worker_id != source.worker_id:
            changes.append(f"worker_id: {existing_source.worker_id} → {source.worker_id}")
        if existing_source.type_code != source.type_code:
            if source.type_code in ["live", "direct"]:
                self.delete_local_source_file(existing_source.file_path)
            elif existing_source.file_path == source.file_path:
                self.download_source_file(source)

            changes.append(f"type_code: {existing_source.type_code} → {source.type_code}")
        if existing_source.url != source.url:
            changes.append(f"url: {existing_source.url} → {source.url}")
        if existing_source.file_path != source.file_path:
            self.delete_local_source_file(existing_source.file_path)
            self.download_source_file(source)

            changes.append(f"file_path: {existing_source.file_path} → {source.file_path}")

        if changes:
            # Update existing record
            existing_source.name = source.name
            existing_source.worker_id = source.worker_id
            existing_source.type_code = source.type_code
            existing_source.url = source.url
            existing_source.file_path = source.file_path

            updated_sources.append(existing_source)
            changed_records.append(f"🔄 [APP] [UPDATE] Worker Source ID {source.id}: " + ", ".join(changes))

    def _handle_new_source(self, source, new_sources):
        """Handle source that doesn't exist locally."""
        new_record = WorkerSourceEntity(
                        id=source.id,
                        name=source.name,
                        worker_id=source.worker_id,
                        type_code=source.type_code,
                        file_path=source.file_path,
                        url=source.url
                    )
        new_sources.append(new_record)
        logger.info(f"🆕 [APP] [INSERT] Added Worker Source ID {source.id} - {source.name}")
        if source.type_code == "file":
            self.download_source_file(source)

    def _save_changes(self, new_sources, updated_sources, sources_to_delete, changed_records):
        """Save all changes to database in a single transaction."""
        try:
            if new_sources:
                self.repo.session.bulk_save_objects(new_sources)

            if updated_sources:
                self.repo.session.bulk_save_objects(updated_sources)
                
            for source in sources_to_delete:
                logger.info(f"❌ [APP] [DELETE] Removing Worker Source ID {source.id} - {source.name}")
                self.repo.session.delete(source)
                self.delete_local_source_file(source.file_path)
                
            self.repo.session.commit()

            for change in changed_records:
                logger.info(change)

        except Exception as e:
            self.repo.session.rollback()
            logging.error(f"Error saving sources changes: {e}")
            raise

    def update_worker_source(
        self, worker_source_id: str, resolution: str, status_code: str, frame_rate: float, worker_timestamp: str, token: str
    ) -> dict:
        """Updates a worker source entry using gRPC with token authentication."""
        if not self.stub:
            return {"success": False, "message": "gRPC connection is not established."}

        try:
            request = UpdateWorkerSourceRequest(
                worker_source_id=worker_source_id,
                resolution=resolution,
                status_code=status_code,
                frame_rate=frame_rate,
                worker_timestamp=worker_timestamp,
                token=token
            )
            response = self.handle_rpc(self.stub.Update, request)

            if response and response.success:
                return {"success": True, "message": response.message}

            return {"success": False, "message": response.message if response else "Unknown error"}

        except Exception as e:
            logging.error(f"Error updating worker source: {e}")
            return {"success": False, "message": f"Error occurred: {e}"}

    def download_source_file(self, source) -> bool:
        """Download the AI model and save it to the models directory."""
        if not self.stub:
            logging.error("gRPC connection is not established.")
            return False
        if not source.file_path:
            return False
        
        try:
            logging.info(f"📥 Downloading source file '{source.name}'...")
            request = DownloadSourceFileRequest(source_id=source.id)
            file_path = self._get_path(source.file_path)
            
            with open(file_path, "wb") as f:
                for chunk in self.stub.DownloadSourceFile(request):
                    f.write(chunk.file_chunk)
            
            logging.info(f"✅ Source File '{source.name}' downloaded successfully")
            return True
        
        except Exception as e:
            logging.error(f"❌ Error downloading Source File '{source.name}': {e}")
            return False
        
    def delete_local_source_file(self, file: str) -> None:
        """Delete a local Source file."""
        if not file:
            return

        file_path = self._get_path(file)
        try:
            file_path.unlink()
            logging.info(f"🗑️ File deleted")
        except Exception as e:
            logging.error(f"❌ Error deleting file: {e}")