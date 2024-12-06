import asyncio
import logging
from pathlib import Path
from aiohttp import web
from flask import Flask, request, jsonify

from config.config import APP_HOST, APP_PORT, DATABASE_PATH
from services.vk_service import VKService
from services.storage_service import StorageService
from utils.helpers import PhoneNumberHelper, TextHelper

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

# Инициализация сервисов
storage = StorageService()
vk_service = VKService()

# Создаем директорию для базы данных если её нет
Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)

async def handle_form_submission(request):
    """Обработка заявок с сайта"""
    try:
        data = await request.json()
        
        # Проверка обязательных полей
        required_fields = ["name", "phone", "message"]
        if not all(field in data for field in required_fields):
            return web.json_response(
                {"error": "Не все обязательные поля заполнены"}, 
                status=400
            )

        # Валидация и форматирование данных
        if not PhoneNumberHelper.is_valid_phone(data['phone']):
            return web.json_response(
                {"error": "Некорректный формат номера телефона"}, 
                status=400
            )

        # Форматируем данные
        formatted_data = {
            "name": TextHelper.clean_text(data['name']),
            "phone": PhoneNumberHelper.format_phone(data['phone']),
            "task": TextHelper.clean_text(data['message']),
            "source": "website"
        }

        # Создаем заявку
        order_id = await storage.create_order(
            user_id="website",
            name=formatted_data['name'],
            phone=formatted_data['phone'],
            task=formatted_data['task']
        )

        return web.json_response({
            "success": True,
            "order_id": order_id
        })

    except Exception as e:
        logger.error(f"Ошибка обработки формы: {e}")
        return web.json_response(
            {"error": "Внутренняя ошибка сервера"}, 
            status=500
        )

async def handle_health_check(request):
    """Проверка работоспособности сервиса"""
    return web.Response(text="Service is running", status=200)

async def start_vk_bot():
    """Запуск бота ВКонтакте"""
    try:
        logger.info("Запуск VK бота...")
        await vk_service.run()
    except Exception as e:
        logger.error(f"Критическая ошибка в работе VK бота: {e}")

async def init_app():
    """Инициализация веб-приложения"""
    app = web.Application()
    app.router.add_get('/', handle_health_check)  # Добавляем эндпоинт проверки работоспособности
    app.router.add_post('/submit', handle_form_submission)
    return app

async def main():
    """Основная функция запуска"""
    try:
        # Запускаем веб-сервер
        app = await init_app()
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, APP_HOST, APP_PORT)
        
        logger.info(f"Запуск веб-сервера на {APP_HOST}:{APP_PORT}")
        await site.start()

        # Запускаем VK бота
        bot_task = asyncio.create_task(start_vk_bot())
        
        # Создаем бесконечную задачу для веб-сервера
        web_task = asyncio.create_task(asyncio.Event().wait())
        
        # Ждем выполнения обеих задач
        await asyncio.gather(web_task, bot_task)
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        if 'runner' in locals():
            await runner.cleanup()

if __name__ == "__main__":
    try:
        # Запускаем асинхронное приложение
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Завершение работы приложения...")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")