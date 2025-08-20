import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models.dataset_source import DatasetSourceEntity
from ..database.DatabaseManager import DatabaseManager

logger = logging.getLogger(__name__)

class DatasetSourceRepository:
    """Repository for managing dataset source data using SQLAlchemy."""
    
    def __init__(self):
        """Initialize the repository."""
        self.db_manager = DatabaseManager()
        self.session: Session = self.db_manager.get_session("default")
    
    def sync_dataset_sources(self, dataset_sources_data, update_callback=None):
        """
        Synchronize dataset sources from server data with intelligent change detection.
        
        Args:
            dataset_sources_data: List of dataset source data from server
            update_callback: Optional callback function for status updates
        """
        try:
            # Get existing dataset sources from local database
            local_dataset_sources = {ds.id: ds for ds in self.session.query(DatasetSourceEntity).all()}
            
            new_dataset_sources = []
            updated_dataset_sources = []
            changed_dataset_sources = []
            server_dataset_source_ids = set()

            for dataset_source_data in dataset_sources_data:
                server_dataset_source_ids.add(dataset_source_data.id)
                existing_dataset_source = local_dataset_sources.get(dataset_source_data.id)
                changes = []

                if existing_dataset_source:
                    # Check for changes in each field
                    if existing_dataset_source.dataset_id != dataset_source_data.dataset_id:
                        changes.append(f"dataset_id: {existing_dataset_source.dataset_id} → {dataset_source_data.dataset_id}")
                    if existing_dataset_source.worker_source_id != dataset_source_data.worker_source_id:
                        changes.append(f"worker_source_id: {existing_dataset_source.worker_source_id} → {dataset_source_data.worker_source_id}")
                    if existing_dataset_source.sampling_interval != dataset_source_data.sampling_interval:
                        changes.append(f"sampling_interval: {existing_dataset_source.sampling_interval} → {dataset_source_data.sampling_interval}")
                    if existing_dataset_source.dataset_name != dataset_source_data.dataset_name:
                        changes.append(f"dataset_name: '{existing_dataset_source.dataset_name}' → '{dataset_source_data.dataset_name}'")
                    if existing_dataset_source.worker_source_name != dataset_source_data.worker_source_name:
                        changes.append(f"worker_source_name: '{existing_dataset_source.worker_source_name}' → '{dataset_source_data.worker_source_name}'")
                    if existing_dataset_source.worker_source_url != dataset_source_data.worker_source_url:
                        changes.append(f"worker_source_url: '{existing_dataset_source.worker_source_url}' → '{dataset_source_data.worker_source_url}'")

                    if changes:
                        # Update existing record
                        existing_dataset_source.dataset_id = dataset_source_data.dataset_id
                        existing_dataset_source.worker_source_id = dataset_source_data.worker_source_id
                        existing_dataset_source.sampling_interval = dataset_source_data.sampling_interval
                        existing_dataset_source.dataset_name = dataset_source_data.dataset_name
                        existing_dataset_source.worker_source_name = dataset_source_data.worker_source_name
                        existing_dataset_source.worker_source_url = dataset_source_data.worker_source_url
                        updated_dataset_sources.append(existing_dataset_source)
                        changed_dataset_sources.append(f"🔄 [APP] [UPDATE] Dataset Source ID {dataset_source_data.id}: " + ", ".join(changes))
                else:
                    # Create new record
                    new_dataset_source = DatasetSourceEntity(
                        id=dataset_source_data.id,
                        dataset_id=dataset_source_data.dataset_id,
                        worker_source_id=dataset_source_data.worker_source_id,
                        sampling_interval=dataset_source_data.sampling_interval,
                        dataset_name=dataset_source_data.dataset_name,
                        worker_source_name=dataset_source_data.worker_source_name,
                        worker_source_url=dataset_source_data.worker_source_url
                    )
                    new_dataset_sources.append(new_dataset_source)
                    logger.info(f"🆕 [APP] [INSERT] Added Dataset Source ID {dataset_source_data.id} - {dataset_source_data.dataset_name}")

            # Identify and delete dataset sources not in the server response
            records_to_delete = [
                dataset_source for dataset_source_id, dataset_source in local_dataset_sources.items()
                if dataset_source_id not in server_dataset_source_ids
            ]

            # Perform batch operations in a single transaction
            if new_dataset_sources:
                self.session.bulk_save_objects(new_dataset_sources)  # Bulk insert

            if updated_dataset_sources:
                self.session.bulk_save_objects(updated_dataset_sources)  # Bulk update

            if records_to_delete:
                for record in records_to_delete:
                    self.session.delete(record)  # Mark for deletion
                    logger.info(f"❌ [APP] [DELETE] Dataset Source ID {record.id} - {record.dataset_name}")

            self.session.commit()  # Commit once (reducing DB round trips)

            # Log all changes
            for change in changed_dataset_sources:
                logger.info(change)
                
            if new_dataset_sources or updated_dataset_sources or records_to_delete:
                logger.info(f"✅ [APP] Synced {len(dataset_sources_data)} dataset sources (Added: {len(new_dataset_sources)}, Updated: {len(updated_dataset_sources)}, Deleted: {len(records_to_delete)})")
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"🚨 [APP] Database error while syncing dataset sources: {e}", exc_info=True)
        except Exception as e:
            self.session.rollback()
            logger.error(f"🚨 [APP] Error syncing dataset sources: {e}")
    
    def get_all_dataset_sources(self) -> List[DatasetSourceEntity]:
        """Get all dataset sources from local database."""
        try:
            dataset_sources = self.session.query(DatasetSourceEntity).all()
            return dataset_sources
            
        except SQLAlchemyError as e:
            logger.error(f"🚨 [APP] Database error while fetching dataset sources: {e}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"🚨 [APP] Error fetching dataset sources: {e}")
            return []
    
    def get_dataset_source_by_id(self, dataset_source_id: str) -> Optional[DatasetSourceEntity]:
        """Get a specific dataset source by ID."""
        try:
            dataset_source = self.session.query(DatasetSourceEntity).filter_by(id=dataset_source_id).first()
            return dataset_source
            
        except SQLAlchemyError as e:
            logger.error(f"🚨 [APP] Database error while fetching dataset source by ID {dataset_source_id}: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"🚨 [APP] Error fetching dataset source by ID {dataset_source_id}: {e}")
            return None
    
    def get_dataset_sources_by_worker_source_id(self, worker_source_id: str) -> List[DatasetSourceEntity]:
        """Get all dataset sources for a specific worker source."""
        try:
            dataset_sources = self.session.query(DatasetSourceEntity).filter_by(worker_source_id=worker_source_id).all()
            return dataset_sources
            
        except SQLAlchemyError as e:
            logger.error(f"🚨 [APP] Database error while fetching dataset sources by worker source ID {worker_source_id}: {e}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"🚨 [APP] Error fetching dataset sources by worker source ID {worker_source_id}: {e}")
            return [] 