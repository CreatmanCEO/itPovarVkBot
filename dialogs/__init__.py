"""
Модуль диалогов бота IT Повар

Этот модуль реализует всю логику взаимодействия с пользователем через диалоги.
Он включает в себя:
- Управление состояниями диалога
- Обработку пользовательского ввода
- Генерацию клавиатур
- Многоязычную поддержку
- Валидацию данных

Структура модуля:
- states.py: Определение состояний диалога и переходов между ними
- keyboard.py: Генерация клавиатур для разных состояний
- handlers.py: Обработчики пользовательского ввода
- messages.py: Шаблоны сообщений и текстов

Основные возможности:
1. Управление состояниями:
   - Определение текущего состояния
   - Валидация возможных переходов
   - Сохранение контекста диалога

2. Навигация:
   - Глобальные команды (/start, /menu, /help, /cancel)
   - Возврат в предыдущее состояние
   - Отмена текущего действия
   - Контекстная помощь

3. Валидация ввода:
   - Проверка формата данных
   - Обработка ошибок
   - Повторный запрос при некорректном вводе

4. Многоязычность:
   - Поддержка русского и английского языков
   - Возможность смены языка в процессе диалога
   - Сохранение языковых предпочтений

5. Управление заявками:
   - Создание новых заявок
   - Просмотр существующих
   - Фильтрация по статусу
   - История заявок
   - Редактирование и отмена
   - Система отзывов

Пример использования:

```python
from dialogs import DialogState, KeyboardBuilder, GLOBAL_COMMANDS

# Получение клавиатуры для состояния
keyboard = KeyboardBuilder.get_state_keyboard(DialogState.MAIN_MENU)

# Проверка глобальной команды
if message.text in GLOBAL_COMMANDS:
    new_state = GLOBAL_COMMANDS[message.text]
    # Переход в новое состояние...

# Обработка состояния
if current_state == DialogState.CONTACT_INPUT:
    if validate_phone(message.text):
        # Переход к подтверждению...
    else:
        # Переход к повторному вводу...
```

Примечания:
1. Все состояния определены в классе DialogState
2. Переходы между состояниями описаны в STATE_TRANSITIONS
3. Тексты сообщений хранятся в STATE_MESSAGES
4. Глобальные команды доступны через GLOBAL_COMMANDS
"""

from .states import DialogState, OrderStatus, STATE_TRANSITIONS, STATE_MESSAGES, GLOBAL_COMMANDS
from .handlers import DialogHandler
from .messages import MessageBuilder
from .keyboard import KeyboardBuilder, MAIN_MENU_KEYBOARD, SERVICE_TYPE_KEYBOARD, CONFIRMATION_KEYBOARD, HELP_KEYBOARD, CANCEL_KEYBOARD

__all__ = [
    'DialogState',
    'OrderStatus',
    'STATE_TRANSITIONS',
    'STATE_MESSAGES',
    'GLOBAL_COMMANDS',
    'DialogHandler',
    'MessageBuilder',
    'KeyboardBuilder',
    'MAIN_MENU_KEYBOARD',
    'SERVICE_TYPE_KEYBOARD',
    'CONFIRMATION_KEYBOARD',
    'HELP_KEYBOARD',
    'CANCEL_KEYBOARD'
]