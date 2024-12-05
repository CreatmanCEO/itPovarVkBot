import logging
import vk_api
import json
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from datetime import datetime
from typing import Optional, Dict, Any

from config.config import VK_TOKEN, VK_GROUP_ID
from models.order import Order
from services.storage_service import StorageService
from services.telegram_service import TelegramService
from utils.keyboard import create_keyboard, get_order_keyboard, get_main_keyboard

logger = logging.getLogger(__name__)

class VKService:
    def __init__(self):
    self.vk_session = vk_api.VkApi(token=VK_TOKEN)
    self.longpoll = VkBotLongPoll(self.vk_session, VK_GROUP_ID)
    self.vk = self.vk_session.get_api()
    self.storage = StorageService()
    self.user_states: Dict[int, str] = {}
    self.user_data: Dict[int, Dict[str, Any]] = {}

    def send_message(self, user_id: int, message: str, keyboard=None):
        """Отправка сообщения пользователю"""
        try:
            # Если keyboard уже в JSON формате, оставляем как есть
            # Если это словарь - преобразуем в JSON
            keyboard_json = keyboard
            if isinstance(keyboard, dict):
                keyboard_json = json.dumps(keyboard, ensure_ascii=False)

            self.vk.messages.send(
                user_id=user_id,
                message=message,
                random_id=int(datetime.now().timestamp() * 1000),
                keyboard=keyboard_json
            )
            logger.info(f"Сообщение отправлено пользователю {user_id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {e}")

    def start_conversation(self, user_id: int):
        """Начало диалога"""
        active_orders = self.storage.get_user_orders(str(user_id))
        
        if active_orders:
            buttons = ["Создать новую заявку"]
            buttons.extend([f"Заявка №{order.id}" for order in active_orders])
            
            message = (
                f"Здравствуйте, {self.user_data[user_id]['name']}!\n\n"
                "У вас есть активные заявки. Выберите действие:"
            )
            keyboard = create_keyboard(buttons)
            self.send_message(user_id, message, keyboard)
            self.user_states[user_id] = "choosing_action"
        else:
            message = (
                f"Здравствуйте, {self.user_data[user_id]['name']}! "
                "Я автоматический помощник сообщества IT-Помощь в Поварово.\n\n"
                "Выберите категорию услуг:"
            )
            self.send_message(user_id, message, get_main_keyboard())
            self.user_states[user_id] = "awaiting_category"

    def handle_services_selection(self, user_id: int, is_business: bool):
        """Обработка выбора категории услуг"""
        if is_business:
            message = "Опишите деятельность вашей компании и какая помощь требуется:"
            self.user_states[user_id] = "awaiting_business_description"
        else:
            message = (
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
            self.user_states[user_id] = "awaiting_task_description"
        
        self.send_message(user_id, message)

    def request_contact(self, user_id: int):
        """Запрос контактных данных"""
        message = "Для связи с вами укажите, пожалуйста, номер телефона:"
        self.send_message(user_id, message)
        self.user_states[user_id] = "awaiting_phone"

    def handle_order_management(self, user_id: int, text: str):
        """Обработка управления заявкой"""
        if text.startswith("заявка №"):
            order_id = int(text.split("№")[1])
            order = self.storage.get_order(str(user_id), order_id)
            if order:
                message = (
                    f"Заявка №{order.id}:\n"
                    f"Дата: {order.date}\n"
                    f"Описание: {order.task}\n\n"
                    "Выберите действие:"
                )
                self.send_message(user_id, message, get_order_keyboard(order.id))
                self.user_data[user_id]["current_order"] = order.id
                self.user_states[user_id] = "managing_order"

    def handle_order_action(self, user_id: int, text: str):
        """Обработка действий с заявкой"""
        order_id = self.user_data[user_id]["current_order"]
        order = self.storage.get_order(str(user_id), order_id)
        
        if not order:
            self.start_conversation(user_id)
            return

        if text.lower() == "изменить заявку":
            self.send_message(user_id, "Введите новое описание заявки:")
            self.user_states[user_id] = "updating_order"
        
        elif text.lower() == "удалить заявку":
            if self.storage.delete_order(str(user_id), order_id):
                TelegramService.notify_order_delete(order)
                self.send_message(user_id, f"Заявка №{order_id} удалена")
            self.start_conversation(user_id)
        
        elif text.lower() == "назад":
            self.start_conversation(user_id)

    def process_new_message(self, event):
        """Обработка нового сообщения"""
        try:
            user_id = event.message.from_id
            text = event.message.text.lower() if event.message.text else ""

            # Инициализация данных пользователя
            if user_id not in self.user_data:
                user_info = self.vk.users.get(user_ids=user_id)[0]
                self.user_data[user_id] = {"name": user_info["first_name"]}

            # Обработка команд и состояний
            if text in ["", "начать", "привет", "здравствуйте", "добрый день", "добрый вечер"]:
                self.start_conversation(user_id)
            
            elif text == "услуги населению":
                self.handle_services_selection(user_id, False)
            
            elif text == "услуги для бизнеса":
                self.handle_services_selection(user_id, True)
            
            elif text == "создать новую заявку":
                message = "Чем я могу вам помочь в этот раз?"
                self.send_message(user_id, message, get_main_keyboard())
                self.user_states[user_id] = "awaiting_category"
            
            elif user_id in self.user_states:
                state = self.user_states[user_id]
                
                if state == "choosing_action":
                    if text.startswith("заявка №"):
                        self.handle_order_management(user_id, text)
                    else:
                        self.start_conversation(user_id)
                
                elif state == "managing_order":
                    self.handle_order_action(user_id, text)
                
                elif state in ["awaiting_task_description", "awaiting_business_description"]:
                    self.user_data[user_id]["task"] = event.message.text
                    self.request_contact(user_id)
                
                elif state == "awaiting_phone":
                    self.process_phone_input(user_id, event.message.text)
                
                elif state == "updating_order":
                    self.process_order_update(user_id, event.message.text)
            
            else:
                self.start_conversation(user_id)

        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
            self.send_message(user_id, "Произошла ошибка. Пожалуйста, попробуйте позже.")

    def process_phone_input(self, user_id: int, phone: str):
        """Обработка ввода телефона"""
        self.user_data[user_id]["phone"] = phone
        message = (
            "Проверьте данные вашей заявки:\n\n"
            f"Имя: {self.user_data[user_id]['name']}\n"
            f"Телефон: {phone}\n"
            f"Описание: {self.user_data[user_id]['task']}\n\n"
            "Всё верно?"
        )
        keyboard = create_keyboard(["Отправить заявку", "Изменить заявку"])
        self.send_message(user_id, message, keyboard)
        self.user_states[user_id] = "awaiting_confirmation"

    def process_order_update(self, user_id: int, new_text: str):
        """Обработка обновления заявки"""
        order_id = self.user_data[user_id]["current_order"]
        if self.storage.update_order(str(user_id), order_id, new_text):
            order = self.storage.get_order(str(user_id), order_id)
            if order:
                TelegramService.notify_order_update(order)
                self.send_message(user_id, f"Заявка №{order_id} обновлена")
        self.start_conversation(user_id)

    def run(self):
        """Запуск прослушивания сообщений"""
        logger.info("Запуск VK бота...")
        try:
            for event in self.longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    self.process_new_message(event)
        except Exception as e:
            logger.error(f"Критическая ошибка в работе бота: {e}")