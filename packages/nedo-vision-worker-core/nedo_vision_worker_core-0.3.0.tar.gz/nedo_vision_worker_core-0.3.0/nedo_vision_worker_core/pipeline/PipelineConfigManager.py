from ..repositories.WorkerSourcePipelineRepository import WorkerSourcePipelineRepository


class PipelineConfigManager:
    def __init__(self):
        self.config_repository = WorkerSourcePipelineRepository()
        self.config = {}
    
    def update(self, pipeline_id):
        self.config = self.config_repository.get_pipeline_configs_by_pipeline_id(pipeline_id)

    def is_feature_enabled(self, feature_name):
        """
        Generic method to check if a feature is enabled in configuration.
        
        :param feature_name: Name of the feature to check
        :return: True if feature is enabled, False otherwise
        """
        return (feature_name in self.config and 
                self.config[feature_name].get("is_enabled", False))
    
    def get_feature_config(self, feature_name, default = {}) -> dict:
        """
        Get the configuration for a specific feature.
        
        :param feature_name: Name of the feature
        :return : Feature configuration
        """
        if not self.is_feature_enabled(feature_name):
            return default

        return self.config[feature_name].get("value", default)
