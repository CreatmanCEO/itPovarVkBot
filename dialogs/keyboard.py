import json
from typing import List, Optional
from .states import DialogState

class KeyboardBuilder:
    @staticmethod
    def create_keyboard(buttons: List[str], one_time: bool = True, inline: bool = False) -> str:
        """
        Создание клавиатуры ВКонтакте
        
        Args:
            buttons: Список кнопок
            one_time: Скрывать ли клавиатуру после нажатия
            inline: Встроенная клавиатура или нет
        
        Returns:
            str: JSON строка с клавиатурой для VK API
        """
        keyboard = {
            "one_time": one_time,
            "inline": inline,
            "buttons": [
                [{
                    "action": {
                        "type": "text",
                        "label": str(btn)[:40]
                    },
                    "color": "primary"
                }] for btn in buttons
            ]
        }
        return json.dumps(keyboard, ensure_ascii=False)

    @classmethod
    def get_state_keyboard(cls, state: DialogState, context: Optional[dict] = None) -> str:
        """Получение клавиатуры для конкретного состояния"""
        context = context or {}
        
        if state == DialogState.START:
            buttons = ["Начать"]
        
        elif state == DialogState.MAIN_MENU:
            buttons = ["Создать заявку", "Мои заявки"]
            
        elif state == DialogState.CHOOSING_SERVICE_TYPE:
            buttons = ["Услуги Населению", "Услуги для Бизнеса", "Назад"]
            
        elif state == DialogState.VIEWING_ORDERS:
            # Формируем кнопки на основе активных заявок
            buttons = ["Создать новую заявку"]
            orders = context.get('orders', [])
            buttons.extend([f"Заявка №{order['id']}" for order in orders])
            buttons.append("Назад в меню")
            
        elif state == DialogState.ORDER_MANAGEMENT:
            buttons = ["Изменить заявку", "Удалить заявку", "Назад к заявкам"]
            
        elif state == DialogState.ORDER_CONFIRMATION:
            buttons = ["Отправить заявку", "Изменить заявку"]
            
        elif state == DialogState.BUSINESS_TYPE_INPUT:
            buttons = ["Назад"]
            
        elif state == DialogState.BUSINESS_TASK_INPUT:
            buttons = ["Назад к описанию компании"]
            
        elif state == DialogState.PERSONAL_TASK_INPUT:
            buttons = ["Назад к выбору услуг"]
            
        elif state == DialogState.CONTACT_INPUT:
            buttons = ["Назад"]
            
        else:
            buttons = []

        # Добавляем кнопку отмены для определенных состояний
        if state in [
            DialogState.BUSINESS_TYPE_INPUT,
            DialogState.BUSINESS_TASK_INPUT,
            DialogState.PERSONAL_TASK_INPUT,
            DialogState.CONTACT_INPUT
        ]:
            buttons.append("Отменить заявку")

        return cls.create_keyboard(buttons)

    @classmethod
    def get_empty_keyboard(cls) -> str:
        """Пустая клавиатура"""
        return json.dumps({"buttons": [], "one_time": True})

# Предустановленные клавиатуры для часто используемых состояний
MAIN_MENU_KEYBOARD = KeyboardBuilder.get_state_keyboard(DialogState.MAIN_MENU)
SERVICE_TYPE_KEYBOARD = KeyboardBuilder.get_state_keyboard(DialogState.CHOOSING_SERVICE_TYPE)
CONFIRMATION_KEYBOARD = KeyboardBuilder.get_state_keyboard(DialogState.ORDER_CONFIRMATION)