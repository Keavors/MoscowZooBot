from bot_instance import bot
from handlers import register_handlers

if __name__ == "__main__":
    register_handlers()  # Явная регистрация обработчиков
    bot.polling(none_stop=True)