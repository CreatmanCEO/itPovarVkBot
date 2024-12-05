import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import requests
from flask import Flask, request, jsonify

# Токены
VK_TOKEN = "vk1.a.KX1Q0v6Y3C420UgfV7zPoDL4V1OOYdengHYQjQyh_MtFvYca-M_871lyF0-g_qe-9Hn-MNA02wU73OjyBvX9uhh9aM9Afp7wbiBupahqPAoPoUZnEFC-BArLAYJCzX6PpN5sNnlw_qS5HlN9OASoNrvbJ2PFkIF48Dn9uqMG4zB995jvF4sk100fSSHiL5HlgclOrOs7qovLJKeyulnm8A"
TG_TOKEN = "8157141771:AAHxRzh3_kCS1amiPTaXw3FTYnN-GrBdt-g"
TG_CHAT_ID = "@CreatmanLead_bot"

# Flask для обработки POST-запросов с сайта
app = Flask(__name__)

# Telegram отправка
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    data = {"chat_id": TG_CHAT_ID, "text": message}
    requests.post(url, data=data)

# VK API
vk_session = vk_api.VkApi(token=VK_TOKEN)
longpoll = VkBotLongPoll(vk_session, 228564877)
vk = vk_session.get_api()

# VK отправка сообщений
def send_message(user_id, message, keyboard=None):
    vk.messages.send(
        user_id=user_id,
        message=message,
        random_id=0,
        keyboard=keyboard
    )

# Обработка заявок с сайта
@app.route("/submit", methods=["POST"])
def handle_form_submission():
    data = request.json
    name = data.get("name")
    phone = data.get("phone")
    message = data.get("message")
    
    if not name or not phone or not message:
        return jsonify({"error": "Некорректные данные"}), 400

    # Формируем сообщение
    tg_message = (f"Новая заявка с сайта:\n"
                  f"Имя: {name}\n"
                  f"Телефон: {phone}\n"
                  f"Сообщение: {message}")
    
    send_to_telegram(tg_message)
    return jsonify({"success": "Заявка отправлена"}), 200

# VK Bot обработка событий
def handle_event(event):
    user_id = event.message.from_id
    text = event.message.text.lower()
    user_info = vk.users.get(user_ids=user_id)[0]
    user_name = user_info["first_name"]

    if text == "начать":
        message = (f"Здравствуйте, {user_name}! Я — IT-Помощь в Поварово. "
                   "Мы занимаемся настройкой компьютеров, установкой программ, обучением работе с ИИ "
                   "и другими IT-услугами для частных лиц и бизнеса. Чем я могу вам помочь?")
        keyboard = create_keyboard(["Услуги Населению", "Услуги для Бизнеса"])
        send_message(user_id, message, keyboard)
    elif text == "услуги населению":
        message = ("Мы предлагаем услуги:\n"
                   "- Ремонт и настройка компьютеров\n"
                   "- Установка антивирусов\n"
                   "- Настройка интернета и Wi-Fi\n"
                   "- Обучение работе с компьютером и программами\n\n"
                   "Что случилось и как мы можем вам помочь?")
        send_message(user_id, message)
    elif text == "услуги для бизнеса":
        message = ("Пожалуйста, можете ли вы вкратце описать деятельность вашей компании?")
        keyboard = create_keyboard(["Да", "Нет"])
        send_message(user_id, message, keyboard)
    elif text == "да":
        send_message(user_id, "Введите краткое описание вашей компании:")
    elif text == "нет":
        send_message(user_id, "Опишите, какая помощь вам требуется:")
    else:
        send_message(user_id, "Спасибо за обращение! Мы свяжемся с вами в ближайшее время.")

# Генерация клавиатуры
def create_keyboard(buttons):
    keyboard = {
        "one_time": False,
        "buttons": [[{"action": {"type": "text", "payload": "{}", "label": btn}, "color": "primary"}] for btn in buttons]
    }
    return vk_api.utils.json.dumps(keyboard)

# Основной запуск
if __name__ == "__main__":
    import threading

    # Запускаем VK Bot
    def vk_bot():
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                handle_event(event)

    # Запускаем Flask
    vk_thread = threading.Thread(target=vk_bot, daemon=True)
    vk_thread.start()
    app.run(host="0.0.0.0", port=5000)
