import os
from pathlib import Path

# Определение базовых путей
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
LOG_DIR = BASE_DIR / 'logs'

# Создание необходимых директорий
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Токены и ID
VK_TOKEN = "vk1.a.KX1Q0v6Y3C420UgfV7zPoDL4V1OOYdengHYQjQyh_MtFvYca-M_871lyF0-g_qe-9Hn-MNA02wU73OjyBvX9uhh9aM9Afp7wbiBupahqPAoPoUZnEFC-BArLAYJCzX6PpN5sNnlw_qS5HlN9OASoNrvbJ2PFkIF48Dn9uqMG4zB995jvF4sk100fSSHiL5HlgclOrOs7qovLJKeyulnm8A"
VK_GROUP_ID = 228564877
TELEGRAM_WEBHOOK = "https://telegram-form.creatmanick-850.workers.dev"

# Настройки приложения
APP_HOST = "0.0.0.0"
APP_PORT = 5000
MAX_ORDERS = 5  # Максимальное количество активных заявок для пользователя

# Пути к файлам
DATABASE_PATH = DATA_DIR / 'orders.db'
LOG_FILE = LOG_DIR / 'bot.log'

# Настройки логирования
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
            'level': 'INFO',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': str(LOG_FILE),
            'formatter': 'detailed',
            'level': 'INFO',
        }
    },
    'loggers': {
        '': {  # Корневой логгер
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

# Настройки базы данных
DB_CONFIG = {
    'pragmas': {
        'journal_mode': 'wal',  # Для лучшей производительности
        'foreign_keys': 1,      # Включаем поддержку внешних ключей
        'cache_size': -64000    # 64MB кэш
    }
}