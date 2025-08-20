import logging
from sqlalchemy.orm import Session 
from sqlalchemy.exc import SQLAlchemyError
from ..database.DatabaseManager import DatabaseManager
from ..protos.WorkerSourcePipelineService_pb2 import WorkerSourcePipelineListResponse
from ..models.worker_source_pipeline import WorkerSourcePipelineEntity
from ..models.worker_source_pipeline_config import WorkerSourcePipelineConfigEntity

logger = logging.getLogger(__name__)

class WorkerSourcePipelineRepository:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.session: Session = self.db_manager.get_session("config")

    def sync_worker_source_pipelines(self, response: WorkerSourcePipelineListResponse, on_status_update):
        """
        Synchronize worker source pipelines from the server with the local database.
        This includes both WorkerSourcePipelineEntity and WorkerSourcePipelineConfigEntity.

        Args:
            response (WorkerSourcePipelineListResponse): The gRPC response containing worker source pipeline data.
        """
        try:
            local_pipelines = {pipeline.id: pipeline for pipeline in self.session.query(WorkerSourcePipelineEntity).all()}
            local_pipeline_configs = {config.id: config for config in self.session.query(WorkerSourcePipelineConfigEntity).all()}

            new_pipelines = []
            updated_pipelines = []
            new_pipeline_configs = []
            updated_pipeline_configs = []
            changed_pipelines = []
            changed_configs = []
            server_pipeline_ids = set()
            server_pipeline_config_ids = set()

            for pipeline in response.data:
                server_pipeline_ids.add(pipeline.id)
                existing_pipeline = local_pipelines.get(pipeline.id)
                changes = []

                if existing_pipeline:
                    if existing_pipeline.name != pipeline.name:
                        changes.append(f"name: '{existing_pipeline.name}' → '{pipeline.name}'")
                    if existing_pipeline.worker_source_id != pipeline.worker_source_id:
                        changes.append(f"worker_source_id: {existing_pipeline.worker_source_id} → {pipeline.worker_source_id}")
                    if existing_pipeline.worker_id != pipeline.worker_id:
                        changes.append(f"worker_id: {existing_pipeline.worker_id} → {pipeline.worker_id}")
                    if existing_pipeline.ai_model_id != pipeline.ai_model_id:
                        changes.append(f"ai_model_id: {existing_pipeline.ai_model_id} → {pipeline.ai_model_id}")
                    if existing_pipeline.location_name != pipeline.location_name:
                        changes.append(f"location_name: {existing_pipeline.location_name} → {pipeline.location_name}")
                    if existing_pipeline.pipeline_status_code != pipeline.pipeline_status_code and existing_pipeline.pipeline_status_code != "restart":
                        on_status_update(pipeline.id, existing_pipeline.pipeline_status_code)

                    if changes:
                        existing_pipeline.name = pipeline.name
                        existing_pipeline.worker_source_id = pipeline.worker_source_id
                        existing_pipeline.worker_id = pipeline.worker_id
                        existing_pipeline.ai_model_id = pipeline.ai_model_id
                        existing_pipeline.location_name = pipeline.location_name
                        updated_pipelines.append(existing_pipeline)
                        changed_pipelines.append(f"🔄 [APP] [UPDATE] Worker Source Pipeline ID {pipeline.id}: " + ", ".join(changes))
                else:
                    new_pipelines.append(WorkerSourcePipelineEntity(
                        id=pipeline.id,
                        name=pipeline.name,
                        worker_source_id=pipeline.worker_source_id,
                        worker_id=pipeline.worker_id,
                        ai_model_id=pipeline.ai_model_id,
                        pipeline_status_code=pipeline.pipeline_status_code,
                        location_name=pipeline.location_name
                    ))
                    logger.info(f"🆕 [APP] [INSERT] Added Worker Source Pipeline ID {pipeline.id} - {pipeline.name}")

                for config in pipeline.worker_source_pipeline_configs:
                    server_pipeline_config_ids.add(config.id)
                    existing_config = local_pipeline_configs.get(config.id)
                    config_changes = []

                    if existing_config:
                        if existing_config.worker_source_pipeline_id != config.worker_source_pipeline_id:
                            config_changes.append(f"worker_source_pipeline_id: {existing_config.worker_source_pipeline_id} → {config.worker_source_pipeline_id}")
                        if existing_config.pipeline_config_id != config.pipeline_config_id:
                            config_changes.append(f"pipeline_config_id: {existing_config.pipeline_config_id} → {config.pipeline_config_id}")
                        if existing_config.is_enabled != config.is_enabled:
                            config_changes.append(f"is_enabled: {existing_config.is_enabled} → {config.is_enabled}")
                        if existing_config.value != config.value:
                            config_changes.append(f"value: '{existing_config.value}' → '{config.value}'")
                        if existing_config.pipeline_config_name != config.pipeline_config.name:
                            config_changes.append(f"pipeline_config_name: '{existing_config.pipeline_config_name}' → '{config.pipeline_config.name}'")
                        if existing_config.pipeline_config_code != config.pipeline_config.code:
                            config_changes.append(f"pipeline_config_code: '{existing_config.pipeline_config_code}' → '{config.pipeline_config.code}'")

                        if config_changes:
                            existing_config.worker_source_pipeline_id = config.worker_source_pipeline_id
                            existing_config.pipeline_config_id = config.pipeline_config_id
                            existing_config.is_enabled = config.is_enabled
                            existing_config.value = config.value
                            existing_config.pipeline_config_name = config.pipeline_config.name
                            existing_config.pipeline_config_code = config.pipeline_config.code
                            updated_pipeline_configs.append(existing_config)
                            changed_configs.append(f"🔄 [APP] [UPDATE] Worker Source Pipeline Config ID {config.id}: " + ", ".join(config_changes))
                    else:
                        new_pipeline_configs.append(WorkerSourcePipelineConfigEntity(
                            id=config.id,
                            worker_source_pipeline_id=config.worker_source_pipeline_id,
                            pipeline_config_id=config.pipeline_config_id,
                            is_enabled=config.is_enabled,
                            value=config.value,
                            pipeline_config_name=config.pipeline_config.name,
                            pipeline_config_code=config.pipeline_config.code
                        ))
                        logger.info(f"🆕 [APP] [INSERT] Added Worker Source Pipeline Config ID {config.id}")

            self.session.commit()

            for change in changed_pipelines:
                logger.info(change)
            for change in changed_configs:
                logger.info(change)

            # Identify and delete pipelines not in the server response
            records_to_delete = [
                pipeline for pipeline_id, pipeline in local_pipelines.items()
                if pipeline_id not in server_pipeline_ids
            ]

            # Identify and delete pipeline configs not in the server response
            configs_to_delete = [
                config for config_id, config in local_pipeline_configs.items()
                if config_id not in server_pipeline_config_ids
            ]

            # Perform batch insert, update, and delete in a single transaction
            if new_pipelines:
                self.session.bulk_save_objects(new_pipelines)  # Bulk insert

            if updated_pipelines:
                self.session.bulk_save_objects(updated_pipelines)  # Bulk update

            if new_pipeline_configs:
                self.session.bulk_save_objects(new_pipeline_configs)  # Bulk insert configs

            if updated_pipeline_configs:
                self.session.bulk_save_objects(updated_pipeline_configs)  # Bulk update configs

            if records_to_delete:
                for record in records_to_delete:
                    self.session.delete(record)  # Mark for deletion
                    logger.info(f"❌ [APP] [DELETE] Worker Source Pipeline ID {record.id} - {record.name}")

            if configs_to_delete:
                for config in configs_to_delete:
                    self.session.delete(config)  # Mark for deletion

            self.session.commit()  # Commit once (reducing DB round trips)
        
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"❌ [APP] [DATABASE ERROR] Error during sync: {e}", exc_info=True)

    def get_worker_source_pipelines(self):
        try:
            return self.session.query(WorkerSourcePipelineEntity).all()
        except Exception as e:
            logger.error(f"🚨 [APP] Database error while fetching worker source pipelines: {e}", exc_info=True)
            return []
        
    def get_worker_source_pipeline(self, pipeline_id):
        try:
            return self.session.query(WorkerSourcePipelineEntity).filter_by(id=pipeline_id).first()
        except Exception as e:
            logger.error(f"🚨 [APP] Database error while fetching worker source pipeline: {e}", exc_info=True)