import os
import logging
from typing import Optional
from .model_load_balancer import ModelLoadBalancer

model_balancer = None

def init_load_balancer(
    config_path: Optional[str] = None, 
    logger: Optional[logging.Logger] = None
):
    """
    Initializes the global ModelLoadBalancer instance.

    This function is idempotent. If the balancer is already initialized,
    it does nothing. It follows a safe initialization pattern where the
    global instance is only assigned after successful configuration loading.
    
    Args:
        config_path (Optional[str]): The path to the model configuration file.
            If not provided, it's determined by the `MODEL_CONFIG_PATH`
            environment variable, or defaults to "config/models_config.json".
        logger (Optional[logging.Logger]): An optional logger instance to be
            used by the model balancer.
    """
    global model_balancer
    if model_balancer is None:
        # Use parameter if provided, otherwise check env var, then default
        final_config_path = config_path or os.getenv(
            "MODEL_CONFIG_PATH", 
            "config/models_config.json"
        )
        try:
            # 1. Create a local instance first.
            balancer = ModelLoadBalancer(
                config_path=final_config_path, 
                logger=logger
            )
            # 2. Attempt to load its configuration.
            balancer.load_config()
            # 3. Only assign to the global variable on full success.
            model_balancer = balancer
        except Exception as e:
            # If any step fails, the global model_balancer remains None,
            # allowing for another initialization attempt later.
            # Re-raise the exception to notify the caller of the failure.
            raise RuntimeError(f"Failed to initialize and configure ModelLoadBalancer from {final_config_path}: {e}") from e

def get_model_balancer() -> ModelLoadBalancer:
    if model_balancer is None:
        raise RuntimeError("ModelLoadBalancer not initialized. Please call init_load_balancer() first.")
    return model_balancer
