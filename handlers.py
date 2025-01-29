from telebot import types
from data.animals import ANIMALS
from data.questions import QUESTIONS
from keyboards import create_keyboard, restart_keyboard
from utils import calculate_result, update_scores

# Словарь для хранения данных пользователей
user_data = {}

def start_handler(bot, message):
    """Обработчик команды /start."""
    user_id = message.chat.id
    user_data[user_id] = {"score": {animal: 0 for animal in ANIMALS}, "question_index": 0}

    bot.send_message(
        user_id,
        "Привет! Давайте узнаем, какое у вас тотемное животное в Московском зоопарке. Ответьте на несколько вопросов!",
    )
    ask_question(bot, user_id)

def ask_question(bot, user_id):
    """Задаёт пользователю следующий вопрос."""
    question_data = QUESTIONS[user_data[user_id]["question_index"]]
    markup = create_keyboard(question_data["options"])
    bot.send_message(user_id, question_data["question"], reply_markup=markup)

def handle_answer(bot, message):
    """Обрабатывает ответ пользователя."""
    user_id = message.chat.id
    if user_id not in user_data:
        bot.send_message(user_id, "Начните викторину с команды /start.")
        return

    question_index = user_data[user_id]["question_index"]
    if question_index >= len(QUESTIONS):
        bot.send_message(user_id, "Вы уже завершили викторину! Напишите /start, чтобы начать заново.")
        return

    # Обновляем баллы
    question_data = QUESTIONS[question_index]
    user_data[user_id]["score"] = update_scores(user_data[user_id]["score"], question_data["weights"])

    # Переход к следующему вопросу
    user_data[user_id]["question_index"] += 1
    if user_data[user_id]["question_index"] < len(QUESTIONS):
        ask_question(bot, user_id)
    else:
        show_result(bot, user_id)

def show_result(bot, user_id):
    """Показывает результат викторины."""
    result_animal = calculate_result(user_data[user_id]["score"])
    description = ANIMALS[result_animal]["description"]
    image_url = ANIMALS[result_animal]["image"]

    bot.send_photo(user_id, image_url, caption=f"Ваше тотемное животное — {result_animal}!\n{description}")

    # Кнопка для перезапуска
    bot.send_message(user_id, "Хотите пройти викторину ещё раз?", reply_markup=restart_keyboard())

    # Рассказываем о программе опеки
    bot.send_message(
        user_id,
        "Хотите узнать больше о программе опеки? Переходите по ссылке: https://moscowzoo.ru/about/guardianship",
    )

def restart_handler(bot, message):
    """Обработчик перезапуска викторины."""
    start_handler(bot, message)