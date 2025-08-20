# Import all models to ensure they are registered with SQLAlchemy Base registry
from .ai_model import AIModelEntity
from .auth import AuthEntity
from .config import ConfigEntity
from .dataset_source import DatasetSourceEntity
from .logs import LogEntity
from .ppe_detection import PPEDetectionEntity
from .ppe_detection_label import PPEDetectionLabelEntity
from .restricted_area_violation import RestrictedAreaViolationEntity
from .user import UserEntity
from .worker_source import WorkerSourceEntity
from .worker_source_pipeline import WorkerSourcePipelineEntity
from .worker_source_pipeline_config import WorkerSourcePipelineConfigEntity
from .worker_source_pipeline_debug import WorkerSourcePipelineDebugEntity
from .worker_source_pipeline_detection import WorkerSourcePipelineDetectionEntity 