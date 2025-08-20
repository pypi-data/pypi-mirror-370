import os
import logging
import threading
import time
from pathlib import Path
from enum import Enum
from typing import Dict, Optional, Set, List
from contextlib import contextmanager
from dataclasses import dataclass

from ..models.ai_model import AIModelEntity
from ..repositories.AIModelRepository import AIModelRepository
from .GrpcClientBase import GrpcClientBase
from ..protos.AIModelService_pb2_grpc import AIModelGRPCServiceStub
from ..protos.AIModelService_pb2 import GetAIModelListRequest, DownloadAIModelRequest
from ..database.DatabaseManager import _get_storage_paths


class DownloadState(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DownloadInfo:
    model_id: str
    model_name: str
    version: str
    state: DownloadState = DownloadState.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    thread: Optional[threading.Thread] = None
    stop_event: threading.Event = None

    def __post_init__(self):
        if self.stop_event is None:
            self.stop_event = threading.Event()


class AIModelClient(GrpcClientBase):
    def __init__(self, token: str, server_host: str, server_port: int = 50051):
        super().__init__(server_host, server_port)
        storage_paths = _get_storage_paths()
        self.models_path = storage_paths["models"]
        self.models_path.mkdir(parents=True, exist_ok=True)
        self.repository = AIModelRepository()
        self.token = token
        
        self.download_tracker: Dict[str, DownloadInfo] = {}
        self.download_lock = threading.RLock()
        
        if not self.connect(AIModelGRPCServiceStub):
            logging.error("Failed to connect to gRPC server")
            self.stub = None

    def _get_model_path(self, filename: str) -> Path:
        return self.models_path / os.path.basename(filename)

    def _model_file_exists(self, file_path: str) -> bool:
        if not file_path:
            return False
        model_path = self._get_model_path(file_path)
        return model_path.exists() and model_path.stat().st_size > 0

    @contextmanager
    def _download_lock_context(self):
        with self.download_lock:
            yield

    def _get_download_info(self, model_id: str) -> Optional[DownloadInfo]:
        with self._download_lock_context():
            return self.download_tracker.get(model_id)

    def _set_download_info(self, model_id: str, download_info: DownloadInfo):
        with self._download_lock_context():
            self.download_tracker[model_id] = download_info

    def _remove_download_info(self, model_id: str):
        with self._download_lock_context():
            self.download_tracker.pop(model_id, None)

    def _is_downloading(self, model_id: str) -> bool:
        download_info = self._get_download_info(model_id)
        return download_info and download_info.state in {DownloadState.PENDING, DownloadState.DOWNLOADING}

    def _cancel_download(self, model_id: str) -> bool:
        download_info = self._get_download_info(model_id)
        if not download_info or download_info.state not in {DownloadState.PENDING, DownloadState.DOWNLOADING}:
            return False

        download_info.state = DownloadState.CANCELLED
        download_info.stop_event.set()
        
        if download_info.thread and download_info.thread.is_alive():
            download_info.thread.join(timeout=5)
        
        self._update_model_status(model_id, "cancelled", "Download cancelled")
        logging.info(f"🛑 Cancelled download for {download_info.model_name}")
        return True

    def _update_model_status(self, model_id: str, status: str, error_message: str = None):
        try:
            from datetime import datetime
            model = self.repository.get_model_by_id(model_id)
            if model:
                model.download_status = status
                model.last_download_attempt = datetime.utcnow()
                if error_message:
                    model.download_error = error_message
                self.repository.session.commit()
        except Exception as e:
            logging.error(f"❌ Error updating model status: {e}")
            if hasattr(self.repository, 'session'):
                self.repository.session.rollback()

    def sync_ai_models(self, worker_id: str) -> dict:
        if not self.stub:
            return {"success": False, "message": "gRPC connection not established"}
        
        try:
            response = self._fetch_model_list(worker_id)
            if not response or not response.success:
                return {"success": False, "message": getattr(response, 'message', 'Unknown error')}
            
            self._process_server_models(response.data)
            return {"success": True, "message": response.message, "data": response.data}
        
        except Exception as e:
            logging.error(f"Error syncing models: {e}")
            return {"success": False, "message": f"Error: {e}"}

    def _fetch_model_list(self, worker_id: str):
        request = GetAIModelListRequest(worker_id=worker_id, token=self.token)
        return self.handle_rpc(self.stub.GetAIModelList, request)

    def _process_server_models(self, server_models):
        local_models = {model.id: model for model in self.repository.get_models()}
        server_model_ids = {model.id for model in server_models}
        
        new_models = []
        updated_models = []
        
        for model in server_models:
            existing_model = local_models.get(model.id)
            if existing_model:
                self._handle_existing_model(model, existing_model, updated_models)
            else:
                self._handle_new_model(model, new_models)
        
        models_to_delete = [
            model for model_id, model in local_models.items()
            if model_id not in server_model_ids
        ]
        
        self._save_changes(new_models, updated_models, models_to_delete)

    def _handle_existing_model(self, server_model, local_model, updated_models: List):
        if not self._model_file_exists(local_model.file):
            logging.warning(f"⚠️ Model file missing for {local_model.name}. Re-downloading...")
            self._schedule_download(server_model)
            return

        needs_update, changes = self._check_model_changes(server_model, local_model)

        version_changed = server_model.version != local_model.version
        if not needs_update:
            return

        change_desc = ", ".join(changes)
        logging.info(f"🔄 Model update: {server_model.name} ({change_desc})")

        if version_changed:
            self._cancel_download(server_model.id)
            self.delete_local_model(local_model.file)
            self._schedule_download(server_model)
        
        self._update_model_properties(local_model, server_model)
        updated_models.append(local_model)

    def _handle_new_model(self, server_model, new_models: List):
        if self._is_downloading(server_model.id):
            logging.info(f"⏳ Model {server_model.name} already downloading")
            return

        new_model = self._create_model_entity(server_model)
        new_models.append(new_model)
        
        logging.info(f"⬇️ New model: {server_model.name}")
        self._schedule_download(server_model)

    def _check_model_changes(self, server_model, local_model) -> tuple[bool, List[str]]:
        """Check if model needs update and return list of changes"""
        changes = []
        
        if server_model.version != local_model.version:
            changes.append(f"version: {local_model.version} -> {server_model.version}")
        
        if server_model.ai_model_type_code != local_model.type:
            changes.append(f"type: {local_model.type} -> {server_model.ai_model_type_code}")
        
        server_classes = set(server_model.classes)
        local_classes = set(local_model.get_classes() or [])
        if server_classes != local_classes:
            changes.append("classes updated")
        
        server_ppe_groups = {
            group.name: {"compliance": group.compliance, "violation": group.violation}
            for group in (server_model.ppe_class_groups or [])
        }
        local_ppe_groups = local_model.get_ppe_class_groups() or {}
        if server_ppe_groups != local_ppe_groups:
            changes.append("PPE class groups updated")
        
        if server_model.main_class != local_model.get_main_class():
            changes.append(f"main class: {local_model.get_main_class()} -> {server_model.main_class}")

        return bool(changes), changes
        
    def _create_model_entity(self, server_model) -> AIModelEntity:
        model = AIModelEntity(
            id=server_model.id,
            name=server_model.name,
            type=server_model.ai_model_type_code,
            file=os.path.basename(server_model.file_path),
            version=server_model.version
        )
        self._update_model_properties(model, server_model)
        return model

    def _update_model_properties(self, local_model: AIModelEntity, server_model):
        local_model.name = server_model.name
        local_model.type = server_model.ai_model_type_code
        local_model.version = server_model.version
        local_model.set_classes(list(server_model.classes))
        local_model.set_ppe_class_groups({
            group.name: {
            "compliance": group.compliance,
            "violation": group.violation
            }
            for group in (server_model.ppe_class_groups or [])
        })
        local_model.set_main_class(server_model.main_class)

    def _schedule_download(self, model):
        self._cancel_download(model.id)
        
        download_info = DownloadInfo(
            model_id=model.id,
            model_name=model.name,
            version=model.version,
            start_time=time.time()
        )
        
        self._update_model_status(model.id, "pending")
        
        download_info.thread = threading.Thread(
            target=self._download_worker,
            args=(model, download_info),
            daemon=True,
            name=f"ModelDownload-{model.id[:8]}"
        )
        download_info.thread.start()
        self._set_download_info(model.id, download_info)

    def _download_worker(self, model, download_info: DownloadInfo):
        try:
            download_info.state = DownloadState.DOWNLOADING
            self._update_model_status(model.id, "downloading")
            logging.info(f"📥 Downloading {model.name}...")
            
            success = self._download_model_file(model, download_info)
            
            if success:
                download_info.state = DownloadState.COMPLETED
                download_info.end_time = time.time()
                duration = download_info.end_time - download_info.start_time
                self._update_model_status(model.id, "completed")
                logging.info(f"✅ Downloaded {model.name} in {duration:.1f}s")
            else:
                self._handle_download_failure(download_info, "Download failed")
                
        except Exception as e:
            self._handle_download_failure(download_info, str(e))
        finally:
            threading.Timer(300, lambda: self._remove_download_info(model.id)).start()

    def _handle_download_failure(self, download_info: DownloadInfo, error: str):
        download_info.state = DownloadState.FAILED
        download_info.error_message = error
        self._update_model_status(download_info.model_id, "failed", error)
        logging.error(f"❌ Failed to download {download_info.model_name}: {error}")

    def _save_changes(self, new_models: List, updated_models: List, models_to_delete: List):
        try:
            if new_models:
                self.repository.session.bulk_save_objects(new_models)
            if updated_models:
                self.repository.session.bulk_save_objects(updated_models)
                
            for model in models_to_delete:
                logging.info(f"🗑️ Removing {model.name}")
                self._cancel_download(model.id)
                self.repository.session.delete(model)
                self.delete_local_model(model.file)
                
            self.repository.session.commit()
        except Exception as e:
            self.repository.session.rollback()
            logging.error(f"Error saving changes: {e}")
            raise

    def _download_model_file(self, model, download_info: DownloadInfo) -> bool:
        if not self.stub:
            return False
        
        try:
            request = DownloadAIModelRequest(ai_model_id=model.id, token=self.token)
            file_path = self._get_model_path(model.file_path)
            
            with open(file_path, "wb") as f:
                for chunk in self.stub.DownloadAIModel(request):
                    if download_info.stop_event.is_set():
                        logging.info(f"🛑 Download cancelled: {model.name}")
                        return False
                    f.write(chunk.file_chunk)
            
            return True
        
        except Exception as e:
            logging.error(f"❌ Download error for {model.name}: {e}")
            return False
    
    def delete_local_model(self, filename: str) -> bool:
        try:
            file_path = self._get_model_path(filename)
            if file_path.exists():
                file_path.unlink()
                logging.info(f"🗑️ Deleted {filename}")
                return True
            return False
        except Exception as e:
            logging.error(f"❌ Error deleting {filename}: {e}")
            return False

    def get_download_status(self, model_id: str) -> Optional[Dict]:
        download_info = self._get_download_info(model_id)
        if not download_info:
            return None
            
        return {
            "model_id": download_info.model_id,
            "model_name": download_info.model_name,
            "version": download_info.version,
            "state": download_info.state.value,
            "start_time": download_info.start_time,
            "end_time": download_info.end_time,
            "error_message": download_info.error_message
        }

    def get_all_download_status(self) -> Dict[str, Dict]:
        with self._download_lock_context():
            return {
                model_id: self.get_download_status(model_id)
                for model_id in self.download_tracker.keys()
            }

    def cancel_all_downloads(self) -> int:
        cancelled_count = 0
        with self._download_lock_context():
            for model_id in list(self.download_tracker.keys()):
                if self._cancel_download(model_id):
                    cancelled_count += 1
        return cancelled_count

    def cleanup_downloads(self):
        with self._download_lock_context():
            completed_ids = [
                model_id for model_id, info in self.download_tracker.items()
                if info.state in {DownloadState.COMPLETED, DownloadState.FAILED, DownloadState.CANCELLED}
            ]
            for model_id in completed_ids:
                self._remove_download_info(model_id)