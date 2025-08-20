from sqlalchemy.orm import Session
from ..database.DatabaseManager import DatabaseManager
from ..models.worker_source import WorkerSourceEntity


class WorkerSourceRepository:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.session: Session = self.db_manager.get_session("config")

    def get_worker_sources(self):
        """
        Fetch all worker sources from the local database in a single query.

        Returns:
            list: A list of WorkerSourceEntity records.
        """
        self.session.expire_all()
        return self.session.query(WorkerSourceEntity).all()
