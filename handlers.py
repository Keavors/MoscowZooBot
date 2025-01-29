from telebot import types
from bot_instance import bot
from data.animals import ANIMALS
from data.questions import QUESTIONS
from keyboards import create_keyboard
from utils import calculate_result, update_scores
import logging

# Настройка логирования
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

user_data = {}


def register_handlers():
    """Регистрация обработчиков с приоритетом"""
    bot.message_handler(commands=['start'])(start_handler)
    bot.message_handler(func=lambda msg: is_user_in_quiz(msg))(process_answer)
    bot.callback_query_handler(func=lambda call: True)(handle_callback)
    bot.message_handler(func=lambda msg: True)(fallback_handler)


def is_user_in_quiz(message) -> bool:
    """Проверяет, активна ли викторина у пользователя"""
    user_id = message.chat.id
    return (
            user_id in user_data and
            user_data[user_id].get("question_index", 0) < len(QUESTIONS)
    )


def fallback_handler(message):
    """Обработчик всех сообщений, которые не попали в другие обработчики"""
    user_id = message.chat.id
    try:
        if user_id in user_data and "result_animal" in user_data[user_id]:
            # После завершения викторины
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton("🔄 Пройти снова", callback_data="restart"),
                types.InlineKeyboardButton("📞 Контакты", callback_data="contact")
            )
            bot.send_message(
                user_id,
                "🌀 Викторина завершена. Выберите действие:",
                reply_markup=markup
            )
        else:
            # До начала викторины
            bot.send_message(user_id, "ℹ️ Начните викторину: /start")
    except Exception as e:
        logging.error(f"Fallback error: {e}")
        bot.send_message(user_id, "⚠️ Неизвестная команда. Используйте /start")


def start_handler(message):
    """Обработчик команды /start"""
    try:
        user_id = message.chat.id
        user_data[user_id] = {
            "score": {animal: 0 for animal in ANIMALS},
            "question_index": 0,  # Обязательный ключ
            "excluded_animals": set(),
            "feedback": None,
            "result_animal": None
        }

        bot.send_message(
            user_id,
            "🐾 Добро пожаловать в викторину Московского зоопарка!\n"
            "Ответьте на 10 вопросов, чтобы узнать ваше тотемное животное.\n\n"
            "Начнём? Выбирайте варианты ответов! 🦁"
        )
        ask_question(user_id)
        logging.info(f"User {user_id} started quiz")

    except Exception as e:
        logging.error(f"Start error: {e}", exc_info=True)
        bot.send_message(message.chat.id, "⚠️ Произошла ошибка. Попробуйте /start")


def ask_question(user_id):
    """Задаёт следующий вопрос"""
    try:
        if user_data[user_id]["question_index"] >= len(QUESTIONS):
            show_result(user_id)
            return

        question_index = user_data[user_id]["question_index"]
        question_data = QUESTIONS[question_index]

        # Создаем клавиатуру с вариантами ответов
        markup = create_keyboard([option["text"] for option in question_data["options"]])
        progress = f"Вопрос {question_index + 1}/{len(QUESTIONS)}"

        bot.send_message(
            user_id,
            f"📌 {progress}\n{question_data['question']}",
            reply_markup=markup
        )

    except Exception as e:
        logging.error(f"Ask question error: {e}", exc_info=True)
        bot.send_message(user_id, "⚠️ Ошибка загрузки вопроса. Попробуйте /start")


def process_answer(message):
    """Обработка ответа пользователя"""
    user_id = message.chat.id
    try:
        # Проверяем, зарегистрирован ли пользователь и есть ли данные
        if user_id not in user_data:
            bot.send_message(user_id, "🌀 Пожалуйста, начните викторину: /start")
            return

        # Проверяем наличие ключа 'question_index'
        user_session = user_data[user_id]
        if "question_index" not in user_session:
            bot.send_message(user_id, "⚠️ Сессия повреждена. Начните заново: /start")
            return

        current_index = user_session["question_index"]

        # Проверяем, не завершена ли викторина
        if current_index >= len(QUESTIONS):
            show_result(user_id)
            return

        # Получаем текущий вопрос
        current_question = QUESTIONS[current_index]

        # Нормализация ответа
        user_answer = message.text.strip().lower()
        options = {
            opt["text"].strip().lower(): opt
            for opt in current_question["options"]
        }

        if user_answer not in options:
            error_msg = (
                "🚫 Используйте кнопки для ответа:\n"
                f"{', '.join([opt['text'] for opt in current_question['options']])}"
            )
            bot.send_message(user_id, error_msg)
            return ask_question(user_id)

        # Обновляем данные
        selected_option = options[user_answer]
        user_session["excluded_animals"].update(selected_option["excludes"])
        user_session["score"] = update_scores(user_session["score"], selected_option["weights"])
        user_session["question_index"] += 1

        ask_question(user_id)

    except KeyError as e:
        logging.error(f"KeyError: {e} в процессе ответа пользователя {user_id}")
        bot.send_message(user_id, "⚠️ Ошибка данных. Пожалуйста, начните заново: /start")
    except Exception as e:
        logging.error(f"Ошибка в process_answer: {e}", exc_info=True)
        bot.send_message(user_id, "🌀 Произошла непредвиденная ошибка. Попробуйте /start")


def show_result(user_id):
    """Показывает итоговый результат"""
    try:
        total_score = sum(user_data[user_id]["score"].values())
        excluded = user_data[user_id]["excluded_animals"]
        result_animal = calculate_result(total_score, excluded)
        user_data[user_id]["result_animal"] = result_animal  # Сохраняем для шаринга
        animal_data = ANIMALS[result_animal]

        caption = (
            f"🎉 Ваше тотемное животное — *{result_animal}*!\n\n"
            f"{animal_data['description']}\n\n"
            f"🐾 Узнать о программе опеки: [ссылка]({animal_data['opeka_link']})"
        )

        bot.send_photo(
            user_id,
            animal_data['image'],
            caption=caption,
            parse_mode='Markdown',
            reply_markup=types.ReplyKeyboardRemove()
        )

        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("🔄 Пройти снова", callback_data="restart"),
            types.InlineKeyboardButton("📤 Поделиться", callback_data="share")
        )
        markup.row(
            types.InlineKeyboardButton("📝 Оставить отзыв", callback_data="feedback"),
            types.InlineKeyboardButton("📞 Контакты", callback_data="contact")
        )

        bot.send_message(user_id, "👇 Выберите дальнейшее действие:", reply_markup=markup)

        # Очистка временных данных (кроме result_animal для шаринга)
        keys_to_delete = ['score', 'question_index', 'excluded_animals']
        for key in keys_to_delete:
            user_data[user_id].pop(key, None)

    except Exception as e:
        logging.error(f"Result error: {e}", exc_info=True)
        bot.send_message(user_id, "⚠️ Ошибка показа результата. Попробуйте /start")


def handle_callback(call):
    """Обработчик inline-кнопок"""
    try:
        user_id = call.message.chat.id
        data = call.data

        if data == "restart":
            user_data.pop(user_id, None)  # Полная очистка данных
            start_handler(call.message)

        elif data == "share":
            animal = user_data.get(user_id, {}).get("result_animal", "животное")
            share_text = (
                f"Моё тотемное животное Московского зоопарка — {animal}! 🦁\n"
                "Пройди викторину и узнай своё: @MoscowZooBot"
            )
            bot.send_message(user_id, f"📩 Для публикации:\n\n{share_text}")

        elif data == "feedback":
            msg = bot.send_message(user_id, "✍️ Напишите ваш отзыв или предложение:")
            bot.register_next_step_handler(msg, save_feedback)

        elif data == "contact":
            animal = user_data.get(user_id, {}).get("result_animal", "неизвестное животное")
            contact_msg = (
                "📬 Контакты для опеки:\n\n"
                f"Ваше животное: {animal}\n"
                "Email: opeka@moscowzoo.ru\n"
                "Телефон: +7 (495) 777-77-77"
            )
            bot.send_message(user_id, contact_msg)

    except Exception as e:
        logging.error(f"Callback error: {e}", exc_info=True)
        bot.send_message(call.message.chat.id, "⚠️ Ошибка. Попробуйте ещё раз.")


def save_feedback(message):
    """Сохранение отзыва"""
    try:
        user_id = message.chat.id
        feedback = message.text.strip()

        if len(feedback) < 10:
            bot.send_message(user_id, "❌ Отзыв должен содержать минимум 10 символов")
            return

        if user_id in user_data:
            user_data[user_id]["feedback"] = feedback

        bot.send_message(user_id, "✅ Благодарим за обратную связь!")
        logging.info(f"Feedback from {user_id}: {feedback[:100]}")


    except Exception as e:
        logging.error(f"Feedback error: {e}")
        bot.send_message(message.chat.id, "⚠️ Не удалось сохранить отзыв.")


def fallback_handler(message):
    """Обработчик неподдерживаемых сообщений"""
    user_id = message.chat.id
    if message.text.startswith('/'):
        bot.send_message(user_id, "⚠️ Неизвестная команда. Для начала викторины отправьте /start")
    else:
        print(1)
        bot.send_message(user_id, "ℹ️ Пожалуйста, используйте кнопки для ответов")
