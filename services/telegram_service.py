import aiohttp
import logging
import os
from datetime import datetime
from typing import Optional, Any, Dict
from models.schemas import Order
from utils.helpers import OrderHelper, PhoneNumberHelper, TextHelper, DateTimeHelper

logger = logging.getLogger(__name__)

class TelegramService:
    """Сервис для отправки уведомлений в Telegram"""
    
    WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK", "https://telegram-form.creatmanick-850.workers.dev")
    
    @staticmethod
    async def notify_new_order(order: Order) -> bool:
        """Уведомление о новой заявке"""
        if not TelegramService.WEBHOOK_URL:
            logger.warning("TELEGRAM_WEBHOOK не настроен, уведомления отключены")
            return False
            
        order_number = OrderHelper.generate_order_number(order.id)
        status_emoji = OrderHelper.get_status_emoji('new')
        
        business_type_text = f"Тип бизнеса: {order.business_type}\n" if order.business_type else ""
        
        message = (
            f"{status_emoji} [ВК] Новая заявка {order_number}\n"
            f"От: {order.name}\n"
            f"Телефон: {PhoneNumberHelper.format_phone(order.phone)}\n"
            f"{business_type_text}"
            f"Задача: {TextHelper.clean_text(order.task)}\n"
            f"Дата: {DateTimeHelper.format_datetime(order.created_at)}"
        )
        return await TelegramService._send_notification(message)

    @staticmethod
    async def notify_order_update(order: Order, old_task: str) -> bool:
        """Уведомление об изменении заявки"""
        order_number = OrderHelper.generate_order_number(order.id)
        status_emoji = OrderHelper.get_status_emoji('updated')
        
        message = (
            f"{status_emoji} [ВК] Изменение заявки {order_number}\n"
            f"От: {order.name}\n"
            f"Старый текст: {TextHelper.truncate(old_task, 100)}\n"
            f"Новый текст: {TextHelper.truncate(order.task, 100)}\n"
            f"Дата изменения: {DateTimeHelper.format_datetime(datetime.now())}"
        )
        return await TelegramService._send_notification(message)

    @staticmethod
    async def notify_order_delete(order: Order) -> bool:
        """Уведомление об удалении заявки"""
        order_number = OrderHelper.generate_order_number(order.id)
        status_emoji = OrderHelper.get_status_emoji('deleted')
        
        message = (
            f"{status_emoji} [ВК] Удаление заявки {order_number}\n"
            f"От: {order.name}\n"
            f"Описание: {TextHelper.truncate(order.task, 100)}\n"
            f"Дата удаления: {DateTimeHelper.format_datetime(datetime.now())}"
        )
        return await TelegramService._send_notification(message)

    @staticmethod
    async def notify_error(error_type: str, details: Dict[str, Any]) -> bool:
        """Уведомление об ошибке в работе бота"""
        message = (
            "⚠️ [ВК] Ошибка в работе бота\n"
            f"Тип: {error_type}\n"
            f"Детали: {details}\n"
            f"Время: {DateTimeHelper.format_datetime(datetime.now())}"
        )
        return await TelegramService._send_notification(message)

    @staticmethod
    async def _send_notification(message: str) -> bool:
        """Отправка уведомления в Telegram"""
        if not TelegramService.WEBHOOK_URL:
            logger.warning("TELEGRAM_WEBHOOK не настроен, уведомления отключены")
            return False
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    TelegramService.WEBHOOK_URL,
                    json={
                        "name": "VK Bot",
                        "phone": "System",
                        "message": message
                    }
                ) as response:
                    if response.status == 200:
                        logger.info("Уведомление успешно отправлено в Telegram")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка отправки в Telegram: {error_text}")
                        return False
        except Exception as e:
            logger.error(f"Ошибка при отправке в Telegram: {str(e)}")
            return False