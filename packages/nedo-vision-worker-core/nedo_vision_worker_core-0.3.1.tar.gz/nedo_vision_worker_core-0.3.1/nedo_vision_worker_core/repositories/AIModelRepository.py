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
            self.session.expire_all()
            models = self.session.query(AIModelEntity).all()
            
            for model in models:
                self.session.expunge(model)

            return models
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving models: {e}")
            return []