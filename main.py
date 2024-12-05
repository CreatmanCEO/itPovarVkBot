import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import requests
from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Токены
VK_TOKEN = "vk1.a.KX1Q0v6Y3C420UgfV7zPoDL4V1OOYdengHYQjQyh_MtFvYca-M_871lyF0-g_qe-9Hn-MNA02wU73OjyBvX9uhh9aM9Afp7wbiBupahqPAoPoUZnEFC-BArLAYJCzX6PpN5sNnlw_qS5HlN9OASoNrvbJ2PFkIF48Dn9uqMG4zB995jvF4sk100fSSHiL5HlgclOrOs7qovLJKeyulnm8A"
TG_TOKEN = "8157141771:AAHxRzh3_kCS1amiPTaXw3FTYnN-GrBdt-g"
TG_CHAT_ID = "@CreatmanLead_bot"

# Flask для обработки POST-запросов с сайта
app = Flask(__name__)

class ITBot:
    def __init__(self):
        self.vk_session = vk_api.VkApi(token=VK_TOKEN)
        self.longpoll = VkBotLongPoll(self.vk_session, 228564877)
        self.vk = self.vk_session.get_api()
        self.user_states = {}  # Для хранения состояний пользователей

    def send_to_telegram(self, message):
        """Отправка сообщения в Telegram"""
        try:
            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
            data = {"chat_id": TG_CHAT_ID, "text": message}
            response = requests.post(url, data=data)
            response.raise_for_status()
            logger.info(f"Сообщение успешно отправлено в Telegram: {message[:50]}...")
        except Exception as e:
            logger.error(f"Ошибка при отправке в Telegram: {e}")

    def send_message(self, user_id, message, keyboard=None):
        """Отправка сообщения VK с обработкой ошибок"""
        try:
            keyboard_json = json.dumps(keyboard) if keyboard else None
            self.vk.messages.send(
                user_id=user_id,
                message=message,
                random_id=int(datetime.now().timestamp() * 1000),
                keyboard=keyboard_json
            )
            logger.info(f"Сообщение отправлено пользователю {user_id}: {message[:50]}...")
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {e}")

    def create_keyboard(self, buttons):
        """Создание клавиатуры с проверкой входных данных"""
        if not buttons or not isinstance(buttons, list):
            return None
        
        return {
            "one_time": False,
            "buttons": [
                [
                    {
                        "action": {
                            "type": "text",
                            "label": str(btn)[:40]  # Ограничение длины текста кнопки
                        },
                        "color": "primary"
                    }
                ] for btn in buttons
            ]
        }

    def handle_event(self, event):
        """Обработка событий от пользователя"""
        try:
            user_id = event.message.from_id
            text = event.message.text.lower() if event.message.text else ""
            user_info = self.vk.users.get(user_ids=user_id)[0]
            user_name = user_info["first_name"]

            logger.info(f"Получено сообщение: {text} от {user_name} ({user_id})")

            # Обработка команд
            if text in ["", "начать", "привет", "здравствуйте", "добрый день", "добрый вечер"]:
                self.handle_greeting(user_id, user_name)
            elif text == "услуги населению":
                self.handle_personal_services(user_id)
            elif text == "услуги для бизнеса":
                self.handle_business_services(user_id)
            elif text == "да":
                self.send_message(user_id, "Введите краткое описание вашей компании:")
                self.user_states[user_id] = "awaiting_company_description"
            elif text == "нет":
                self.send_message(user_id, "Опишите, какая помощь вам требуется:")
                self.user_states[user_id] = "awaiting_help_description"
            elif user_id in self.user_states:
                self.handle_user_input(user_id, text, user_name)
            else:
                self.handle_unknown_command(user_id, user_name)

        except Exception as e:
            logger.error(f"Ошибка при обработке события: {e}")
            self.send_message(user_id, "Произошла ошибка при обработке вашего запроса. Попробуйте позже.")

    def handle_greeting(self, user_id, user_name):
        """Обработка приветствия"""
        message = (
            f"Здравствуйте, {user_name}! Я автоматический помощник сообщества — IT-Помощь в Поварово.\n"
            "Мы занимаемся:\n"
            "• Настройкой компьютеров и устройств\n"
            "• Разработкой программ и приложений\n"
            "• Обучением работе с ИИ и программами\n"
            "• Автоматизацией бизнес-процессов и еще много чем...\n\n"
            "Как я могу вам помочь?"
        )
        keyboard = self.create_keyboard(["Услуги Населению", "Услуги для Бизнеса"])
        self.send_message(user_id, message, keyboard)

    def handle_personal_services(self, user_id):
        """Обработка запроса услуг для населения"""
        message = (
            "Наши услуги для частных лиц:\n\n"
            "🔧 Компьютерная помощь:\n"
            "• Настройка и ремонт компьютеров\n"
            "• Установка программ и антивирусов\n"
            "• Восстановление данных\n\n"
            "💻 Разработка:\n"
            "• Создание сайтов и приложений\n"
            "• Разработка чат-ботов\n"
            "• Автоматизация процессов\n\n"
            "📱 Обучение:\n"
            "• Работа с компьютером и программами\n"
            "• Основы программирования\n"
            "• Работа с искусственным интеллектом\n\n"
            "Опишите вашу задачу, и мы подберем оптимальное решение!"
        )
        self.send_message(user_id, message)
        self.user_states[user_id] = "awaiting_personal_task"

    def handle_business_services(self, user_id):
        """Обработка запроса услуг для бизнеса"""
        message = (
            "Для подбора оптимального решения для вашего бизнеса, "
            "пожалуйста, опишите вкратце деятельность вашей компании."
        )
        keyboard = self.create_keyboard(["Да", "Нет"])
        self.send_message(user_id, message, keyboard)

    def handle_user_input(self, user_id, text, user_name):
        """Обработка пользовательского ввода в зависимости от состояния"""
        state = self.user_states.pop(user_id)  # Удаляем состояние после обработки
        
        if state in ["awaiting_company_description", "awaiting_help_description", "awaiting_personal_task"]:
            # Формируем сообщение для отправки в Telegram
            message_type = {
                "awaiting_company_description": "Описание компании",
                "awaiting_help_description": "Запрос помощи",
                "awaiting_personal_task": "Личный запрос"
            }[state]
            
            tg_message = (
                f"Новый запрос от пользователя:\n"
                f"Тип: {message_type}\n"
                f"Имя: {user_name}\n"
                f"ID: {user_id}\n"
                f"Сообщение: {text}"
            )
            self.send_to_telegram(tg_message)
            
            # Отправляем подтверждение пользователю
            response = (
                "Спасибо за обращение! Мы получили ваш запрос и свяжемся с вами в ближайшее время.\n"
                "Если у вас есть дополнительные вопросы, не стесняйтесь их задавать."
            )
            self.send_message(user_id, response)

    def handle_unknown_command(self, user_id, user_name):
        """Обработка неизвестной команды"""
        message = (
            f"Извините, {user_name}, я не совсем понял ваш запрос.\n"
            "Выберите, пожалуйста, одну из доступных опций:"
        )
        keyboard = self.create_keyboard(["Услуги Населению", "Услуги для Бизнеса"])
        self.send_message(user_id, message, keyboard)

@app.route("/submit", methods=["POST"])
def handle_form_submission():
    """Обработка заявок с сайта"""
    try:
        data = request.json
        required_fields = ["name", "phone", "message"]
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Не все обязательные поля заполнены"}), 400

        tg_message = (
            "Новая заявка с сайта:\n"
            f"Имя: {data['name']}\n"
            f"Телефон: {data['phone']}\n"
            f"Сообщение: {data['message']}"
        )
        
        bot.send_to_telegram(tg_message)
        return jsonify({"success": "Заявка успешно отправлена"}), 200
        
    except Exception as e:
        logger.error(f"Ошибка при обработке формы: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

if __name__ == "__main__":
    import threading

    # Создаем экземпляр бота
    bot = ITBot()

    # Запускаем VK Bot
    def vk_bot():
        logger.info("Запуск VK бота...")
        try:
            for event in bot.longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    bot.handle_event(event)
        except Exception as e:
            logger.error(f"Критическая ошибка в работе бота: {e}")

    # Запускаем Flask и VK бот
    vk_thread = threading.Thread(target=vk_bot, daemon=True)
    vk_thread.start()
    
    logger.info("Запуск веб-сервера...")
    app.run(host="0.0.0.0", port=5000)