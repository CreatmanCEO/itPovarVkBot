import requests
import logging
from config.config import TELEGRAM_WEBHOOK
from models.order import Order

logger = logging.getLogger(__name__)

class TelegramService:
    @staticmethod
    def send_notification(message_type: str, data: dict) -> bool:
        """
        Отправка уведомления в Telegram
        
        Args:
            message_type: Тип сообщения ('new_order', 'update_order', 'delete_order')
            data: Данные для отправки
        """
        try:
            if message_type == "new_order":
                message = {
                    "name": f"[ВК] {data['name']}",
                    "phone": data['phone'],
                    "message": f"Новая заявка №{data['order_id']}\n{data['task']}"
                }
            elif message_type == "update_order":
                message = {
                    "name": f"[ВК] Изменение заявки №{data['order_id']}",
                    "phone": data['name'],
                    "message": f"Новый текст заявки:\n{data['task']}"
                }
            elif message_type == "delete_order":
                message = {
                    "name": f"[ВК] Удаление заявки №{data['order_id']}",
                    "phone": data['name'],
                    "message": "Заявка удалена пользователем"
                }
            else:
                raise ValueError(f"Неизвестный тип сообщения: {message_type}")

            response = requests.post(
                TELEGRAM_WEBHOOK,
                headers={'Content-Type': 'application/json'},
                json=message
            )
            
            if not response.ok:
                logger.error(f"Ошибка отправки в Telegram: {response.text}")
                return False
                
            logger.info(f"Уведомление {message_type} успешно отправлено в Telegram")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при отправке в Telegram: {e}")
            return False

    @classmethod
    def notify_new_order(cls, order: Order) -> bool:
        """Уведомление о новой заявке"""
        return cls.send_notification("new_order", {
            "name": order.name,
            "phone": order.phone,
            "task": order.task,
            "order_id": order.id
        })

    @classmethod
    def notify_order_update(cls, order: Order) -> bool:
        """Уведомление об изменении заявки"""
        return cls.send_notification("update_order", {
            "name": order.name,
            "task": order.task,
            "order_id": order.id
        })

    @classmethod
    def notify_order_delete(cls, order: Order) -> bool:
        """Уведомление об удалении заявки"""
        return cls.send_notification("delete_order", {
            "name": order.name,
            "order_id": order.id
        })