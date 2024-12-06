import json
import logging
import aiosqlite
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from config.config import DATABASE_PATH, DB_CONFIG
from models.schemas import Order, UserState
from utils.helpers import PhoneNumberHelper, TextHelper, DateTimeHelper

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Создание базы данных и таблиц если они не существуют"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        async def init_db():
            async with aiosqlite.connect(self.db_path) as db:
                # Применяем pragma настройки
                for pragma, value in DB_CONFIG['pragmas'].items():
                    await db.execute(f"PRAGMA {pragma} = {value}")

                # Таблица заявок
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        business_type TEXT,
                        task TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP
                    )
                ''')

                # Таблица состояний пользователей
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS user_states (
                        user_id TEXT PRIMARY KEY,
                        state TEXT NOT NULL,
                        context TEXT NOT NULL,
                        temp_data TEXT,
                        updated_at TIMESTAMP NOT NULL
                    )
                ''')

                # Индексы для оптимизации
                await db.execute('CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)')
                await db.execute('CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)')
                
                await db.commit()

        import asyncio
        asyncio.run(init_db())

    async def create_order(self, user_id: str, name: str, phone: str, task: str, 
                          business_type: Optional[str] = None) -> int:
        """Создание новой заявки"""
        phone = PhoneNumberHelper.format_phone(phone)
        task = TextHelper.clean_text(task)
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            now = datetime.now().isoformat()
            
            cursor = await db.execute('''
                INSERT INTO orders (user_id, name, phone, business_type, task, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                RETURNING id
            ''', (user_id, name, phone, business_type, task, 'new', now))
            
            row = await cursor.fetchone()
            await db.commit()
            return row['id']

    async def get_user_orders(self, user_id: str, limit: int = 5) -> List[Order]:
        """Получение активных заявок пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            cursor = await db.execute('''
                SELECT * FROM orders 
                WHERE user_id = ? AND status != 'deleted'
                ORDER BY created_at DESC LIMIT ?
            ''', (user_id, limit))
            
            rows = await cursor.fetchall()
            return [Order.from_dict(dict(row)) for row in rows]

    async def get_order(self, order_id: int) -> Optional[Order]:
        """Получение заявки по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            cursor = await db.execute('''
                SELECT * FROM orders WHERE id = ? AND status != 'deleted'
            ''', (order_id,))
            
            row = await cursor.fetchone()
            return Order.from_dict(dict(row)) if row else None

    async def update_order(self, order_id: int, task: str) -> Optional[Order]:
        """Обновление заявки"""
        task = TextHelper.clean_text(task)
        now = datetime.now().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            cursor = await db.execute('''
                UPDATE orders 
                SET task = ?, updated_at = ?, status = 'updated'
                WHERE id = ? AND status != 'deleted'
                RETURNING *
            ''', (task, now, order_id))
            
            row = await cursor.fetchone()
            await db.commit()
            return Order.from_dict(dict(row)) if row else None

    async def delete_order(self, order_id: int) -> Optional[Order]:
        """Мягкое удаление заявки"""
        now = datetime.now().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Получаем заявку перед удалением
            cursor = await db.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
            order = await cursor.fetchone()
            
            if not order:
                return None
                
            await db.execute('''
                UPDATE orders 
                SET status = 'deleted', updated_at = ?
                WHERE id = ?
            ''', (now, order_id))
            
            await db.commit()
            return Order.from_dict(dict(order))

    async def set_user_state(self, user_id: str, state: str, 
                            context: Dict[str, Any], temp_data: Optional[Dict[str, Any]] = None) -> None:
        """Сохранение состояния пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            now = datetime.now().isoformat()
            
            await db.execute('''
                INSERT OR REPLACE INTO user_states 
                (user_id, state, context, temp_data, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_id,
                state,
                json.dumps(context, ensure_ascii=False),
                json.dumps(temp_data, ensure_ascii=False) if temp_data else None,
                now
            ))
            
            await db.commit()

    async def get_user_state(self, user_id: str) -> Optional[UserState]:
        """Получение состояния пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            cursor = await db.execute('''
                SELECT * FROM user_states WHERE user_id = ?
            ''', (user_id,))
            
            row = await cursor.fetchone()
            if row:
                return UserState(
                    user_id=row['user_id'],
                    state=row['state'],
                    context=json.loads(row['context']) if row['context'] else {},
                    temp_data=json.loads(row['temp_data']) if row['temp_data'] else {}
                )
            return None

    async def cleanup_old_states(self, hours: int = 24) -> int:
        """Очистка старых состояний пользователей"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                DELETE FROM user_states 
                WHERE datetime(updated_at) < datetime('now', ?)
            ''', (f'-{hours} hours',))
            
            deleted = cursor.rowcount
            await db.commit()
            return deleted