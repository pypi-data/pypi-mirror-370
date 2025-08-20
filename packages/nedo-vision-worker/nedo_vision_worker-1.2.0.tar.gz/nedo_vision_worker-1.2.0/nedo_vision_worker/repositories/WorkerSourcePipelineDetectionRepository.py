import os
from sqlalchemy.orm import Session
from ..database.DatabaseManager import _get_storage_paths, DatabaseManager
from ..models.worker_source_pipeline_detection import WorkerSourcePipelineDetectionEntity


class WorkerSourcePipelineDetectionRepository:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.session: Session = self.db_manager.get_session("default")
        storage_paths = _get_storage_paths()
        self.storage_dir = storage_paths["files"] / "detection_image"
        os.makedirs(self.storage_dir, exist_ok=True)

    def get_entries(self) -> list[WorkerSourcePipelineDetectionEntity]:
        self.session.expire_all()

        # Fetch new entries
        entries = self.session.query(WorkerSourcePipelineDetectionEntity)\
            .order_by(WorkerSourcePipelineDetectionEntity.created_at.asc())\
            .all()

        return entries

    def delete_entry_by_id(self, id: str):
        """
        Delete a debug entry by its ID, including the associated image file (if it exists).

        :param entry_id: The ID of the entry to delete.
        :return: True if the entry was found and deleted, False otherwise.
        """
        entry = self.session.query(WorkerSourcePipelineDetectionEntity).filter_by(id=id).first()

        if not entry:
            return

        # Delete image file if it exists
        if entry.image_path and os.path.exists(entry.image_path):
            try:
                os.remove(entry.image_path)
            except Exception as e:
                # Optional: Log or handle file deletion error
                print(f"Failed to delete image file: {entry.image_path}, error: {e}")

        # Delete DB entry
        self.session.delete(entry)
        self.session.commit()

