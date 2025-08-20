import logging
from .models.config import ConfigEntity
from ..database.DatabaseManager import DatabaseManager  # DatabaseManager for managing sessions


class ConfigurationManager:
    """
    A class to manage server configuration stored in the 'config' database using SQLAlchemy.
    """

    @staticmethod
    def init_database():
        """
        Initialize the 'config' database and create the `server_config` table if it doesn't exist.
        """
        try:
            DatabaseManager.init_databases()
            logging.info("Configuration database initialized successfully.")
        except Exception as e:
            logging.exception("Failed to initialize the configuration database.")
            raise RuntimeError("Database initialization failed.") from e

    @staticmethod
    def set_config(key: str, value: str):
        """
        Set or update a configuration key-value pair in the 'config' database.

        Args:
            key (str): The configuration key.
            value (str): The configuration value.
        """
        if not key or not isinstance(key, str):
            raise ValueError("The 'key' must be a non-empty string.")
        if not isinstance(value, str):
            raise ValueError("The 'value' must be a string.")

        session = None
        try:
            session = DatabaseManager.get_session("config")
            logging.info(f"Attempting to set configuration: {key} = {value}")
            existing_config = session.query(ConfigEntity).filter_by(key=key).first()
            if existing_config:
                logging.info(f"Updating configuration key: {key}")
                existing_config.value = value
            else:
                logging.info(f"Adding new configuration key: {key}")
                new_config = ConfigEntity(key=key, value=value)
                session.add(new_config)
            session.commit()
            logging.info(f"Configuration key '{key}' set successfully.")
        except Exception as e:
            if session:
                session.rollback()
            logging.exception(f"Failed to set configuration key '{key}': {e}")
            raise RuntimeError(f"Failed to set configuration key '{key}'") from e
        finally:
            if session:
                session.close()

    @staticmethod
    def set_config_batch(configs: dict):
        """
        Set or update multiple configuration key-value pairs in the 'config' database in a batch operation.

        Args:
            configs (dict): A dictionary containing configuration key-value pairs.
        """
        if not isinstance(configs, dict) or not configs:
            raise ValueError("The 'configs' parameter must be a non-empty dictionary.")

        session = None
        try:
            session = DatabaseManager.get_session("config")
            logging.info(f"Attempting to set {len(configs)} configuration keys in batch.")

            # Retrieve existing configurations
            existing_configs = session.query(ConfigEntity).filter(ConfigEntity.key.in_(configs.keys())).all()
            existing_keys = {config.key: config for config in existing_configs}

            for key, value in configs.items():
                if key in existing_keys:
                    logging.info(f"Updating configuration key: {key}")
                    existing_keys[key].value = value
                else:
                    logging.info(f"Adding new configuration key: {key}")
                    new_config = ConfigEntity(key=key, value=value)
                    session.add(new_config)

            session.commit()
            logging.info("All configuration keys set successfully.")
        except Exception as e:
            if session:
                session.rollback()
            logging.exception(f"Failed to set batch configuration keys: {e}")
            raise RuntimeError("Failed to set batch configuration keys.") from e
        finally:
            if session:
                session.close()

    @staticmethod
    def get_config(key: str) -> str:
        """
        Retrieve the value of a specific configuration key from the 'config' database.

        Args:
            key (str): The configuration key.

        Returns:
            str: The configuration value, or None if the key does not exist.
        """
        if not key or not isinstance(key, str):
            raise ValueError("The 'key' must be a non-empty string.")

        session = None
        try:
            session = DatabaseManager.get_session("config")
            logging.info(f"Retrieving configuration key: {key}")
            config = session.query(ConfigEntity).filter_by(key=key).first()
            if config:
                logging.info(f"Configuration key '{key}' retrieved successfully.")
                return config.value
            else:
                logging.warning(f"Configuration key '{key}' not found.")
                return None
        except Exception as e:
            logging.exception(f"Failed to retrieve configuration key '{key}': {e}")
            raise RuntimeError(f"Failed to retrieve configuration key '{key}'") from e
        finally:
            if session:
                session.close()

    @staticmethod
    def get_all_configs() -> dict:
        """
        Retrieve all configuration key-value pairs from the 'config' database.

        Returns:
            dict: A dictionary of all configuration key-value pairs.
        """
        session = None
        try:
            session = DatabaseManager.get_session("config")
            logging.info("Retrieving all configuration keys.")
            configs = session.query(ConfigEntity).all()
            if configs:
                logging.info("All configuration keys retrieved successfully.")
                return {config.key: config.value for config in configs}
            else:
                logging.info("No configuration keys found.")
                return {}
        except Exception as e:
            logging.exception("Failed to retrieve all configuration keys.")
            raise RuntimeError("Failed to retrieve all configuration keys.") from e
        finally:
            if session:
                session.close()

    @staticmethod
    def print_config():
        """
        Print all configuration key-value pairs to the console.
        """
        try:
            configs = ConfigurationManager.get_all_configs()
            if configs:
                print("Current Configuration:")
                for key, value in configs.items():
                    print(f"  {key}: {value}")
            else:
                print("No configuration found. Please initialize the configuration.")
        except Exception as e:
            logging.exception("Failed to print configuration keys.")
            raise RuntimeError("Failed to print configuration keys.") from e
