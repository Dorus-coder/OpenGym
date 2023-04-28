import yaml
import logging
import logging.config
from pathlib import Path

def get_logger_from_config(name: str, logging_config_file: Path = Path(r'layoutenv_pkg\\src\\configs\\log_config.yaml')):
    with logging_config_file.open('r') as configyml:
        config_dict = yaml.safe_load(configyml)
    logging.config.dictConfig(config_dict)
    return logging.getLogger(name)


