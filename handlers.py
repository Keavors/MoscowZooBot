from telebot import types
import logging

from app import bot
from data.animals import ANIMALS
from data.questions import QUESTIONS
from keyboards import create_keyboard, restart_keyboard, share_keyboard, contact_keyboard, feedback_keyboard
from utils import calculate_result, update_scores

# Настройка логирования
logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Словарь для хранения данных пользователей
user_data = {}


def start_handler(bot, message):
    """Обработчик команды /start с логированием и обработкой ошибок"""
    try:
        user_id = message.chat.id
        user_data[user_id] = {
            "score": {animal: 0 for animal in ANIMALS},
            "question_index": 0,
            "feedback": None
        }

        bot.send_message(
            user_id,
            "🐾 Привет! Я помогу тебе найти твоё тотемное животное Московского зоопарка!\n"
            "Ответь на 10 вопросов, и я подберу тебе идеального питомца-опекуна!\n\n"
            "Начнём? Жми на кнопки ответов! 🦁"
        )
        ask_question(bot, user_id)
        logging.info(f"User {user_id} started quiz")

    except Exception as e:
        logging.error(f"Error in start_handler: {e}", exc_info=True)
        bot.send_message(message.chat.id, "⚠️ Что-то пошло не так. Попробуйте позже.")


def ask_question(bot, user_id):
    """Задаёт следующий вопрос с проверкой прогресса"""
    try:
        if user_data[user_id]["question_index"] >= len(QUESTIONS):
            show_result(bot, user_id)
            return

        question_data = QUESTIONS[user_data[user_id]["question_index"]]
        progress = f"Вопрос {user_data[user_id]['question_index'] + 1}/{len(QUESTIONS)}"

        msg = bot.send_message(
            user_id,
            f"📌 {progress}\n{question_data['question']}",
            reply_markup=create_keyboard(question_data["options"])
        )
        bot.register_next_step_handler(msg, lambda m: handle_answer(bot, m))

    except Exception as e:
        logging.error(f"Error asking question: {e}", exc_info=True)
        bot.send_message(user_id, "⚠️ Ошибка загрузки вопроса. Попробуйте /start")


def handle_answer(bot, message):
    """Обработка ответов с валидацией и подсчётом баллов"""
    try:
        user_id = message.chat.id

        if user_id not in user_data:
            bot.send_message(user_id, "🌀 Начни викторину заново: /start")
            return

        # Проверка валидности ответа
        current_question = QUESTIONS[user_data[user_id]["question_index"]]
        if message.text not in current_question["options"]:
            bot.send_message(user_id, "🚫 Пожалуйста, выбери вариант из предложенных кнопок!")
            ask_question(bot, user_id)
            return

        # Обновление баллов
        user_data[user_id]["score"] = update_scores(
            user_data[user_id]["score"],
            current_question["weights"]
        )

        user_data[user_id]["question_index"] += 1
        ask_question(bot, user_id)

    except Exception as e:
        logging.error(f"Error handling answer: {e}", exc_info=True)
        bot.send_message(message.chat.id, "⚠️ Ошибка обработки ответа. Попробуйте /start")


def show_result(bot, user_id):
    """Показ результата с дополнительными опциями"""
    try:
        result_animal = calculate_result(user_data[user_id]["score"])
        animal_data = ANIMALS[result_animal]

        # Формирование описания
        description = (
            f"🎉 Твоё тотемное животное — *{result_animal}*!\n\n"
            f"{animal_data['description']}\n\n"
            f"🐾 Хочешь взять под опеку этого красавца? "
            f"Переходи на [сайт программы]({animal_data['opeka_link']})!"
        )

        # Отправка результата
        bot.send_photo(
            user_id,
            animal_data['image'],
            caption=description,
            parse_mode='Markdown',
            reply_markup=types.ReplyKeyboardRemove()
        )

        # Панель действий после викторины
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("🔄 Пройти ещё раз", callback_data="restart"),
            types.InlineKeyboardButton("📤 Поделиться", callback_data="share")
        )
        markup.row(
            types.InlineKeyboardButton("📝 Оставить отзыв", callback_data="feedback"),
            types.InlineKeyboardButton("📞 Связаться с куратором", callback_data="contact")
        )

        bot.send_message(
            user_id,
            "👇 Что ты хочешь сделать дальше?",
            reply_markup=markup
        )

        # Очистка данных пользователя (кроме отзыва)
        del user_data[user_id]['score']
        del user_data[user_id]['question_index']

    except Exception as e:
        logging.error(f"Error showing result: {e}", exc_info=True)
        bot.send_message(user_id, "⚠️ Ошибка показа результата. Попробуйте /start")


def handle_callback(bot, call):
    """Обработчик inline-кнопок"""
    try:
        user_id = call.message.chat.id

        if call.data == "restart":
            start_handler(bot, call.message)

        elif call.data == "share":
            result_animal = calculate_result(user_data.get(user_id, {}).get("score", {}))
            share_text = (
                f"Моё тотемное животное Московского зоопарка — {result_animal}! 🐯\n"
                f"Пройди викторину и узнай своё: https://t.me/your_bot_name"
            )
            bot.send_message(
                user_id,
                f"📲 Вот твоя ссылка для分享:\n\n{share_text}",
                reply_markup=types.ReplyKeyboardRemove()
            )

        elif call.data == "feedback":
            msg = bot.send_message(user_id, "📝 Напиши свой отзыв или предложение:")
            bot.register_next_step_handler(msg, save_feedback)

        elif call.data == "contact":
            result_animal = calculate_result(user_data.get(user_id, {}).get("score", {}))
            contact_info = (
                "📩 Для связи с куратором программы опеки:\n\n"
                f"*Результат вашей викторины:* {result_animal}\n"
                "✉️ Email: opeka@moscowzoo.ru\n"
                "📞 Телефон: +7 (495) 777-77-77\n\n"
                "Мы свяжемся с вами в течение 2 рабочих дней!"
            )
            bot.send_message(
                user_id,
                contact_info,
                parse_mode='Markdown'
            )

    except Exception as e:
        logging.error(f"Callback error: {e}", exc_info=True)
        bot.send_message(user_id, "⚠️ Произошла ошибка. Попробуйте позже.")


def save_feedback(message):
    """Сохранение отзыва с модерацией"""
    try:
        user_id = message.chat.id
        feedback = message.text

        if len(feedback) < 10:
            bot.send_message(user_id, "❌ Слишком короткий отзыв. Напиши хотя бы 10 символов.")
            return

        # Здесь можно добавить сохранение в БД или отправку на почту
        user_data[user_id]["feedback"] = feedback
        bot.send_message(
            user_id,
            "✅ Спасибо за отзыв! Мы обязательно его учтём!\n"
            "Если ты оставил контактные данные, с тобой могут связаться."
        )
        logging.info(f"Feedback from {user_id}: {feedback[:50]}...")

    except Exception as e:
        logging.error(f"Feedback error: {e}", exc_info=True)
        bot.send_message(user_id, "⚠️ Ошибка сохранения отзыва. Попробуйте позже.")


def error_handler(bot, message):
    """Глобальный обработчик ошибок"""
    logging.error(f"Unhandled exception: {message}")
    bot.send_message(
        message.chat.id,
        "🔧 Произошла непредвиденная ошибка. Мы уже работаем над исправлением!\n"
        "Попробуйте начать заново: /start"
    )