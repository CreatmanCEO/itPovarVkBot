import json
import logging
import asyncio
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from datetime import datetime
from typing import Optional, Dict, Any

from config.config import VK_TOKEN, VK_GROUP_ID
from models.schemas import UserState, Order
from services.storage_service import StorageService
from services.telegram_service import TelegramService
from dialogs.states import DialogState
from dialogs.handlers import DialogHandler
from utils.helpers import PhoneNumberHelper, TextHelper, DateTimeHelper, OrderHelper

logger = logging.getLogger(__name__)

class VKService:
    def __init__(self):
        # Инициализация VK API
        self.vk_session = vk_api.VkApi(token=VK_TOKEN)
        self.longpoll = VkBotLongPoll(self.vk_session, VK_GROUP_ID)
        self.vk = self.vk_session.get_api()

        # Инициализация сервисов
        self.storage = StorageService()
        self.dialog_handler = DialogHandler(self.storage)
        
        # Кэш состояний пользователей для оптимизации
        self.user_states_cache: Dict[int, UserState] = {}
        self.cache_cleanup_task = None

    async def send_message(self, user_id: int, message: str, keyboard: Optional[dict] = None) -> bool:
        """
        Отправка сообщения пользователю
        
        Args:
            user_id: ID пользователя ВК
            message: Текст сообщения
            keyboard: Клавиатура в формате словаря
            
        Returns:
            bool: Успешность отправки
        """
        try:
            # Подготовка клавиатуры
            keyboard_json = json.dumps(keyboard, ensure_ascii=False) if keyboard else None
            
            # Генерация random_id
            random_id = int(datetime.now().timestamp() * 1000)
            
            # Отправка сообщения
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.vk.messages.send(
                    user_id=user_id,
                    message=message,
                    random_id=random_id,
                    keyboard=keyboard_json
                )
            )
            
            logger.info(f"Сообщение отправлено пользователю {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
            return False

    async def get_user_info(self, user_id: int) -> Dict[str, Any]:
        """Получение информации о пользователе"""
        try:
            user_info = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.vk.users.get(user_ids=user_id)[0]
            )
            return user_info
        except Exception as e:
            logger.error(f"Ошибка при получении информации о пользователе {user_id}: {e}")
            return {"first_name": "Пользователь", "last_name": ""}

    async def get_or_create_user_state(self, user_id: int) -> UserState:
        """
        Получение или создание состояния пользователя
        
        Args:
            user_id: ID пользователя ВК
            
        Returns:
            UserState: Объект состояния пользователя
        """
        # Проверяем кэш
        if user_id in self.user_states_cache:
            return self.user_states_cache[user_id]
        
        # Пытаемся получить из БД
        state = await self.storage.get_user_state(str(user_id))
        
        if not state:
            # Получаем информацию о пользователе
            user_info = await self.get_user_info(user_id)
            
            # Создаем новое состояние
            state = UserState(
                user_id=str(user_id),
                state=DialogState.START.name,
                context={
                    "name": user_info["first_name"],
                    "full_name": f"{user_info['first_name']} {user_info.get('last_name', '')}"
                }
            )
            
            # Сохраняем в БД
            await self.storage.set_user_state(
                str(user_id),
                state.state,
                state.context
            )
        
        # Сохраняем в кэш
        self.user_states_cache[user_id] = state
        return state
        
    async def process_new_message(self, event) -> None:
        """
        Обработка нового сообщения
        
        Args:
            event: Событие от VK API
        """
        try:
            user_id = event.message.from_id
            message_text = event.message.text or ""
            
            # Получаем состояние пользователя
            user_state = await self.get_or_create_user_state(user_id)
            
            # Обрабатываем служебные команды
            if message_text.lower() == "отменить заявку":
                await self.handle_cancel(user_id, user_state)
                return
                
            if message_text.lower() == "удалить заявку":
                await self.handle_delete_order(user_id, user_state)
                return

            # Обрабатываем состояние через dialog_handler
            new_state, response_message, keyboard_data = await self.dialog_handler.handle_state(
                user_state,
                message_text
            )

            # Обновляем состояние пользователя
            user_state.state = new_state.name
            await self.storage.set_user_state(
                str(user_id), 
                user_state.state, 
                user_state.context,
                user_state.temp_data
            )
            
            # Обновляем кэш
            self.user_states_cache[user_id] = user_state

            # Формируем и отправляем ответ
            keyboard = await self.build_keyboard(new_state, keyboard_data)
            await self.send_message(user_id, response_message, keyboard)

        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
            await self.handle_error(user_id, e)

    async def build_keyboard(self, state: DialogState, data: Dict[str, Any]) -> dict:
        """
        Формирование клавиатуры в зависимости от состояния
        
        Args:
            state: Текущее состояние диалога
            data: Дополнительные данные для клавиатуры
            
        Returns:
            dict: Структура клавиатуры для VK API
        """
        buttons = []
        
        # Основные кнопки в зависимости от состояния
        if data.get("show_main_menu"):
            buttons.extend(["Создать заявку", "Мои заявки"])
            
        elif data.get("show_service_types"):
            buttons.extend(["Услуги Населению", "Услуги для Бизнеса"])
            
        elif data.get("show_confirmation"):
            buttons.extend(["Отправить заявку", "Изменить заявку"])
            
        elif data.get("show_order_actions"):
            buttons.extend(["Изменить заявку", "Удалить заявку"])
            
        # Добавляем кнопки заявок, если есть
        if data.get("orders"):
            buttons.extend([f"Заявка №{order['id']}" for order in data["orders"]])
            
        # Добавляем кнопку создания новой заявки
        if data.get("show_new_order"):
            buttons.append("Создать новую заявку")
            
        # Добавляем кнопку "Назад" если нужно
        if data.get("show_back") and state not in [DialogState.START, DialogState.MAIN_MENU]:
            buttons.append("Назад")
            
        # Формируем структуру клавиатуры
        keyboard = {
            "one_time": True,
            "buttons": [[{
                "action": {
                    "type": "text",
                    "label": btn
                },
                "color": "primary"
            }] for btn in buttons]
        }
        
        return keyboard

    async def handle_cancel(self, user_id: int, user_state: UserState) -> None:
        """Обработка отмены создания заявки"""
        # Сбрасываем состояние
        user_state.state = DialogState.MAIN_MENU.name
        user_state.temp_data = {}
        
        # Сохраняем обновленное состояние
        await self.storage.set_user_state(
            str(user_id),
            user_state.state,
            user_state.context
        )
        
        # Отправляем сообщение
        keyboard = await self.build_keyboard(
            DialogState.MAIN_MENU,
            {"show_main_menu": True}
        )
        await self.send_message(
            user_id,
            "Создание заявки отменено. Выберите действие:",
            keyboard
        )
    async def handle_delete_order(self, user_id: int, user_state: UserState) -> None:
        """Обработка удаления заявки"""
        try:
            order_id = user_state.temp_data.get("current_order_id")
            if not order_id:
                return
            
            # Получаем заявку перед удалением для уведомления
            order = await self.storage.get_order(order_id)
            if not order:
                return
                
            # Удаляем заявку
            deleted = await self.storage.delete_order(order_id)
            if not deleted:
                await self.send_message(
                    user_id,
                    "Не удалось удалить заявку. Попробуйте позже.",
                    await self.build_keyboard(DialogState.VIEWING_ORDERS, {"show_orders_list": True})
                )
                return
                
            # Отправляем уведомление в Telegram
            await TelegramService.notify_order_delete(order)
            
            # Отправляем подтверждение пользователю
            keyboard = await self.build_keyboard(
                DialogState.VIEWING_ORDERS,
                {"show_orders_list": True}
            )
            await self.send_message(
                user_id,
                f"Заявка №{order_id} успешно удалена.",
                keyboard
            )
            
        except Exception as e:
            logger.error(f"Ошибка при удалении заявки: {e}")
            await self.handle_error(user_id, e)

    async def handle_error(self, user_id: int, error: Exception) -> None:
        """Обработка ошибок"""
        try:
            # Логируем ошибку
            logger.error(f"Ошибка при обработке запроса от пользователя {user_id}: {error}")
            
            # Отправляем сообщение пользователю
            keyboard = await self.build_keyboard(
                DialogState.MAIN_MENU,
                {"show_main_menu": True}
            )
            await self.send_message(
                user_id,
                "Произошла ошибка. Пожалуйста, попробуйте позже или начните сначала.",
                keyboard
            )
            
            # Уведомляем администратора через Telegram
            error_details = {
                "user_id": user_id,
                "error_type": type(error).__name__,
                "error_message": str(error)
            }
            await TelegramService.notify_error("bot_error", error_details)
            
        except Exception as e:
            logger.critical(f"Ошибка при обработке ошибки: {e}")

    async def cleanup_cache(self) -> None:
        """Периодическая очистка кэша состояний"""
        while True:
            try:
                # Очищаем старые состояния из БД
                deleted = await self.storage.cleanup_old_states(hours=24)
                if deleted > 0:
                    logger.info(f"Удалено {deleted} старых состояний")
                
                # Очищаем кэш
                self.user_states_cache.clear()
                
                # Ждем 6 часов
                await asyncio.sleep(6 * 60 * 60)
                
            except Exception as e:
                logger.error(f"Ошибка при очистке кэша: {e}")
                await asyncio.sleep(60)  # Ждем минуту перед повторной попыткой

    async def run(self) -> None:
        """Запуск бота"""
        logger.info("Запуск VK бота...")
        
        # Запускаем задачу очистки кэша
        self.cache_cleanup_task = asyncio.create_task(self.cleanup_cache())
        
        while True:
            try:
                # Создаем новый longpoll для каждой итерации
                self.longpoll = VkBotLongPoll(self.vk_session, VK_GROUP_ID)
                
                # Слушаем события
                for event in self.longpoll.listen():
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        # Запускаем обработку сообщения в отдельной задаче
                        asyncio.create_task(self.process_new_message(event))
                        
            except Exception as e:
                logger.error(f"Ошибка в основном цикле бота: {e}")
                # Ждем перед повторным подключением
                await asyncio.sleep(5)
            
            finally:
                # Отменяем задачу очистки кэша при выходе
                if self.cache_cleanup_task:
                    self.cache_cleanup_task.cancel()
                    try:
                        await self.cache_cleanup_task
                    except asyncio.CancelledError:
                        pass

    async def stop(self) -> None:
        """Остановка бота"""
        logger.info("Остановка VK бота...")
        if self.cache_cleanup_task:
            self.cache_cleanup_task.cancel()
            try:
                await self.cache_cleanup_task
            except asyncio.CancelledError:
                pass