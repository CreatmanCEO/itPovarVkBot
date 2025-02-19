import json
import os
from typing import Dict, Optional

class LocalizationService:
    """Сервис для работы с локализацией"""
    
    def __init__(self, locales_dir: str = "locales"):
        """
        Инициализация сервиса локализации
        
        Args:
            locales_dir (str): Путь к директории с файлами локализации
        """
        self.locales_dir = locales_dir
        self.locales: Dict[str, Dict] = {}
        self.default_locale = "ru"
        self._load_locales()
    
    def _load_locales(self) -> None:
        """Загрузка всех доступных локализаций"""
        for file in os.listdir(self.locales_dir):
            if file.endswith(".json"):
                locale = file.split(".")[0]
                with open(os.path.join(self.locales_dir, file), 'r', encoding='utf-8') as f:
                    self.locales[locale] = json.load(f)
    
    def get_text(self, key: str, locale: str = None, **kwargs) -> str:
        """
        Получение локализованного текста по ключу
        
        Args:
            key (str): Ключ текста (например, "common.welcome")
            locale (str, optional): Код языка. По умолчанию используется русский
            **kwargs: Параметры для форматирования строки
        
        Returns:
            str: Локализованный текст
        """
        locale = locale or self.default_locale
        if locale not in self.locales:
            locale = self.default_locale
            
        # Разбиваем ключ на части (например, "common.welcome" -> ["common", "welcome"])
        parts = key.split(".")
        
        # Ищем текст в словаре локализации
        current = self.locales[locale]
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                # Если ключ не найден, возвращаем ключ
                return key
        
        # Форматируем строку с переданными параметрами
        if isinstance(current, str):
            try:
                return current.format(**kwargs)
            except KeyError:
                return current
        
        return key
    
    def get_available_locales(self) -> list:
        """
        Получение списка доступных языков
        
        Returns:
            list: Список кодов доступных языков
        """
        return list(self.locales.keys())
    
    def set_default_locale(self, locale: str) -> None:
        """
        Установка языка по умолчанию
        
        Args:
            locale (str): Код языка
        """
        if locale in self.locales:
            self.default_locale = locale 