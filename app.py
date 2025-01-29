from telebot import TeleBot
from config import TOKEN
from handlers import start_handler, handle_answer, handle_callback

# Инициализация бота
bot = TeleBot(TOKEN)

# Регистрация обработчиков
@bot.message_handler(commands=["start"])
def start(message):
    start_handler(bot, message)

@bot.message_handler(func=lambda message: True)
def answer(message):
    handle_answer(bot, message)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    handle_callback(bot, call)

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)