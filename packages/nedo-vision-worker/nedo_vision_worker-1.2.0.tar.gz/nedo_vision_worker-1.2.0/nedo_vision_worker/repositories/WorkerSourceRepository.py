import logging
from sqlalchemy.orm import Session
from ..database.DatabaseManager import DatabaseManager
from ..models.worker_source import WorkerSourceEntity

logger = logging.getLogger(__name__)

class WorkerSourceRepository:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.session: Session = self.db_manager.get_session("config")

    def get_all_worker_sources(self):
        """Retrieve all worker sources from the database."""
        try:
            return self.session.query(WorkerSourceEntity).all()
        except Exception as e:
            logger.error(f"🚨 [APP] Database error while fetching worker sources: {e}", exc_info=True)
            return []
    
    def bulk_update_worker_sources(self, updated_records):
        """Batch update worker sources in the database."""
        try:
            if not updated_records:
                logger.info("✅ [APP] No worker sources to update.")
                return

            self.session.bulk_save_objects(updated_records) 
            self.session.commit()
            logger.info(f"✅ [APP] Bulk updated {len(updated_records)} worker sources in the database.")
        except Exception as e:
            self.session.rollback()
            logger.error(f"🚨 [APP] Database error while updating worker sources: {e}", exc_info=True)

    def get_worker_source_by_id(self, worker_source_id: str):
        """Retrieve a worker source by its ID from the database."""
        try:
            worker_source = self.session.query(WorkerSourceEntity).filter_by(id=worker_source_id).first()
            if worker_source:
                return worker_source
            else:
                logger.warning(f"⚠️ [APP] Worker Source ID {worker_source_id} not found.")
                return None
        except Exception as e:
            logger.error(f"🚨 [APP] Database error while fetching worker source by ID {worker_source_id}: {e}", exc_info=True)
            return None
