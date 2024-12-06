from enum import Enum, auto

class DialogState(Enum):
    """Состояния диалога"""
    # Начальные состояния
    START = auto()
    MAIN_MENU = auto()
    
    # Выбор типа услуг
    CHOOSING_SERVICE_TYPE = auto()
    
    # Ветка для бизнеса
    BUSINESS_TYPE_INPUT = auto()
    BUSINESS_TASK_INPUT = auto()
    
    # Ветка для частных лиц
    PERSONAL_TASK_INPUT = auto()
    
    # Общие состояния
    CONTACT_INPUT = auto()
    ORDER_CONFIRMATION = auto()
    
    # Управление заявками
    VIEWING_ORDERS = auto()
    ORDER_MANAGEMENT = auto()
    ORDER_EDITING = auto()
    
    # Завершающие состояния
    FINISHED = auto()

class OrderStatus(Enum):
    """Статусы заявок"""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELETED = "deleted"

# Возможные переходы между состояниями
STATE_TRANSITIONS = {
    DialogState.START: [DialogState.MAIN_MENU],
    DialogState.MAIN_MENU: [DialogState.CHOOSING_SERVICE_TYPE, DialogState.VIEWING_ORDERS],
    DialogState.CHOOSING_SERVICE_TYPE: [
        DialogState.BUSINESS_TYPE_INPUT,
        DialogState.PERSONAL_TASK_INPUT,
        DialogState.MAIN_MENU
    ],
    DialogState.BUSINESS_TYPE_INPUT: [
        DialogState.BUSINESS_TASK_INPUT,
        DialogState.CHOOSING_SERVICE_TYPE
    ],
    DialogState.BUSINESS_TASK_INPUT: [
        DialogState.CONTACT_INPUT,
        DialogState.BUSINESS_TYPE_INPUT
    ],
    DialogState.PERSONAL_TASK_INPUT: [
        DialogState.CONTACT_INPUT,
        DialogState.CHOOSING_SERVICE_TYPE
    ],
    DialogState.CONTACT_INPUT: [
        DialogState.ORDER_CONFIRMATION,
        DialogState.PERSONAL_TASK_INPUT,
        DialogState.BUSINESS_TASK_INPUT
    ],
    DialogState.ORDER_CONFIRMATION: [
        DialogState.FINISHED,
        DialogState.PERSONAL_TASK_INPUT,
        DialogState.BUSINESS_TASK_INPUT
    ],
    DialogState.VIEWING_ORDERS: [
        DialogState.ORDER_MANAGEMENT,
        DialogState.MAIN_MENU
    ],
    DialogState.ORDER_MANAGEMENT: [
        DialogState.ORDER_EDITING,
        DialogState.VIEWING_ORDERS,
        DialogState.MAIN_MENU
    ],
    DialogState.ORDER_EDITING: [
        DialogState.ORDER_MANAGEMENT,
        DialogState.VIEWING_ORDERS
    ],
    DialogState.FINISHED: [DialogState.MAIN_MENU]
}

# Сообщения для каждого состояния
STATE_MESSAGES = {
    DialogState.START: "Здравствуйте! Я автоматический помощник сообщества IT-Помощь в Поварово.",
    DialogState.MAIN_MENU: "Выберите действие:",
    DialogState.CHOOSING_SERVICE_TYPE: "Выберите категорию услуг:",
    DialogState.BUSINESS_TYPE_INPUT: "Опишите деятельность вашей компании:",
    DialogState.BUSINESS_TASK_INPUT: "Опишите, какая помощь требуется для вашего бизнеса:",
    DialogState.PERSONAL_TASK_INPUT: (
        "Наши услуги для частных лиц:\n\n"
        "🔧 Компьютерная помощь:\n"
        "• Настройка и ремонт компьютеров\n"
        "• Установка программ и антивирусов\n"
        "• Восстановление данных\n\n"
        "💻 Разработка:\n"
        "• Создание сайтов и приложений\n"
        "• Разработка чат-ботов\n"
        "• Автоматизация процессов\n\n"
        "📱 Обучение:\n"
        "• Работа с компьютером и программами\n"
        "• Основы программирования\n"
        "• Работа с искусственным интеллектом\n\n"
        "Опишите вашу задачу:"
    ),
    DialogState.CONTACT_INPUT: "Для связи с вами укажите, пожалуйста, номер телефона:",
    DialogState.ORDER_CONFIRMATION: "Проверьте данные вашей заявки:\n{order_details}\nВсё верно?",
    DialogState.VIEWING_ORDERS: "Ваши активные заявки:",
    DialogState.ORDER_MANAGEMENT: "Заявка №{order_id}:\n{order_details}\nВыберите действие:",
    DialogState.ORDER_EDITING: "Введите новое описание заявки:",
    DialogState.FINISHED: "Спасибо! Ваша заявка принята. Мы свяжемся с вами в ближайшее время."
}