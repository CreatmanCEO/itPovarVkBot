import os
from datetime import datetime

# Токены
VK_TOKEN = "vk1.a.KX1Q0v6Y3C420UgfV7zPoDL4V1OOYdengHYQjQyh_MtFvYca-M_871lyF0-g_qe-9Hn-MNA02wU73OjyBvX9uhh9aM9Afp7wbiBupahqPAoPoUZnEFC-BArLAYJCzX6PpN5sNnlw_qS5HlN9OASoNrvbJ2PFkIF48Dn9uqMG4zB995jvF4sk100fSSHiL5HlgclOrOs7qovLJKeyulnm8A"
VK_GROUP_ID = 228564877
TELEGRAM_WEBHOOK = "https://telegram-form.creatmanick-850.workers.dev"

# Настройки приложения
APP_HOST = "0.0.0.0"
APP_PORT = 5000
MAX_ORDERS = 5  # Максимальное количество активных заявок для пользователя

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDERS_FILE = os.path.join(BASE_DIR, 'data', 'orders.json')

# Создаем директорию для данных, если её нет
os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)