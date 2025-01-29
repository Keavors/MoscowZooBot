from telebot import types

def create_keyboard(options):
    """Создаёт клавиатуру с вариантами ответов."""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for option in options:
        markup.add(types.KeyboardButton(option))
    return markup

def restart_keyboard():
    """Создаёт клавиатуру для перезапуска викторины."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Попробовать ещё раз?"))
    return markup