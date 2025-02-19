from enum import Enum, auto

class DialogState(Enum):
    """Состояния диалога"""
    # Начальные состояния
    START = auto()
    MAIN_MENU = auto()
    HELP = auto()
    LANGUAGE_SELECTION = auto()
    
    # Выбор типа услуг
    CHOOSING_SERVICE_TYPE = auto()
    
    # Ветка для бизнеса
    BUSINESS_TYPE_INPUT = auto()
    BUSINESS_TASK_INPUT = auto()
    
    # Ветка для частных лиц
    PERSONAL_TASK_INPUT = auto()
    
    # Общие состояния
    CONTACT_INPUT = auto()
    CONTACT_INPUT_RETRY = auto()
    ORDER_CONFIRMATION = auto()
    
    # Управление заявками
    VIEWING_ORDERS = auto()
    ORDERS_FILTER = auto()
    ORDER_HISTORY = auto()
    ORDER_MANAGEMENT = auto()
    ORDER_EDITING = auto()
    ORDER_FEEDBACK = auto()
    
    # Состояния ошибок и восстановления
    ERROR_HANDLING = auto()
    INPUT_VALIDATION = auto()
    
    # Состояния отмены и возврата
    CANCEL_CONFIRMATION = auto()
    
    # Завершающие состояния
    FINISHED = auto()

class OrderStatus(Enum):
    """Статусы заявок"""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELETED = "deleted"
    CANCELLED = "cancelled"

# Глобальные команды, доступные в любом состоянии
GLOBAL_COMMANDS = {
    "/start": DialogState.START,
    "/menu": DialogState.MAIN_MENU,
    "/help": DialogState.HELP,
    "/cancel": DialogState.CANCEL_CONFIRMATION
}

# Возможные переходы между состояниями
STATE_TRANSITIONS = {
    DialogState.START: [
        DialogState.MAIN_MENU,
        DialogState.LANGUAGE_SELECTION
    ],
    DialogState.MAIN_MENU: [
        DialogState.CHOOSING_SERVICE_TYPE,
        DialogState.VIEWING_ORDERS,
        DialogState.HELP,
        DialogState.LANGUAGE_SELECTION
    ],
    DialogState.HELP: [
        DialogState.MAIN_MENU,
        DialogState.CHOOSING_SERVICE_TYPE,
        DialogState.VIEWING_ORDERS
    ],
    DialogState.LANGUAGE_SELECTION: [
        DialogState.MAIN_MENU,
        DialogState.START
    ],
    DialogState.CHOOSING_SERVICE_TYPE: [
        DialogState.BUSINESS_TYPE_INPUT,
        DialogState.PERSONAL_TASK_INPUT,
        DialogState.MAIN_MENU,
        DialogState.HELP,
        DialogState.CANCEL_CONFIRMATION
    ],
    DialogState.BUSINESS_TYPE_INPUT: [
        DialogState.BUSINESS_TASK_INPUT,
        DialogState.CHOOSING_SERVICE_TYPE,
        DialogState.ERROR_HANDLING,
        DialogState.CANCEL_CONFIRMATION,
        DialogState.MAIN_MENU
    ],
    DialogState.BUSINESS_TASK_INPUT: [
        DialogState.CONTACT_INPUT,
        DialogState.BUSINESS_TYPE_INPUT,
        DialogState.ERROR_HANDLING,
        DialogState.CANCEL_CONFIRMATION,
        DialogState.MAIN_MENU
    ],
    DialogState.PERSONAL_TASK_INPUT: [
        DialogState.CONTACT_INPUT,
        DialogState.CHOOSING_SERVICE_TYPE,
        DialogState.ERROR_HANDLING,
        DialogState.CANCEL_CONFIRMATION,
        DialogState.MAIN_MENU
    ],
    DialogState.CONTACT_INPUT: [
        DialogState.ORDER_CONFIRMATION,
        DialogState.CONTACT_INPUT_RETRY,
        DialogState.ERROR_HANDLING,
        DialogState.CANCEL_CONFIRMATION,
        DialogState.MAIN_MENU
    ],
    DialogState.CONTACT_INPUT_RETRY: [
        DialogState.CONTACT_INPUT,
        DialogState.ORDER_CONFIRMATION,
        DialogState.CANCEL_CONFIRMATION,
        DialogState.MAIN_MENU
    ],
    DialogState.ORDER_CONFIRMATION: [
        DialogState.FINISHED,
        DialogState.CONTACT_INPUT,
        DialogState.ERROR_HANDLING,
        DialogState.CANCEL_CONFIRMATION,
        DialogState.MAIN_MENU
    ],
    DialogState.VIEWING_ORDERS: [
        DialogState.ORDER_MANAGEMENT,
        DialogState.ORDERS_FILTER,
        DialogState.ORDER_HISTORY,
        DialogState.MAIN_MENU
    ],
    DialogState.ORDERS_FILTER: [
        DialogState.VIEWING_ORDERS,
        DialogState.ORDER_HISTORY,
        DialogState.MAIN_MENU
    ],
    DialogState.ORDER_HISTORY: [
        DialogState.VIEWING_ORDERS,
        DialogState.ORDER_MANAGEMENT,
        DialogState.MAIN_MENU
    ],
    DialogState.ORDER_MANAGEMENT: [
        DialogState.ORDER_EDITING,
        DialogState.ORDER_FEEDBACK,
        DialogState.VIEWING_ORDERS,
        DialogState.MAIN_MENU
    ],
    DialogState.ORDER_EDITING: [
        DialogState.ORDER_MANAGEMENT,
        DialogState.ERROR_HANDLING,
        DialogState.CANCEL_CONFIRMATION,
        DialogState.MAIN_MENU
    ],
    DialogState.ORDER_FEEDBACK: [
        DialogState.ORDER_MANAGEMENT,
        DialogState.VIEWING_ORDERS,
        DialogState.MAIN_MENU
    ],
    DialogState.ERROR_HANDLING: [
        DialogState.MAIN_MENU,
        DialogState.INPUT_VALIDATION,
        DialogState.CANCEL_CONFIRMATION
    ],
    DialogState.INPUT_VALIDATION: [
        DialogState.CONTACT_INPUT,
        DialogState.BUSINESS_TASK_INPUT,
        DialogState.PERSONAL_TASK_INPUT,
        DialogState.MAIN_MENU
    ],
    DialogState.CANCEL_CONFIRMATION: [
        DialogState.MAIN_MENU
    ],
    DialogState.FINISHED: [DialogState.MAIN_MENU]
}

# Сообщения для каждого состояния
STATE_MESSAGES = {
    DialogState.START: (
        "Здравствуйте! Я автоматический помощник сообщества IT-Помощь в Поварово.\n"
        "В любой момент вы можете использовать следующие команды:\n"
        "• /start - Начать сначала\n"
        "• /menu - Вернуться в главное меню\n"
        "• /help - Получить помощь\n"
        "• /cancel - Отменить текущее действие"
    ),
    DialogState.MAIN_MENU: "Выберите действие:",
    DialogState.HELP: (
        "Я могу помочь вам:\n"
        "• Создать новую заявку\n"
        "• Просмотреть существующие заявки\n"
        "• Изменить или отменить заявку\n"
        "• Оставить отзыв\n\n"
        "Глобальные команды:\n"
        "• /start - Начать сначала\n"
        "• /menu - Вернуться в главное меню\n"
        "• /help - Получить помощь\n"
        "• /cancel - Отменить текущее действие\n\n"
        "Для начала работы выберите пункт меню."
    ),
    DialogState.LANGUAGE_SELECTION: "Выберите язык / Choose language:",
    DialogState.CHOOSING_SERVICE_TYPE: "Выберите категорию услуг:",
    DialogState.BUSINESS_TYPE_INPUT: (
        "Опишите деятельность вашей компании:\n"
        "Например: интернет-магазин, производство, услуги и т.д.\n\n"
        "Для отмены введите /cancel"
    ),
    DialogState.BUSINESS_TASK_INPUT: (
        "Опишите, какая помощь требуется для вашего бизнеса:\n"
        "Например: разработка сайта, настройка CRM, автоматизация процессов\n\n"
        "Для отмены введите /cancel"
    ),
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
        "Опишите вашу задачу:\n"
        "Для отмены введите /cancel"
    ),
    DialogState.CONTACT_INPUT: (
        "Для связи с вами укажите, пожалуйста, номер телефона:\n"
        "Формат: +7 (XXX) XXX-XX-XX\n\n"
        "Для отмены введите /cancel"
    ),
    DialogState.CONTACT_INPUT_RETRY: (
        "Номер телефона введен некорректно.\n"
        "Пожалуйста, используйте формат: +7 (XXX) XXX-XX-XX\n\n"
        "Для отмены введите /cancel"
    ),
    DialogState.ORDER_CONFIRMATION: (
        "Проверьте данные вашей заявки:\n"
        "{order_details}\n"
        "Всё верно?\n\n"
        "Для отмены введите /cancel"
    ),
    DialogState.VIEWING_ORDERS: "Ваши активные заявки:",
    DialogState.ORDERS_FILTER: "Выберите статус заявок для просмотра:",
    DialogState.ORDER_HISTORY: "История ваших заявок:",
    DialogState.ORDER_MANAGEMENT: (
        "Заявка №{order_id}:\n"
        "{order_details}\n"
        "Выберите действие:"
    ),
    DialogState.ORDER_EDITING: (
        "Введите новое описание заявки:\n\n"
        "Для отмены введите /cancel"
    ),
    DialogState.ORDER_FEEDBACK: (
        "Оцените качество выполнения заявки от 1 до 5\n"
        "и оставьте комментарий при желании:\n\n"
        "Для отмены введите /cancel"
    ),
    DialogState.ERROR_HANDLING: (
        "Произошла ошибка при обработке вашего запроса.\n"
        "Пожалуйста, попробуйте еще раз или обратитесь в поддержку.\n\n"
        "• /menu - Вернуться в главное меню\n"
        "• /help - Получить помощь"
    ),
    DialogState.INPUT_VALIDATION: (
        "Пожалуйста, проверьте правильность введенных данных:\n\n"
        "Для отмены введите /cancel"
    ),
    DialogState.CANCEL_CONFIRMATION: (
        "Вы уверены, что хотите отменить текущее действие?\n"
        "Все введенные данные будут потеряны."
    ),
    DialogState.FINISHED: (
        "Спасибо! Ваша заявка принята. Мы свяжемся с вами в ближайшее время.\n\n"
        "• Создать новую заявку - нажмите 'Создать заявку'\n"
        "• Вернуться в главное меню - нажмите 'В меню'"
    )
}