import yaml
import logging
import os

def setup_logging():
    """Configures the root logger and silences noisy libraries."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.getLogger('pydriller').setLevel(logging.WARNING)

def load_config_and_prepare_dirs(config_path="config.yaml"):
    """
    Loads YAML config, sets up logging, and creates necessary directories.
    
    Args:
        config_path (str): Path to the configuration file.
        
    Returns:
        dict: The loaded configuration.
    """
    setup_logging()
    
    logger = logging.getLogger(__name__)
    logger.info(f"Loading configuration from {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Ensure output directories exist
    os.makedirs(config['results_dir'], exist_ok=True)
    os.makedirs(config['clone_dir'], exist_ok=True)
    logger.info(f"Ensured results directory '{config['results_dir']}' and clone directory '{config['clone_dir']}' exist.")
    
    return config