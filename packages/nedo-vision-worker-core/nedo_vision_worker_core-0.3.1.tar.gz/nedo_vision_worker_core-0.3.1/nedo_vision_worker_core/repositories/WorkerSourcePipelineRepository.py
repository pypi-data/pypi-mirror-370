import json
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..database.DatabaseManager import DatabaseManager
from ..models.worker_source_pipeline import WorkerSourcePipelineEntity
from ..models.worker_source_pipeline_config import WorkerSourcePipelineConfigEntity


class WorkerSourcePipelineRepository:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.session: Session = self.db_manager.get_session("config")

    def get_all_pipelines(self):
        """
        Fetch all worker source pipelines from the local database in a single query.

        Returns:
            list: A list of WorkerSourcePipelineEntity records.
        """
        self.session.expire_all()
        return self.session.query(WorkerSourcePipelineEntity).all()

    def get_pipeline_configs_by_pipeline_id(self, pipeline_id):
        """
        Retrieves all pipeline configurations for a given pipeline ID and returns them as a dictionary.

        The dictionary format:
        {
            "config_code_1": { "id": "xxx", "is_enabled": true, "value": "some_value", "name": "Config Name" },
            "config_code_2": { "id": "yyy", "is_enabled": false, "value": "another_value", "name": "Another Config Name" }
        }

        Args:
            pipeline_id (str): The unique identifier of the pipeline.

        Returns:
            dict: A dictionary mapping pipeline_config_code to its configuration details.
        """
        try:
            pipeline_configs = (
                self.session.query(WorkerSourcePipelineConfigEntity)
                .filter(WorkerSourcePipelineConfigEntity.worker_source_pipeline_id == pipeline_id)
                .all()
            )

            def parse_value(value):
                """Attempts to parse the value as JSON if applicable."""
                if not value:
                    return value  # Keep None or empty string as is
                
                value = value.strip()  # Remove leading/trailing spaces
                if (value.startswith("{") and value.endswith("}")) or (value.startswith("[") and value.endswith("]")):
                    try:
                        return json.loads(value)  # Parse JSON object or list
                    except json.JSONDecodeError:
                        pass  # Keep as string if parsing fails
                return value  # Return original value if not JSON

            # Convert result into a dictionary with pipeline_config_code as key
            config_dict = {
                config.pipeline_config_code: {
                    "id": config.id,
                    "is_enabled": config.is_enabled,  # Keep original boolean value
                    "value": parse_value(config.value),  # Parse JSON if applicable
                    "name": config.pipeline_config_name
                }
                for config in pipeline_configs
            }

            return config_dict

        except SQLAlchemyError as e:
            print(f"Database error while retrieving pipeline configs: {e}")
            return {}
        
    def get_worker_source_pipeline(self, pipeline_id):
        self.session.expire_all()
        return self.session.query(WorkerSourcePipelineEntity).filter_by(id=pipeline_id).first()