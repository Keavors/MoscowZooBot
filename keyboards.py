from telebot import types

def create_keyboard(options: list) -> types.ReplyKeyboardMarkup:
    """Создаёт reply-клавиатуру с вариантами ответов"""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for option in options:
        btn = types.KeyboardButton(option)
        markup.add(btn)
    return markup

def restart_keyboard() -> types.ReplyKeyboardMarkup:
    """Клавиатура для перезапуска викторины"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Попробовать ещё раз?"))
    return markup

def actions_keyboard() -> types.InlineKeyboardMarkup:
    """Инлайн-клавиатура с пост-викторинными действиями"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔄 Пройти ещё раз", callback_data="restart"),
        types.InlineKeyboardButton("📤 Поделиться", callback_data="share"),
        types.InlineKeyboardButton("📝 Отзыв", callback_data="feedback"),
        types.InlineKeyboardButton("📞 Контакты", callback_data="contact")
    )
    return markup

def share_keyboard(result_animal: str) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    share_text = f"Моё тотемное животное — {result_animal}! Пройди викторину: https://t.me/MoscowZooBot"  # Актуальная ссылка
    markup.add(
        types.InlineKeyboardButton("📱 Telegram", url=f"https://t.me/share/url?text={share_text}"),
        types.InlineKeyboardButton("📧 Email", callback_data="share_email")
    )
    return markup

def contact_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✉️ Написать письмо", url="mailto:opeka@moscowzoo.ru"),  # Исправленный email
        types.InlineKeyboardButton("📞 Позвонить", callback_data="call_curator")
    )
    return markup

def feedback_keyboard() -> types.InlineKeyboardMarkup:
    """Клавиатура для сбора отзывов"""
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("⭐️ Оценить бота", url="https://forms.gle/example"),
        types.InlineKeyboardButton("✍️ Текстовый отзыв", callback_data="text_feedback")
    )
    return markup