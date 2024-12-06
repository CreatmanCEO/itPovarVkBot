import logging
from typing import Tuple, Optional, Dict, Any
from datetime import datetime

from .states import DialogState, STATE_TRANSITIONS
from models.schemas import UserState, Order
from services.storage_service import StorageService
from utils.helpers import PhoneNumberHelper, TextHelper, DateTimeHelper, OrderHelper

logger = logging.getLogger(__name__)

class DialogHandler:
    def __init__(self, storage: StorageService):
        self.storage = storage

    async def handle_state(self, user_state: UserState, message: str) -> Tuple[DialogState, str, Dict[str, Any]]:
        """
        Обработка сообщения в зависимости от текущего состояния
        
        Args:
            user_state: Текущее состояние пользователя
            message: Текст сообщения
        
        Returns:
            Tuple[DialogState, str, Dict]: (новое состояние, сообщение для пользователя, данные для клавиатуры)
        """
        try:
            current_state = DialogState[user_state.state]
            
            # Проверяем команду отмены
            if message.lower() == "отменить":
                return await self.handle_cancel(user_state)
            
            # Проверяем команду "назад"
            if message.lower() == "назад":
                return await self.handle_back(user_state)

            # Обработка состояний
            handlers = {
                DialogState.START: self.handle_start,
                DialogState.MAIN_MENU: self.handle_main_menu,
                DialogState.CHOOSING_SERVICE_TYPE: self.handle_service_choice,
                DialogState.BUSINESS_TYPE_INPUT: self.handle_business_type,
                DialogState.BUSINESS_TASK_INPUT: self.handle_business_task,
                DialogState.PERSONAL_TASK_INPUT: self.handle_personal_task,
                DialogState.CONTACT_INPUT: self.handle_contact_input,
                DialogState.ORDER_CONFIRMATION: self.handle_confirmation,
                DialogState.VIEWING_ORDERS: self.handle_viewing_orders,
                DialogState.ORDER_MANAGEMENT: self.handle_order_management,
                DialogState.ORDER_EDITING: self.handle_order_editing
            }
            
            handler = handlers.get(current_state)
            if handler:
                return await handler(user_state, message)
            
            # Если не нашли обработчик, возвращаемся в главное меню
            logger.warning(f"Неизвестное состояние: {current_state}")
            return DialogState.MAIN_MENU, "Давайте начнем сначала. Выберите действие:", {"show_main_menu": True}
            
        except Exception as e:
            logger.error(f"Ошибка при обработке состояния: {e}")
            return DialogState.MAIN_MENU, "Произошла ошибка. Давайте попробуем сначала:", {"show_main_menu": True}

    async def handle_start(self, user_state: UserState, message: str) -> Tuple[DialogState, str, Dict[str, Any]]:
        """Обработка начального состояния"""
        # Проверяем наличие активных заявок
        orders = await self.storage.get_user_orders(user_state.user_id)
        keyboard_data = {
            "show_orders": bool(orders),
            "show_new_order": True
        }
        
        return (
            DialogState.MAIN_MENU,
            f"Здравствуйте, {user_state.context['name']}! "
            "Я автоматический помощник сообщества IT-Помощь в Поварово.\n\n"
            "Чем могу помочь?",
            keyboard_data
        )

    async def handle_main_menu(self, user_state: UserState, message: str) -> Tuple[DialogState, str, Dict[str, Any]]:
        """Обработка главного меню"""
        if message.lower() in ["создать заявку", "новая заявка"]:
            return (
                DialogState.CHOOSING_SERVICE_TYPE,
                "Выберите категорию услуг:",
                {"show_service_types": True}
            )
        elif message.lower() == "мои заявки":
            return await self.handle_orders_list(user_state)
        else:
            return (
                DialogState.MAIN_MENU,
                "Пожалуйста, выберите действие с помощью кнопок:",
                {"show_main_menu": True}
            )

    async def handle_service_choice(self, user_state: UserState, message: str) -> Tuple[DialogState, str, Dict[str, Any]]:
        """Обработка выбора типа услуг"""
        if message.lower() == "услуги для бизнеса":
            return (
                DialogState.BUSINESS_TYPE_INPUT,
                "Расскажите кратко о вашей компании:",
                {"show_back": True}
            )
        elif message.lower() == "услуги населению":
            return (
                DialogState.PERSONAL_TASK_INPUT,
                "Опишите, какая помощь вам требуется:",
                {"show_back": True}
            )
        else:
            return (
                DialogState.CHOOSING_SERVICE_TYPE,
                "Пожалуйста, выберите тип услуг с помощью кнопок:",
                {"show_service_types": True}
            )
    async def handle_business_type(self, user_state: UserState, message: str) -> Tuple[DialogState, str, Dict[str, Any]]:
        """Обработка ввода типа бизнеса"""
        message = TextHelper.clean_text(message)
        if not message:
            return (
                DialogState.BUSINESS_TYPE_INPUT,
                "Пожалуйста, введите информацию о вашей компании:",
                {"show_back": True}
            )
            
        user_state.temp_data["business_type"] = message
        return (
            DialogState.BUSINESS_TASK_INPUT,
            "Опишите, какая помощь требуется для вашего бизнеса:",
            {"show_back": True}
        )

    async def handle_business_task(self, user_state: UserState, message: str) -> Tuple[DialogState, str, Dict[str, Any]]:
        """Обработка ввода задачи для бизнеса"""
        message = TextHelper.clean_text(message)
        if not message:
            return (
                DialogState.BUSINESS_TASK_INPUT,
                "Пожалуйста, опишите вашу задачу:",
                {"show_back": True}
            )
            
        user_state.temp_data["task"] = message
        return (
            DialogState.CONTACT_INPUT,
            "Для связи с вами укажите, пожалуйста, номер телефона:",
            {"show_back": True}
        )

    async def handle_personal_task(self, user_state: UserState, message: str) -> Tuple[DialogState, str, Dict[str, Any]]:
        """Обработка ввода личной задачи"""
        message = TextHelper.clean_text(message)
        if not message:
            return (
                DialogState.PERSONAL_TASK_INPUT,
                "Пожалуйста, опишите вашу задачу:",
                {"show_back": True}
            )
            
        user_state.temp_data["task"] = message
        return (
            DialogState.CONTACT_INPUT,
            "Для связи с вами укажите, пожалуйста, номер телефона:",
            {"show_back": True}
        )

    async def handle_contact_input(self, user_state: UserState, message: str) -> Tuple[DialogState, str, Dict[str, Any]]:
        """Обработка ввода контактных данных"""
        if not PhoneNumberHelper.is_valid_phone(message):
            return (
                DialogState.CONTACT_INPUT,
                "Некорректный формат номера телефона. Пожалуйста, введите номер в формате: 89991234567",
                {"show_back": True}
            )

        user_state.temp_data["phone"] = PhoneNumberHelper.format_phone(message)
        
        # Формируем детали заявки для подтверждения
        order_details = (
            f"Имя: {user_state.context['name']}\n"
            f"Телефон: {user_state.temp_data['phone']}\n"
            f"Описание: {user_state.temp_data['task']}"
        )
        
        if user_state.temp_data.get("business_type"):
            order_details += f"\nТип бизнеса: {user_state.temp_data['business_type']}"
            
        return (
            DialogState.ORDER_CONFIRMATION,
            f"Проверьте данные вашей заявки:\n\n{order_details}\n\nВсё верно?",
            {"show_confirmation": True}
        )

    async def handle_confirmation(self, user_state: UserState, message: str) -> Tuple[DialogState, str, Dict[str, Any]]:
        """Обработка подтверждения заявки"""
        if message.lower() == "подтвердить" or message.lower() == "отправить заявку":
            # Создаем заявку
            order_id = await self.storage.create_order(
                user_id=user_state.user_id,
                name=user_state.context["name"],
                phone=user_state.temp_data["phone"],
                task=user_state.temp_data["task"],
                business_type=user_state.temp_data.get("business_type")
            )
            
            # Очищаем временные данные
            user_state.temp_data = {}
            
            return (
                DialogState.FINISHED,
                f"Спасибо! Ваша заявка №{order_id} принята. "
                "Мы свяжемся с вами в ближайшее время.",
                {"show_main_menu": True}
            )
        else:
            return (
                DialogState.CHOOSING_SERVICE_TYPE,
                "Хорошо, давайте заполним заявку заново. Выберите категорию услуг:",
                {"show_service_types": True}
            )

    async def handle_orders_list(self, user_state: UserState) -> Tuple[DialogState, str, Dict[str, Any]]:
        """Отображение списка заявок пользователя"""
        orders = await self.storage.get_user_orders(user_state.user_id)
        
        if not orders:
            return (
                DialogState.MAIN_MENU,
                "У вас пока нет активных заявок.",
                {"show_main_menu": True}
            )
        
        message_parts = ["Ваши активные заявки:\n"]
        for order in orders:
            status = OrderHelper.format_order_status(order.status)
            status_emoji = OrderHelper.get_status_emoji(order.status)
            time_ago = DateTimeHelper.get_readable_delta(order.created_at)
            
            message_parts.append(
                f"{status_emoji} Заявка №{order.id} ({status})\n"
                f"Создана: {time_ago}\n"
                f"Задача: {TextHelper.truncate(order.task, 100)}\n"
            )
        
        keyboard_data = {
            "orders": [{"id": order.id, "status": order.status} for order in orders],
            "show_new_order": True,
            "show_back": True
        }
        
        return (
            DialogState.VIEWING_ORDERS,
            "\n".join(message_parts),
            keyboard_data
        )

    async def handle_order_management(self, user_state: UserState, message: str) -> Tuple[DialogState, str, Dict[str, Any]]:
        """Обработка действий с конкретной заявкой"""
        # Извлекаем ID заявки из сообщения
        if not message.startswith("заявка №"):
            return await self.handle_orders_list(user_state)
            
        try:
            order_id = int(message.split("№")[1])
            order = await self.storage.get_order(order_id)
            
            if not order:
                return await self.handle_orders_list(user_state)
                
            # Сохраняем ID текущей заявки
            user_state.temp_data["current_order_id"] = order_id
            
            status = OrderHelper.format_order_status(order.status)
            message = (
                f"Заявка №{order.id} ({status})\n"
                f"Создана: {DateTimeHelper.format_datetime(order.created_at)}\n"
                f"Описание: {order.task}\n\n"
                "Выберите действие:"
            )
            
            return (
                DialogState.ORDER_MANAGEMENT,
                message,
                {"show_order_actions": True}
            )
            
        except (ValueError, IndexError):
            return await self.handle_orders_list(user_state)

    async def handle_order_editing(self, user_state: UserState, message: str) -> Tuple[DialogState, str, Dict[str, Any]]:
        """Обработка редактирования заявки"""
        order_id = user_state.temp_data.get("current_order_id")
        if not order_id:
            return await self.handle_orders_list(user_state)
            
        message = TextHelper.clean_text(message)
        if not message:
            return (
                DialogState.ORDER_EDITING,
                "Пожалуйста, введите новое описание заявки:",
                {"show_back": True}
            )
            
        # Обновляем заявку
        updated_order = await self.storage.update_order(order_id, message)
        if not updated_order:
            return await self.handle_orders_list(user_state)
            
        return (
            DialogState.VIEWING_ORDERS,
            f"Заявка №{order_id} успешно обновлена!",
            {"show_orders_list": True}
        )

    async def handle_cancel(self, user_state: UserState) -> Tuple[DialogState, str, Dict[str, Any]]:
        """Обработка отмены"""
        user_state.temp_data = {}  # Очищаем временные данные
        return (
            DialogState.MAIN_MENU,
            "Действие отменено. Выберите, что хотите сделать:",
            {"show_main_menu": True}
        )

    async def handle_back(self, user_state: UserState) -> Tuple[DialogState, str, Dict[str, Any]]:
        """Обработка команды "назад\""""
        current_state = DialogState[user_state.state]
        transitions = STATE_TRANSITIONS.get(current_state, [])
        
        if not transitions:
            return (
                DialogState.MAIN_MENU,
                "Выберите действие:",
                {"show_main_menu": True}
            )
            
        prev_state = transitions[-1]  # Берем последний возможный переход как "назад"
        
        if prev_state == DialogState.MAIN_MENU:
            return await self.handle_main_menu(user_state, "")
        elif prev_state == DialogState.CHOOSING_SERVICE_TYPE:
            return await self.handle_service_choice(user_state, "")
        elif prev_state == DialogState.VIEWING_ORDERS:
            return await self.handle_orders_list(user_state)
            
        return (
            prev_state,
            "Вернулись назад. Выберите действие:",
            {"show_back": True}
        )