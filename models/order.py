from dataclasses import dataclass
from datetime import datetime

@dataclass
class Order:
    id: int
    user_id: str
    name: str
    phone: str
    task: str
    date: str = None

    def __post_init__(self):
        if self.date is None:
            self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self):
        """Конвертация заявки в словарь для сохранения"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'phone': self.phone,
            'task': self.task,
            'date': self.date
        }

    @classmethod
    def from_dict(cls, data):
        """Создание заявки из словаря"""
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            name=data['name'],
            phone=data['phone'],
            task=data['task'],
            date=data['date']
        )