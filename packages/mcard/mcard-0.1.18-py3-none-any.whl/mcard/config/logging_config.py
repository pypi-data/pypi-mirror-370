import logging
import logging.config
from pathlib import Path
from .env_parameters import EnvParameters
from .config_constants import LOG_DIRECTORY, LOG_FILENAME

# Create logs directory if it doesn't exist
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
LOGS_DIR = PROJECT_ROOT / LOG_DIRECTORY
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = str(LOGS_DIR.resolve() / LOG_FILENAME)
env_parameters = EnvParameters()
LOG_LEVEL = env_parameters.get_log_level()  # Use the Singleton to get the log level

_logging_initialized = False

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE,
            'mode': 'a',
            'formatter': 'default',
            'level': env_parameters.get_log_level(),  # Use the Singleton to get the log level
            'maxBytes': 10_000_000,  # 10MB rotation as per README
            'backupCount': 5,
        },
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default',
            'level': env_parameters.get_log_level(),  # Use the Singleton to get the log level
        },
    },
    'root': {
        'level': 'WARNING',  # Set root logger to WARNING by default
        'handlers': ['file', 'console'],
    },
    'loggers': {
        'mcard': {
            'level': 'INFO',  # Set mcard logger to INFO by default
            'handlers': ['file', 'console'],
            'propagate': False,
        },
        'mcard.logging_config': {
            'level': 'DEBUG',  # Set logging_config logger to DEBUG by default for better testability
            'handlers': ['file', 'console'],
            'propagate': False,
        },
    },
}

def setup_logging():
    global _logging_initialized
    if _logging_initialized:
        return
    try:
        # Ensure the log directory exists
        if not LOGS_DIR.is_absolute():
            raise OSError(f'Invalid log directory path: {LOGS_DIR}')
        if LOGS_DIR.exists() and LOGS_DIR.is_file():
            raise OSError(f'Log directory path is a file: {LOGS_DIR}')
        if LOGS_DIR.exists() and not LOGS_DIR.is_dir():
            raise OSError(f'Invalid log directory: {LOGS_DIR}')
        if not LOGS_DIR.exists():
            LOGS_DIR.mkdir()

        # Configure logging
        logging.config.dictConfig(LOGGING_CONFIG)
        logger = logging.getLogger('mcard.logging_config')
        
        # Force all handlers to flush
        for handler in logger.handlers:
            handler.flush()
            
        logger.debug('Logging configuration has been set up.')  # Confirm logging setup
        logger.debug('Logging configuration initialized with handlers: %s', LOGGING_CONFIG['handlers'])
        logger.debug('Current log level for root: %s', LOGGING_CONFIG['root']['level'])
        
        # Set _logging_initialized to True only after successful setup
        _logging_initialized = True
    except Exception:
        raise


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
