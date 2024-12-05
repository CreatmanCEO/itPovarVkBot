import logging
import threading
from flask import Flask, request, jsonify
from config.config import APP_HOST, APP_PORT
from services.vk_service import VKService

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация Flask
app = Flask(__name__)

# Создание экземпляра VK сервиса
vk_service = VKService()

@app.route("/submit", methods=["POST"])
def handle_form_submission():
    """Обработка заявок с сайта"""
    try:
        data = request.json
        if not all(key in data for key in ["name", "phone", "message"]):
            return jsonify({"error": "Неполные данные"}), 400
        return jsonify({"success": True}), 200
        
    except Exception as e:
        logger.error(f"Ошибка обработки формы: {e}")
        return jsonify({"error": str(e)}), 500

def run_vk_bot():
    """Запуск бота ВКонтакте в отдельном потоке"""
    try:
        vk_service.run()
    except Exception as e:
        logger.error(f"Ошибка в работе VK бота: {e}")

if __name__ == "__main__":
    # Запуск VK бота в отдельном потоке
    vk_thread = threading.Thread(target=run_vk_bot, daemon=True)
    vk_thread.start()
    
    # Запуск веб-сервера
    logger.info("Запуск веб-сервера...")
    app.run(host=APP_HOST, port=APP_PORT)