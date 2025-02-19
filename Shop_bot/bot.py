import os
import telebot
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN)
user_sessions = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Привет! Нажмите /contact, чтобы связаться с администратором.")

@bot.message_handler(commands=['contact'])
def contact_admin(message):
    """Соединяет пользователя с администратором"""
    user_sessions[message.chat.id] = ADMIN_ID
    user_sessions[ADMIN_ID] = message.chat.id

    bot.send_message(ADMIN_ID, f"🔔 Новый запрос от пользователя {message.chat.id}.")
    bot.send_message(message.chat.id, "✅ Вы связаны с администратором. Напишите сообщение, и он его получит.\n\nДля выхода введите /stop")

@bot.message_handler(commands=['stop'])
def stop_chat(message):
    """Позволяет пользователю или админу завершить беседу"""
    if message.chat.id in user_sessions:
        other_party = user_sessions.pop(message.chat.id)
        if other_party in user_sessions:
            del user_sessions[other_party]

        bot.send_message(message.chat.id, "❌ Беседа завершена. Вы можете снова написать /contact, чтобы связаться с админом.")
        bot.send_message(other_party, "❌ Собеседник завершил беседу.") if other_party != ADMIN_ID else None

@bot.message_handler(func=lambda message: message.chat.id in user_sessions and message.chat.id != ADMIN_ID)
def forward_to_admin(message):
    """Пересылает сообщения от пользователя админу"""
    bot.send_message(ADMIN_ID, f"📩 Сообщение от {message.chat.id}:\n{message.text}")
    user_sessions[ADMIN_ID] = message.chat.id

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID)
def reply_from_admin(message):
    """Автоматически отвечает последнему пользователю"""
    if ADMIN_ID not in user_sessions:
        bot.send_message(ADMIN_ID, "⚠ Нет активных пользователей.")
        return

    user_id = user_sessions.get(ADMIN_ID)
    if user_id:
        bot.send_message(user_id, f"📩 Ответ от администратора:\n{message.text}")
    else:
        bot.send_message(ADMIN_ID, "⚠ Ошибка: пользователь не найден.")

if __name__ == '__main__':
    bot.polling(none_stop=True)