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
        try:
            logger.info("Инициализация VK сервиса...")
            # Инициализация VK API
            self.vk_session = vk_api.VkApi(token=VK_TOKEN)
            self.vk = self.vk_session.get_api()
            
            # Проверяем подключение и получаем информацию о группе
            group_info = self.vk.groups.getById()[0]
            logger.info(f"VK API успешно инициализирован. Группа: {group_info['name']} (ID: {group_info['id']})")
            
            # Проверяем возможность отправки сообщений
            try:
                self.vk.messages.getConversations(count=1)
                logger.info("Доступ к сообщениям сообщества подтвержден")
            except vk_api.exceptions.ApiError as e:
                if e.code == 917:
                    logger.error("В сообществе отключены сообщения!")
                    raise
                elif e.code == 27:
                    logger.error("Недостаточно прав для работы с сообщениями сообщества!")
                    raise
                else:
                    raise
            
            # Инициализация LongPoll
            try:
                self.longpoll = VkBotLongPoll(self.vk_session, VK_GROUP_ID)
                logger.info("LongPoll успешно инициализирован")
            except Exception as e:
                logger.error(f"Ошибка инициализации LongPoll: {e}")
                raise

            # Инициализация сервисов
            self.storage = StorageService()
            self.dialog_handler = DialogHandler(self.storage)
            
            # Кэш состояний пользователей для оптимизации
            self.user_states_cache: Dict[int, UserState] = {}
            self.cache_cleanup_task = None
            
        except vk_api.exceptions.ApiError as e:
            logger.error(f"Ошибка API VK: {e}")
            raise
        except Exception as e:
            logger.error(f"Ошибка при инициализации VK сервиса: {e}")
            raise

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
        user_id = None
        try:
            user_id = event.message.from_id
            message_text = event.message.text or ""
            
            logger.info(f"Начало обработки сообщения от пользователя {user_id}: {message_text}")
            
            # Получаем состояние пользователя
            try:
                user_state = await self.get_or_create_user_state(user_id)
                logger.info(f"Получено состояние пользователя {user_id}: {user_state.state}")
                
                # Если это новый пользователь или состояние START, отправляем приветствие
                if not user_state.context.get("greeted"):
                    logger.info(f"Отправка приветственного сообщения пользователю {user_id}")
                    welcome_message = (
                        "Здравствуйте! Я бот IT-Помощь в Поварово.\n\n"
                        "Я могу помочь вам:\n"
                        "• Создать заявку на IT-услуги\n"
                        "• Просмотреть ваши текущие заявки\n"
                        "• Отследить статус заявки\n"
                        "• Получить консультацию\n\n"
                        "Используйте кнопки меню для навигации или следующие команды:\n"
                        "• /start - Начать сначала\n"
                        "• /menu - Вернуться в главное меню\n"
                        "• /help - Получить помощь\n"
                        "• /cancel - Отменить текущее действие"
                    )
                    await self.send_message(user_id, welcome_message)
                    user_state.context["greeted"] = True
                    await self.storage.set_user_state(str(user_id), user_state.state, user_state.context)
                    
                    # Показываем основное меню после приветствия
                    menu_message = "Выберите действие:"
                    keyboard = await self.build_keyboard(DialogState.MAIN_MENU, {"show_main_menu": True})
                    await self.send_message(user_id, menu_message, keyboard)
                    return
                    
            except Exception as e:
                logger.error(f"Ошибка при получении состояния пользователя {user_id}: {e}", exc_info=True)
                raise
            
            # Обрабатываем служебные команды
            if message_text.lower() == "отменить заявку":
                logger.info(f"Пользователь {user_id} отменяет заявку")
                await self.handle_cancel(user_id, user_state)
                return
                
            if message_text.lower() == "удалить заявку":
                logger.info(f"Пользователь {user_id} удаляет заявку")
                await self.handle_delete_order(user_id, user_state)
                return

            # Обрабатываем состояние через dialog_handler
            try:
                logger.info(f"Обработка состояния через dialog_handler для пользователя {user_id}")
                new_state, response_message, keyboard_data = await self.dialog_handler.handle_state(
                    user_state,
                    message_text
                )
                logger.info(f"Получен ответ от dialog_handler: state={new_state}, message={response_message[:100]}...")
            except Exception as e:
                logger.error(f"Ошибка при обработке состояния пользователя {user_id}: {e}", exc_info=True)
                raise

            # Обновляем состояние пользователя
            try:
                logger.info(f"Обновление состояния пользователя {user_id} на {new_state.name}")
                user_state.state = new_state.name
                await self.storage.set_user_state(
                    str(user_id), 
                    user_state.state, 
                    user_state.context,
                    user_state.temp_data
                )
                self.user_states_cache[user_id] = user_state
            except Exception as e:
                logger.error(f"Ошибка при обновлении состояния пользователя {user_id}: {e}", exc_info=True)
                raise

            # Формируем и отправляем ответ
            try:
                logger.info(f"Формирование клавиатуры для пользователя {user_id}")
                keyboard = await self.build_keyboard(new_state, keyboard_data)
                
                logger.info(f"Отправка ответа пользователю {user_id}")
                success = await self.send_message(user_id, response_message, keyboard)
                if success:
                    logger.info(f"Ответ успешно отправлен пользователю {user_id}")
                else:
                    logger.error(f"Не удалось отправить ответ пользователю {user_id}")
            except Exception as e:
                logger.error(f"Ошибка при отправке ответа пользователю {user_id}: {e}", exc_info=True)
                raise
            
        except Exception as e:
            error_msg = f"Ошибка при обработке сообщения от пользователя {user_id}: {e}"
            logger.error(error_msg, exc_info=True)
            if user_id:
                await self.handle_error(user_id, error_msg)

    async def build_keyboard(self, state: DialogState, data: Dict[str, Any]) -> dict:
        """
        Создание клавиатуры для текущего состояния
        
        Args:
            state: Текущее состояние диалога
            data: Данные для формирования клавиатуры
            
        Returns:
            dict: Клавиатура в формате VK API
        """
        try:
            logger.debug(f"Создание клавиатуры для состояния {state} с данными {data}")
            
            buttons = []
            
            # Добавляем кнопки в зависимости от флагов
            if data.get("show_start"):
                buttons.extend(["Начать", "Помощь"])
                
            elif data.get("show_main_menu"):
                buttons.extend([
                    "Создать заявку",
                    "Мои заявки",
                    "Помощь"
                ])
                
            elif data.get("show_service_types"):
                buttons.extend([
                    "Услуги Населению",
                    "Услуги для Бизнеса",
                    "Назад"
                ])
                
            elif data.get("show_help"):
                buttons.extend([
                    "Создать заявку",
                    "Мои заявки",
                    "Назад в меню"
                ])
                
            elif data.get("show_cancel"):
                buttons.extend([
                    "Да, отменить",
                    "Нет, продолжить",
                    "В главное меню"
                ])
                
            elif data.get("show_error"):
                buttons.extend([
                    "Повторить",
                    "Помощь",
                    "В главное меню"
                ])
            
            # Добавляем кнопку "Назад" если нужно
            if data.get("show_back") and "Назад" not in buttons:
                buttons.append("Назад")
                
            # Если кнопок нет, добавляем кнопку возврата в меню
            if not buttons:
                buttons.append("В главное меню")
            
            # Разбиваем кнопки на ряды по 2 кнопки
            keyboard_buttons = []
            row = []
            
            for btn in buttons:
                row.append({
                    "action": {
                        "type": "text",
                        "label": btn[:40]  # Ограничение VK API
                    },
                    "color": "primary" if btn not in ["Отменить", "Назад", "В главное меню"] else "secondary"
                })
                
                if len(row) == 2:
                    keyboard_buttons.append(row)
                    row = []
            
            # Добавляем оставшиеся кнопки
            if row:
                keyboard_buttons.append(row)
            
            # Формируем клавиатуру
            keyboard = {
                "one_time": False,
                "buttons": keyboard_buttons
            }
            
            logger.debug(f"Создана клавиатура с кнопками: {buttons}")
            return keyboard
            
        except Exception as e:
            logger.error(f"Ошибка при создании клавиатуры: {e}", exc_info=True)
            # Возвращаем базовую клавиатуру с кнопкой меню
            return {
                "one_time": False,
                "buttons": [[{
                    "action": {
                        "type": "text",
                        "label": "В главное меню"
                    },
                    "color": "secondary"
                }]]
            }

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

    async def handle_error(self, user_id: int, error: str) -> None:
        """Обработка ошибок при работе с сообщениями"""
        try:
            error_message = "Произошла ошибка при обработке вашего сообщения. Попробуйте еще раз или напишите /start для перезапуска бота."
            await self.send_message(user_id, error_message)
            
            # Отправляем уведомление об ошибке в Telegram
            await TelegramService.notify_error("message_processing", {
                "user_id": user_id,
                "error": str(error)
            })
        except Exception as e:
            logger.error(f"Ошибка при обработке ошибки для пользователя {user_id}: {e}", exc_info=True)

    async def cleanup_cache(self) -> None:
        """
        Периодическая очистка кэша состояний пользователей
        """
        while True:
            try:
                await asyncio.sleep(3600)  # Очищаем раз в час
                current_time = datetime.now()
                
                # Удаляем состояния пользователей, неактивных более 24 часов
                to_remove = []
                for user_id, state in self.user_states_cache.items():
                    if (current_time - state.last_activity).total_seconds() > 86400:
                        to_remove.append(user_id)
                        
                for user_id in to_remove:
                    del self.user_states_cache[user_id]
                    
                logger.info(f"Очищено {len(to_remove)} неактивных состояний из кэша")
                
            except Exception as e:
                logger.error(f"Ошибка при очистке кэша: {e}")
                await asyncio.sleep(60)  # При ошибке ждем минуту перед повторной попыткой

    async def run(self) -> None:
        """
        Запуск прослушивания событий VK API
        """
        logger.info("Запуск VK бота...")
        
        try:
            # Запускаем задачу очистки кэша
            self.cache_cleanup_task = asyncio.create_task(self.cleanup_cache())
            
            # Проверяем подключение перед запуском
            try:
                group_info = self.vk.groups.getById()[0]
                logger.info(f"Подключение к VK API активно. Бот готов принимать сообщения в группе {group_info['name']}")
            except Exception as e:
                logger.error(f"Ошибка подключения к VK API: {e}")
                raise
            
            logger.info("Начинаю прослушивание событий...")
            
            # Основной цикл прослушивания событий
            while True:
                try:
                    for event in self.longpoll.listen():
                        if event.type == VkBotEventType.MESSAGE_NEW:
                            logger.info(f"Получено новое сообщение от пользователя {event.message.from_id}")
                            # Обрабатываем сообщение синхронно
                            await self.process_new_message(event)
                except vk_api.exceptions.ApiError as e:
                    logger.error(f"Ошибка API VK в цикле событий: {e}")
                    await asyncio.sleep(5)  # Ждем перед повторной попыткой
                except Exception as e:
                    logger.error(f"Ошибка при обработке событий: {e}", exc_info=True)
                    await asyncio.sleep(5)  # Ждем перед повторной попыткой
                    
        except Exception as e:
            logger.error(f"Критическая ошибка в работе бота: {e}", exc_info=True)
            raise
            
        finally:
            # Останавливаем задачу очистки кэша
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