# IT Повар - Бот ВКонтакте

[English version below](#it-cook---vk-bot)

## О проекте

IT Повар - это бот для ВКонтакте, который помогает автоматизировать обработку заявок и взаимодействие с клиентами. Бот обрабатывает заявки как из ВКонтакте, так и с веб-сайта.

### Основные возможности

- Прием и обработка заявок из ВКонтакте
- API для приема заявок с веб-сайта
- Хранение заявок в базе данных
- Автоматические уведомления
- Валидация данных
- Многоязычная поддержка
- Система отзывов и рейтингов
- История заявок и фильтрация

### Глобальные команды

В любой момент диалога доступны следующие команды:
- `/start` - Начать диалог сначала
- `/menu` - Вернуться в главное меню
- `/help` - Получить справку
- `/cancel` - Отменить текущее действие

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/itPovarVkBot.git
cd itPovarVkBot
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` в корневой директории и добавьте необходимые переменные окружения:
```env
VK_TOKEN=your_vk_token
APP_HOST=localhost
APP_PORT=8080
DATABASE_PATH=./data/database.sqlite
DEFAULT_LOCALE=ru
SECRET_KEY=your_secret_key_here
```

## Структура диалогов

### Основные состояния
- Стартовое меню
- Выбор языка
- Главное меню
- Создание заявки
- Просмотр заявок
- Управление заявками

### Создание заявки
1. Выбор типа услуг:
   - Услуги для населения
   - Услуги для бизнеса

2. Для бизнеса:
   - Описание деятельности компании
   - Описание требуемой помощи

3. Для частных лиц:
   - Выбор категории услуг
   - Описание задачи

4. Общие шаги:
   - Ввод контактных данных
   - Подтверждение заявки

### Управление заявками
- Просмотр активных заявок
- Фильтрация по статусу
- История заявок
- Редактирование заявок
- Отмена заявок
- Оставление отзывов

### Навигация
- Возврат в главное меню из любого состояния
- Отмена текущего действия с подтверждением
- Пошаговый возврат назад
- Контекстная помощь

## Структура проекта

```
itPovarVkBot/
├── src/
│   ├── config/         # Конфигурационные файлы
│   ├── services/       # Сервисы (VK, хранилище)
│   ├── models/         # Модели данных
│   ├── utils/          # Вспомогательные функции
│   └── dialogs/        # Диалоги и сценарии
├── tests/              # Тесты
├── locales/            # Языковые ресурсы
├── logs/               # Логи
└── data/               # База данных
```

## Разработка

### Тестирование

```bash
pytest tests/
```

### Линтинг

```bash
flake8 src/
```

## Развертывание

### Docker

```bash
docker build -t it-povar-bot .
docker run -d --name it-povar-bot it-povar-bot
```

## Поддержка

При возникновении проблем создайте Issue в репозитории или обратитесь к разработчикам.

---

# IT Cook - VK Bot

## About

IT Cook is a VK bot that helps automate request processing and client interactions. The bot handles requests from both VK and website.

### Key Features

- Processing VK requests
- Web API for website requests
- Database storage
- Automatic notifications
- Data validation
- Multilingual support
- Review and rating system
- Order history and filtering

### Global Commands

The following commands are available at any point in the dialog:
- `/start` - Start dialog from beginning
- `/menu` - Return to main menu
- `/help` - Get help
- `/cancel` - Cancel current action

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/itPovarVkBot.git
cd itPovarVkBot
```

2. Create virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file in the root directory and add required environment variables:
```env
VK_TOKEN=your_vk_token
APP_HOST=localhost
APP_PORT=8080
DATABASE_PATH=./data/database.sqlite
DEFAULT_LOCALE=ru
SECRET_KEY=your_secret_key_here
```

## Dialog Structure

### Main States
- Start menu
- Language selection
- Main menu
- Order creation
- Order viewing
- Order management

### Order Creation
1. Service type selection:
   - Services for individuals
   - Business services

2. For business:
   - Company description
   - Required assistance description

3. For individuals:
   - Service category selection
   - Task description

4. Common steps:
   - Contact information input
   - Order confirmation

### Order Management
- Active orders viewing
- Status filtering
- Order history
- Order editing
- Order cancellation
- Leaving reviews

### Navigation
- Return to main menu from any state
- Cancel current action with confirmation
- Step-by-step return
- Contextual help

## Project Structure

```
itPovarVkBot/
├── src/
│   ├── config/         # Configuration files
│   ├── services/       # Services (VK, storage)
│   ├── models/         # Data models
│   ├── utils/          # Helper functions
│   └── dialogs/        # Dialogs and scenarios
├── tests/              # Tests
├── locales/            # Language resources
├── logs/               # Logs
└── data/               # Database
```

## Development

### Testing

```bash
pytest tests/
```

### Linting

```bash
flake8 src/
```

## Deployment

### Docker

```bash
docker build -t it-povar-bot .
docker run -d --name it-povar-bot it-povar-bot
```

## Support

If you encounter any issues, please create an Issue in the repository or contact the developers. 