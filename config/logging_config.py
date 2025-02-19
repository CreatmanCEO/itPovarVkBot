import os
from logging.handlers import RotatingFileHandler
import logging

# Создаем директорию для логов, если её нет
LOGS_DIR = "logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Настройки логирования
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': os.path.join(LOGS_DIR, 'bot.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': os.path.join(LOGS_DIR, 'error.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        }
    },
    'loggers': {
        '': {  # Корневой логгер
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        },
        'bot': {  # Логгер бота
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'web': {  # Логгер веб-сервера
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

def setup_logging():
    """Настройка системы логирования"""
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Создаем логгер для бота
    logger = logging.getLogger('bot')
    logger.info('Логирование настроено')
    
    return logger 