from bot_instance import bot
from handlers import register_handlers

if __name__ == "__main__":
    register_handlers()
    bot.polling(none_stop=True)