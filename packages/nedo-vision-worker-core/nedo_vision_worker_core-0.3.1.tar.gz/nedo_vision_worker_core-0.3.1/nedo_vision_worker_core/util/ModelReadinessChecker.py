import logging
from typing import Dict, Any
from ..models.ai_model import AIModelEntity
from ..database.DatabaseManager import DatabaseManager

logger = logging.getLogger(__name__)


class ModelReadinessChecker:
    """Utility class to check model readiness and provide detailed status information."""
    
    @staticmethod
    def check_model_readiness(model: AIModelEntity) -> Dict[str, Any]:
        """
        Comprehensive check of model readiness.
        
        Args:
            model: The AI model entity to check
            
        Returns:
            Dictionary with readiness status and details
        """
        if not model:
            return {
                "ready": False,
                "reason": "No model provided",
                "status": "none"
            }
        
        # Check download status
        if not model.is_ready_for_use():
            if model.is_downloading():
                return {
                    "ready": False,
                    "reason": f"Model {model.name} is still downloading",
                    "status": model.download_status,
                    "model_name": model.name
                }
            elif model.has_download_failed():
                return {
                    "ready": False,
                    "reason": f"Model {model.name} download failed: {model.download_error}",
                    "status": model.download_status,
                    "model_name": model.name,
                    "error": model.download_error
                }
            else:
                return {
                    "ready": False,
                    "reason": f"Model {model.name} is not ready (status: {model.download_status})",
                    "status": model.download_status,
                    "model_name": model.name
                }
        
        # Check if file exists and has content
        file_path = DatabaseManager.STORAGE_PATHS["models"] / model.file
        if not file_path.exists():
            return {
                "ready": False,
                "reason": f"Model file not found: {file_path}",
                "status": model.download_status,
                "model_name": model.name,
                "file_path": str(file_path)
            }
        
        if file_path.stat().st_size == 0:
            return {
                "ready": False,
                "reason": f"Model file is empty: {file_path}",
                "status": model.download_status,
                "model_name": model.name,
                "file_path": str(file_path)
            }
        
        return {
            "ready": True,
            "reason": "Model is ready for use",
            "status": model.download_status,
            "model_name": model.name,
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size
        }
    
    @staticmethod
    def log_model_status(model: AIModelEntity, context: str = ""):
        """
        Log detailed model status information.
        
        Args:
            model: The AI model entity to check
            context: Additional context for the log message
        """
        if not model:
            logger.warning(f"⚠️ {context}: No model provided")
            return
        
        readiness = ModelReadinessChecker.check_model_readiness(model)
        
        if readiness["ready"]:
            logger.info(f"✅ {context}: Model {model.name} is ready (size: {readiness.get('file_size', 0)} bytes)")
        else:
            if readiness["status"] == "downloading":
                logger.warning(f"⏳ {context}: {readiness['reason']}")
            elif readiness["status"] == "failed":
                logger.error(f"❌ {context}: {readiness['reason']}")
            else:
                logger.warning(f"⚠️ {context}: {readiness['reason']}")
    
    @staticmethod
    def get_models_status(models: list) -> Dict[str, Any]:
        """
        Get status summary for multiple models.
        
        Args:
            models: List of AI model entities
            
        Returns:
            Dictionary with status summary
        """
        if not models:
            return {
                "total": 0,
                "ready": 0,
                "downloading": 0,
                "failed": 0,
                "other": 0
            }
        
        summary = {
            "total": len(models),
            "ready": 0,
            "downloading": 0,
            "failed": 0,
            "other": 0,
            "details": []
        }
        
        for model in models:
            readiness = ModelReadinessChecker.check_model_readiness(model)
            summary["details"].append({
                "model_name": model.name,
                "model_id": model.id,
                "status": readiness["status"],
                "ready": readiness["ready"],
                "reason": readiness["reason"]
            })
            
            if readiness["ready"]:
                summary["ready"] += 1
            elif readiness["status"] == "downloading":
                summary["downloading"] += 1
            elif readiness["status"] == "failed":
                summary["failed"] += 1
            else:
                summary["other"] += 1
        
        return summary
    
    @staticmethod
    def log_models_summary(models: list, context: str = ""):
        """
        Log summary of multiple models status.
        
        Args:
            models: List of AI model entities
            context: Additional context for the log message
        """
        summary = ModelReadinessChecker.get_models_status(models)
        
        if summary["total"] == 0:
            logger.info(f"📊 {context}: No models available")
            return
        
        logger.info(f"📊 {context}: Models status - "
                   f"Ready: {summary['ready']}/{summary['total']}, "
                   f"Downloading: {summary['downloading']}, "
                   f"Failed: {summary['failed']}, "
                   f"Other: {summary['other']}")
        
        # Log details for non-ready models
        for detail in summary["details"]:
            if not detail["ready"]:
                if detail["status"] == "downloading":
                    logger.warning(f"⏳ {context}: {detail['reason']}")
                elif detail["status"] == "failed":
                    logger.error(f"❌ {context}: {detail['reason']}")
                else:
                    logger.warning(f"⚠️ {context}: {detail['reason']}")