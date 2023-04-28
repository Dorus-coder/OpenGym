from layoutenv.envs.example import get_logger_from_config
from pathlib import Path

logger = get_logger_from_config(Path(r'layoutenv_pkg\\src\\configs\\log_config.yaml'), 'file')

logger.debug('debug message')
logger.info('info message')
logger.warning('this is a warning')
logger.critical('this is critical')
logger.error('this is a errror')
