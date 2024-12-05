def create_keyboard(buttons, one_time=True):
    """
    Создание клавиатуры ВКонтакте
    
    Args:
        buttons (list): Список кнопок
        one_time (bool): Скрывать ли клавиатуру после нажатия
    
    Returns:
        dict: Структура клавиатуры для VK API
    """
    return {
        "one_time": one_time,
        "buttons": [[{
            "action": {
                "type": "text",
                "label": str(btn)[:40]
            },
            "color": "primary"
        }] for btn in buttons]
    }

def get_order_keyboard(order_id):
    """
    Создание клавиатуры для управления заявкой
    
    Args:
        order_id (int): Номер заявки
    
    Returns:
        dict: Клавиатура с кнопками управления заявкой
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
        dict: Основная клавиатура с выбором категории услуг
    """
    buttons = [
        "Услуги Населению",
        "Услуги для Бизнеса"
    ]
    return create_keyboard(buttons)