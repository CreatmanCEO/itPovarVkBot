import json

def create_keyboard(buttons, one_time=True):
    """
    Создание клавиатуры ВКонтакте
    
    Args:
        buttons (list): Список кнопок
        one_time (bool): Скрывать ли клавиатуру после нажатия
    
    Returns:
        str: JSON строка с клавиатурой для VK API
    """
    keyboard = {
        "one_time": one_time,
        "buttons": [[{
            "action": {
                "type": "text",
                "label": str(btn)[:40]
            },
            "color": "primary"
        }] for btn in buttons],
        "inline": False
    }
    return json.dumps(keyboard, ensure_ascii=False)

def get_order_keyboard(order_id):
    """
    Создание клавиатуры для управления заявкой
    
    Args:
        order_id (int): Номер заявки
    
    Returns:
        str: JSON строка с клавиатурой для управления заявкой
    """
    buttons = [
        "Изменить заявку",
        "Удалить заявку",
        "Назад"
    ]
    return create_keyboard(buttons)

def get_main_keyboard():
    """
    Создание главной клавиатуры
    
    Returns:
        str: JSON строка с основной клавиатурой
    """
    buttons = [
        "Услуги Населению",
        "Услуги для Бизнеса"
    ]
    return create_keyboard(buttons)