import asyncio
import logging
import logging.config
import os
from pathlib import Path
from aiohttp import web
from flask import Flask, request, jsonify

from config.config import (
    APP_HOST,
    APP_PORT,
    DATABASE_PATH,
    LOGGING_CONFIG,
    validate_config
)
from services.vk_service import VKService
from services.storage_service import StorageService
from utils.helpers import PhoneNumberHelper, TextHelper

# Проверяем конфигурацию
validate_config()

# Настройка логирования
logging.config.dictConfig(LOGGING_CONFIG)
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

async def init_app():
    """Инициализация веб-приложения"""
    app = web.Application()
    app.router.add_get('/', handle_health_check)
    app.router.add_post('/submit', handle_form_submission)
    return app

async def run_web_app():
    """Запуск веб-приложения"""
    app = await init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, APP_HOST, APP_PORT)
    await site.start()
    logger.info(f"Веб-сервер запущен на {APP_HOST}:{APP_PORT}")

async def main():
    """Основная функция запуска"""
    try:
        logger.info("Запуск приложения...")
        
        # Проверяем наличие необходимых переменных окружения
        if not os.getenv('VK_TOKEN'):
            logger.error("Не установлен токен VK API (VK_TOKEN)")
            raise ValueError("VK_TOKEN is not set")
            
        # Запускаем веб-сервер
        logger.info(f"Запуск веб-сервера на {APP_HOST}:{APP_PORT}...")
        await run_web_app()
        logger.info("Веб-сервер успешно запущен")
        
        # Запускаем VK бота
        logger.info("Инициализация VK бота...")
        try:
            # Запускаем бота и ждем его завершения
            await vk_service.run()
        except Exception as e:
            logger.error(f"Ошибка при запуске VK бота: {e}", exc_info=True)
            raise
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения работы...")
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске приложения: {e}", exc_info=True)
        raise
    finally:
        # Останавливаем бота при выходе
        logger.info("Остановка приложения...")
        await vk_service.stop()

if __name__ == "__main__":
    try:
        # Запускаем асинхронное приложение
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения работы...")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при запуске: {e}", exc_info=True)
    finally:
        logger.info("Приложение остановлено")