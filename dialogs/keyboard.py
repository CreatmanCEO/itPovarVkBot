"""
Модуль для создания и управления клавиатурами бота.

Этот модуль предоставляет инструменты для создания клавиатур ВКонтакте
с учетом текущего состояния диалога и контекста пользователя.

Основные компоненты:
- KeyboardBuilder: Класс для создания клавиатур
- Предустановленные клавиатуры для часто используемых состояний

Особенности:
- Автоматическое разбиение кнопок на ряды
- Цветовое оформление кнопок навигации
- Контекстно-зависимые клавиатуры
- Поддержка inline-клавиатур
"""

import json
from typing import List, Optional
from .states import DialogState, OrderStatus

class KeyboardBuilder:
    """
    Класс для создания клавиатур ВКонтакте.
    
    Этот класс предоставляет методы для генерации JSON-строк,
    описывающих клавиатуры для разных состояний диалога.
    
    Особенности:
    - Автоматическое разбиение кнопок на ряды по 2 кнопки
    - Разные цвета для основных и навигационных кнопок
    - Поддержка контекстно-зависимых клавиатур
    - Возможность создания пустых клавиатур
    
    Пример использования:
    ```python
    # Создание простой клавиатуры
    keyboard = KeyboardBuilder.create_keyboard(["Кнопка 1", "Кнопка 2"])
    
    # Получение клавиатуры для состояния
    state_keyboard = KeyboardBuilder.get_state_keyboard(
        DialogState.MAIN_MENU,
        context={'user_id': 123}
    )
    ```
    """
    
    @staticmethod
    def create_keyboard(buttons: List[str], one_time: bool = True, inline: bool = False) -> str:
        """
        Создание клавиатуры ВКонтакте.
        
        Args:
            buttons: Список текстов кнопок
            one_time: Скрывать ли клавиатуру после нажатия
            inline: Встроенная клавиатура или нет
        
        Returns:
            str: JSON строка с клавиатурой для VK API
        
        Пример:
        ```python
        keyboard = KeyboardBuilder.create_keyboard(
            ["Да", "Нет", "Отмена"],
            one_time=True
        )
        ```
        """
        # Разбиваем кнопки на ряды по 2 кнопки
        button_rows = []
        current_row = []
        
        for btn in buttons:
            current_row.append({
                "action": {
                    "type": "text",
                    "label": str(btn)[:40]
                },
                "color": "primary" if btn not in ["Отменить", "Назад", "Отмена"] else "secondary"
            })
            
            if len(current_row) == 2:
                button_rows.append(current_row)
                current_row = []
        
        if current_row:
            button_rows.append(current_row)

        keyboard = {
            "one_time": one_time,
            "inline": inline,
            "buttons": button_rows
        }
        return json.dumps(keyboard, ensure_ascii=False)

    @classmethod
    def get_state_keyboard(cls, state: DialogState, context: Optional[dict] = None) -> str:
        """
        Получение клавиатуры для конкретного состояния диалога.
        
        Args:
            state: Текущее состояние диалога
            context: Контекст пользователя (опционально)
        
        Returns:
            str: JSON строка с клавиатурой
        
        Особенности:
        - Для каждого состояния своя клавиатура
        - Учет контекста пользователя
        - Добавление навигационных кнопок
        - Поддержка глобальных команд
        
        Пример:
        ```python
        # Клавиатура для просмотра заявок
        keyboard = KeyboardBuilder.get_state_keyboard(
            DialogState.VIEWING_ORDERS,
            context={'orders': [{'id': 1}, {'id': 2}]}
        )
        ```
        """
        context = context or {}
        
        if state == DialogState.START:
            buttons = ["Начать", "English", "Помощь"]
        
        elif state == DialogState.MAIN_MENU:
            buttons = [
                "Создать заявку",
                "Мои заявки",
                "Помощь",
                "Сменить язык"
            ]
            
        elif state == DialogState.HELP:
            buttons = [
                "Создать заявку",
                "Мои заявки",
                "Сменить язык",
                "Назад в меню"
            ]
            
        elif state == DialogState.LANGUAGE_SELECTION:
            buttons = ["Русский", "English", "Назад в меню"]
            
        elif state == DialogState.CHOOSING_SERVICE_TYPE:
            buttons = [
                "Услуги Населению",
                "Услуги для Бизнеса",
                "Помощь",
                "Назад в меню"
            ]
            
        elif state == DialogState.VIEWING_ORDERS:
            buttons = [
                "Создать новую заявку",
                "Фильтр заявок",
                "История заявок"
            ]
            # Добавляем кнопки активных заявок
            orders = context.get('orders', [])
            if orders:
                buttons[1:1] = [f"Заявка №{order['id']}" for order in orders]
            buttons.extend(["Назад в меню", "Помощь"])
            
        elif state == DialogState.ORDERS_FILTER:
            buttons = [
                "Все заявки",
                "Активные",
                "Завершенные",
                "Отмененные",
                "Назад к заявкам",
                "В главное меню"
            ]
            
        elif state == DialogState.ORDER_HISTORY:
            buttons = ["Назад к заявкам", "В главное меню"]
            # Добавляем кнопки истории заявок
            history = context.get('history', [])
            if history:
                buttons[0:0] = [f"Заявка №{order['id']}" for order in history]
            
        elif state == DialogState.ORDER_MANAGEMENT:
            buttons = [
                "Изменить заявку",
                "Оставить отзыв",
                "Отменить заявку",
                "Назад к заявкам",
                "В главное меню"
            ]
            
        elif state == DialogState.ORDER_CONFIRMATION:
            buttons = [
                "Отправить заявку",
                "Изменить заявку",
                "Отменить",
                "В главное меню"
            ]
            
        elif state == DialogState.ORDER_FEEDBACK:
            buttons = ["1", "2", "3", "4", "5", "Пропустить", "Назад", "В главное меню"]
            
        elif state == DialogState.CONTACT_INPUT_RETRY:
            buttons = ["Ввести заново", "Отменить", "В главное меню"]
            
        elif state == DialogState.ERROR_HANDLING:
            buttons = [
                "Повторить",
                "Помощь",
                "В главное меню"
            ]
            
        elif state == DialogState.CANCEL_CONFIRMATION:
            buttons = ["Да, отменить", "Нет, продолжить", "В главное меню"]
            
        elif state in [
            DialogState.BUSINESS_TYPE_INPUT,
            DialogState.BUSINESS_TASK_INPUT,
            DialogState.PERSONAL_TASK_INPUT,
            DialogState.CONTACT_INPUT
        ]:
            buttons = ["Назад", "Отменить заявку", "В главное меню"]
            
        elif state == DialogState.FINISHED:
            buttons = ["Создать заявку", "В главное меню"]
            
        else:
            buttons = ["В главное меню"]

        return cls.create_keyboard(buttons)

    @classmethod
    def get_empty_keyboard(cls) -> str:
        """
        Создание пустой клавиатуры.
        
        Returns:
            str: JSON строка с пустой клавиатурой
        
        Используется в случаях, когда нужно скрыть клавиатуру
        или когда ввод с клавиатуры не требуется.
        """
        return json.dumps({"buttons": [], "one_time": True})


# Предустановленные клавиатуры для часто используемых состояний
MAIN_MENU_KEYBOARD = KeyboardBuilder.get_state_keyboard(DialogState.MAIN_MENU)
SERVICE_TYPE_KEYBOARD = KeyboardBuilder.get_state_keyboard(DialogState.CHOOSING_SERVICE_TYPE)
CONFIRMATION_KEYBOARD = KeyboardBuilder.get_state_keyboard(DialogState.ORDER_CONFIRMATION)
HELP_KEYBOARD = KeyboardBuilder.get_state_keyboard(DialogState.HELP)
CANCEL_KEYBOARD = KeyboardBuilder.get_state_keyboard(DialogState.CANCEL_CONFIRMATION)