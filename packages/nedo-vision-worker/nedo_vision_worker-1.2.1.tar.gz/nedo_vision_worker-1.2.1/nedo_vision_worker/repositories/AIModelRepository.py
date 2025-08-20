import os
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..database.DatabaseManager import DatabaseManager
from ..models.ai_model import AIModelEntity

class AIModelRepository:
    """Handles storage of AI Models into SQLite using SQLAlchemy."""

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.session: Session = self.db_manager.get_session("default")

    def get_models(self) -> list:
        """
        Retrieves all AI models from the database.

        Returns:
            list: A list of AIModelEntity objects.
        """
        try:
            models = self.session.query(AIModelEntity).all()
            return models
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving models: {e}")
            return []

    def get_model_by_id(self, model_id: str) -> AIModelEntity:
        """
        Retrieves a specific AI model by ID from the database.

        Args:
            model_id (str): The ID of the model to retrieve.

        Returns:
            AIModelEntity: The model entity if found, None otherwise.
        """
        try:
            model = self.session.query(AIModelEntity).filter(AIModelEntity.id == model_id).first()
            return model
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving model {model_id}: {e}")
            return None