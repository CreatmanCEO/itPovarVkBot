from typing import Dict, Any
from .states import DialogState

class MessageBuilder:
    @staticmethod
    def get_greeting(name: str) -> str:
        return (
            f"Здравствуйте, {name}! "
            "Я автоматический помощник сообщества IT-Помощь в Поварово.\n\n"
            "Чем могу помочь?"
        )

    @staticmethod
    def get_services_list() -> str:
        return (
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
        )

    @staticmethod
    def get_business_services() -> str:
        return (
            "IT-услуги для бизнеса:\n\n"
            "🏢 Автоматизация:\n"
            "• Внедрение CRM-систем\n"
            "• Автоматизация бизнес-процессов\n"
            "• Интеграция сервисов\n\n"
            "🌐 Разработка:\n"
            "• Создание сайтов и веб-приложений\n"
            "• Корпоративные порталы\n"
            "• Мобильные приложения\n\n"
            "🔧 Обслуживание:\n"
            "• Техническая поддержка\n"
            "• Настройка серверов\n"
            "• Обеспечение безопасности\n\n"
            "Опишите деятельность вашей компании:"
        )

    @staticmethod
    def format_order_details(order_data: Dict[str, Any]) -> str:
        details = (
            f"Заявка №{order_data['id']}\n"
            f"Дата создания: {order_data['created_at']}\n"
            f"Имя: {order_data['name']}\n"
            f"Телефон: {order_data['phone']}\n"
            f"Описание: {order_data['task']}"
        )
        if order_data.get('business_type'):
            details += f"\nТип бизнеса: {order_data['business_type']}"
        return details

    @staticmethod
    def get_state_message(state: DialogState, context: Dict[str, Any] = None) -> str:
        """Получение сообщения для конкретного состояния"""
        context = context or {}
        
        if state == DialogState.START:
            return MessageBuilder.get_greeting(context.get('name', 'Пользователь'))
            
        elif state == DialogState.MAIN_MENU:
            return "Выберите действие:"
            
        elif state == DialogState.CHOOSING_SERVICE_TYPE:
            return "Выберите категорию услуг:"
            
        elif state == DialogState.BUSINESS_TYPE_INPUT:
            return MessageBuilder.get_business_services()
            
        elif state == DialogState.BUSINESS_TASK_INPUT:
            return "Опишите, какая помощь требуется для вашего бизнеса:"
            
        elif state == DialogState.PERSONAL_TASK_INPUT:
            return MessageBuilder.get_services_list()
            
        elif state == DialogState.CONTACT_INPUT:
            return "Для связи с вами укажите, пожалуйста, номер телефона:"
            
        elif state == DialogState.ORDER_CONFIRMATION:
            if 'order_details' in context:
                return f"Проверьте данные вашей заявки:\n\n{context['order_details']}\n\nВсё верно?"
            return "Проверьте данные заявки:"
            
        elif state == DialogState.VIEWING_ORDERS:
            if not context.get('orders'):
                return "У вас пока нет активных заявок."
            return "Ваши активные заявки:"
            
        elif state == DialogState.ORDER_MANAGEMENT:
            if 'order_details' in context:
                return f"Заявка №{context['order_id']}:\n\n{context['order_details']}\n\nВыберите действие:"
            return "Выберите действие с заявкой:"
            
        elif state == DialogState.ORDER_EDITING:
            return "Введите новое описание заявки:"
            
        elif state == DialogState.FINISHED:
            return (
                f"Спасибо! Ваша заявка №{context.get('order_id', '')} принята.\n"
                "Мы свяжемся с вами в ближайшее время."
            )
            
        return "Произошла ошибка. Пожалуйста, начните сначала."