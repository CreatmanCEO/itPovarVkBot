import re
from datetime import datetime
from typing import Optional

class PhoneNumberHelper:
    """Вспомогательный класс для работы с телефонными номерами"""
    @staticmethod
    def format_phone(phone: str) -> str:
        """
        Форматирование номера телефона в единый формат
        Input: 89991234567 или +79991234567
        Output: +7 (999) 123-45-67
        """
        # Очищаем от всего кроме цифр
        digits = re.sub(r'\D', '', phone)
        
        # Если начинается с 8, заменяем на 7
        if len(digits) == 11 and digits[0] == '8':
            digits = '7' + digits[1:]
        
        # Если нет 7 в начале, добавляем
        if len(digits) == 10:
            digits = '7' + digits
            
        # Если номер некорректной длины, возвращаем как есть
        if len(digits) != 11:
            return phone
            
        return f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """
        Проверка валидности номера телефона
        Допустимые форматы:
        - 9991234567 (10 цифр)
        - 89991234567 (11 цифр)
        - +79991234567 (11 цифр с плюсом)
        """
        digits = re.sub(r'\D', '', phone)
        if len(digits) == 10:
            return True
        if len(digits) == 11 and digits[0] in ['7', '8']:
            return True
        return False

class DateTimeHelper:
    """Вспомогательный класс для работы с датами и временем"""
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """Форматирование даты и времени"""
        return dt.strftime("%d.%m.%Y %H:%M")

    @staticmethod
    def get_readable_delta(dt: datetime) -> str:
        """
        Получение читаемой разницы во времени
        Например: "5 минут назад", "2 часа назад", "вчера"
        """
        now = datetime.now()
        delta = now - dt
        
        if delta.days > 30:
            return dt.strftime("%d.%m.%Y")
        elif delta.days > 1:
            return f"{delta.days} {'день' if delta.days == 1 else 'дня' if 1 < delta.days < 5 else 'дней'} назад"
        elif delta.days == 1:
            return "вчера"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            return f"{hours} {'час' if hours == 1 else 'часа' if 1 < hours < 5 else 'часов'} назад"
        elif delta.seconds >= 60:
            minutes = delta.seconds // 60
            return f"{minutes} {'минуту' if minutes == 1 else 'минуты' if 1 < minutes < 5 else 'минут'} назад"
        else:
            return "только что"

    @staticmethod
    def is_expired(dt: datetime, hours: int = 24) -> bool:
        """Проверка, прошло ли указанное количество часов"""
        return (datetime.now() - dt).total_seconds() > hours * 3600

class TextHelper:
    """Вспомогательный класс для работы с текстом"""
    @staticmethod
    def clean_text(text: str) -> str:
        """Очистка текста от лишних пробелов и переносов строк"""
        if not text:
            return ""
        # Заменяем множественные пробелы и переносы на одиночные
        return ' '.join(text.split())

    @staticmethod
    def truncate(text: str, length: int = 100, suffix: str = "...") -> str:
        """Сокращение текста до определенной длины"""
        if not text:
            return ""
        if len(text) <= length:
            return text
        truncated = text[:length - len(suffix)].rsplit(' ', 1)[0]
        return truncated + suffix

    @staticmethod
    def sanitize_html(text: str) -> str:
        """Удаление HTML-тегов из текста"""
        if not text:
            return ""
        return re.sub(r'<[^>]+>', '', text)

class OrderHelper:
    """Вспомогательный класс для работы с заявками"""
    @staticmethod
    def generate_order_number(order_id: int) -> str:
        """
        Генерация читаемого номера заявки
        Формат: VK-2024-0001
        """
        return f"VK-{datetime.now().year}-{order_id:04d}"

    @staticmethod
    def format_order_status(status: str) -> str:
        """Получение читаемого статуса заявки"""
        statuses = {
            'new': 'Новая',
            'in_progress': 'В работе',
            'completed': 'Завершена',
            'deleted': 'Удалена',
            'updated': 'Обновлена',
            'cancelled': 'Отменена'
        }
        return statuses.get(status.lower(), status)

    @staticmethod
    def get_status_emoji(status: str) -> str:
        """Получение эмодзи для статуса заявки"""
        emojis = {
            'new': '🆕',
            'in_progress': '⚡',
            'completed': '✅',
            'deleted': '❌',
            'updated': '📝',
            'cancelled': '🚫'
        }
        return emojis.get(status.lower(), '❓')

    @staticmethod
    def is_valid_order_id(order_id: str) -> bool:
        """Проверка валидности ID заявки из текста"""
        try:
            if not order_id.startswith('№'):
                return False
            order_num = int(order_id[1:])
            return order_num > 0
        except (ValueError, IndexError):
            return False