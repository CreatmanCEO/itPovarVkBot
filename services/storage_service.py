import json
import logging
from typing import List, Optional
from models.order import Order
from config.config import ORDERS_FILE, MAX_ORDERS

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.orders = self.load_orders()
        self.next_order_id = self._get_next_order_id()

    def load_orders(self) -> dict:
        """Загрузка заявок из файла"""
        try:
            with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Преобразуем данные в объекты Order
                orders = {}
                for user_id, user_orders in data.items():
                    orders[user_id] = [Order.from_dict(order) for order in user_orders]
                return orders
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка при чтении файла заявок: {e}")
            return {}

    def save_orders(self):
        """Сохранение заявок в файл"""
        try:
            data = {
                user_id: [order.to_dict() for order in orders]
                for user_id, orders in self.orders.items()
            }
            with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка при сохранении заявок: {e}")

    def _get_next_order_id(self) -> int:
        """Получение следующего номера заявки"""
        all_orders = [
            order.id
            for orders in self.orders.values()
            for order in orders
        ]
        return max(all_orders, default=0) + 1

    def create_order(self, user_id: str, name: str, phone: str, task: str) -> Order:
        """Создание новой заявки"""
        order = Order(
            id=self.next_order_id,
            user_id=user_id,
            name=name,
            phone=phone,
            task=task
        )

        if user_id not in self.orders:
            self.orders[user_id] = []
        
        # Если достигнут лимит заявок, удаляем самую старую
        if len(self.orders[user_id]) >= MAX_ORDERS:
            self.orders[user_id].pop(0)
        
        self.orders[user_id].append(order)
        self.next_order_id += 1
        self.save_orders()
        return order

    def get_user_orders(self, user_id: str) -> List[Order]:
        """Получение активных заявок пользователя"""
        return sorted(
            self.orders.get(user_id, []),
            key=lambda x: x.id,
            reverse=True
        )

    def get_order(self, user_id: str, order_id: int) -> Optional[Order]:
        """Получение конкретной заявки пользователя"""
        for order in self.orders.get(user_id, []):
            if order.id == order_id:
                return order
        return None

    def update_order(self, user_id: str, order_id: int, new_task: str) -> bool:
        """Обновление текста заявки"""
        order = self.get_order(user_id, order_id)
        if order:
            order.task = new_task
            self.save_orders()
            return True
        return False

    def delete_order(self, user_id: str, order_id: int) -> bool:
        """Удаление заявки"""
        if user_id in self.orders:
            initial_length = len(self.orders[user_id])
            self.orders[user_id] = [
                order for order in self.orders[user_id]
                if order.id != order_id
            ]
            if len(self.orders[user_id]) < initial_length:
                self.save_orders()
                return True
        return False