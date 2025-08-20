from datetime import datetime, timedelta, timezone
import os
from sqlalchemy.orm import Session
from ..database.DatabaseManager import DatabaseManager
from ..models.worker_source_pipeline_debug import WorkerSourcePipelineDebugEntity


class WorkerSourcePipelineDebugRepository:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.session: Session = self.db_manager.get_session("default")

    def create_debug_entry(self, uuid: str, worker_source_pipeline_id: str) -> WorkerSourcePipelineDebugEntity:
        """
        Create a new debug entry for a worker source pipeline.
        
        Args:
            uuid (str): The requester ID
            worker_source_pipeline_id (str): The ID of the worker source pipeline
            
        Returns:
            WorkerSourcePipelineDebugEntity: The created debug entry
        """
        debug_entry = WorkerSourcePipelineDebugEntity(
            uuid=uuid,
            worker_source_pipeline_id=worker_source_pipeline_id,
        )
        self.session.add(debug_entry)
        self.session.commit()
        return debug_entry

    def get_debug_entries_with_data(self) -> list[WorkerSourcePipelineDebugEntity]:
        """
        Fetch all debug entries that have non-null data, ordered by creation date (oldest first).
        
        Returns:
            list[WorkerSourcePipelineDebugEntity]: List of debug entries with data
        """
        self.session.expire_all()
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=1) 

        # Delete old entries
        old_entries = self.session.query(WorkerSourcePipelineDebugEntity)\
            .filter(
                WorkerSourcePipelineDebugEntity.data.isnot(None),
                WorkerSourcePipelineDebugEntity.created_at < cutoff_time
            ).all()

        for entry in old_entries:
            if entry.image_path and os.path.exists(entry.image_path):
                try:
                    os.remove(entry.image_path)
                except Exception as e:
                    print(f"Warning: Failed to delete image at {entry.image_path} - {e}")
            self.session.delete(entry)

        self.session.commit()

        # Fetch new entries
        entries = self.session.query(WorkerSourcePipelineDebugEntity)\
            .filter(WorkerSourcePipelineDebugEntity.data.isnot(None))\
            .order_by(WorkerSourcePipelineDebugEntity.created_at.asc())\
            .all()

        return entries

    def delete_entry_by_id(self, id: str):
        """
        Delete a debug entry by its ID, including the associated image file (if it exists).

        :param entry_id: The ID of the entry to delete.
        :return: True if the entry was found and deleted, False otherwise.
        """
        entry = self.session.query(WorkerSourcePipelineDebugEntity).filter_by(id=id).first()

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

