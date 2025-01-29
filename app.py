from telebot import TeleBot
from config import TOKEN
from handlers import start_handler, handle_answer, restart_handler

# Инициализация бота
bot = TeleBot(TOKEN)

# Регистрация обработчиков
@bot.message_handler(commands=["start"])
def start(message):
    start_handler(bot, message)

@bot.message_handler(func=lambda message: True)
def answer(message):
    handle_answer(bot, message)

@bot.message_handler(func=lambda message: message.text == "Попробовать ещё раз?")
def restart(message):
    restart_handler(bot, message)

# Запуск бота
if __name__ == "__main__":
    bot.polling()