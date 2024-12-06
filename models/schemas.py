from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class Order(BaseModel):
    """Базовая модель заявки"""
    id: Optional[int] = None
    user_id: str
    name: str
    phone: str
    task: str
    business_type: Optional[str] = None
    status: str = Field(default="new")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    def to_dict(self) -> dict:
        """Преобразование в словарь для хранения"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'phone': self.phone,
            'task': self.task,
            'business_type': self.business_type,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Order':
        """Создание объекта из словаря"""
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str) and data['updated_at']:
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)

class UserState(BaseModel):
    """Модель состояния пользователя"""
    user_id: str
    state: str
    context: Dict[str, Any] = Field(default_factory=dict)
    temp_data: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True

class UserOrderInput(BaseModel):
    """Модель для валидации пользовательского ввода"""
    business_type: Optional[str] = None
    task: Optional[str] = None
    phone: Optional[str] = None
    name: str
    user_id: str