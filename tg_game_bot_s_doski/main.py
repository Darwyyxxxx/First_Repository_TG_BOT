import telebot
from telebot import types
import random

from config import config
from handlers import knb_game, dice_game
from utils import spam_handler

# Инициализация бота
bot = telebot.TeleBot(config.BOT_TOKEN)

# Словарь для хранения состояния пользователя (какую игру он сейчас играет)
# chat_id -> 'main_menu', 'knb', 'dice'
user_game_state = {}

# --- Вспомогательные функции для клавиатур ---

def create_main_menu_keyboard():
    """Создает клавиатуру главного меню."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add("Камень, ножницы, бумага ✊✌️✋")
    keyboard.add("Кубик 🎲")
    keyboard.add("Книгочиталка📚")
    return keyboard

def send_main_menu(chat_id):
    """Отправляет главное меню."""
    bot.send_message(chat_id, "Выберите игру:", reply_markup=create_main_menu_keyboard())
    user_game_state[chat_id] = 'main_menu'

# --- Обработчики команд ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Обработчик команды /start и /help."""
    chat_id = message.chat.id
    bot.send_message(chat_id, "Привет! Я бот с играми и книгой. Выбери что тебе интересно:")
    send_main_menu(chat_id)

# --- Обработчики переходов по кнопкам ---

@bot.message_handler(func=lambda message: message.text == "⬅️ Назад в меню")
def go_back_to_main_menu(message):
    """Обработчик кнопки 'Назад в меню'."""
    send_main_menu(message.chat.id)

@bot.message_handler(func=lambda message: message.text == "Камень, ножницы, бумага ✊✌️✋")
def select_knb_game(message):
    """Выбор игры Камень, ножницы, бумага."""
    knb_game.start_knb_game(bot, message)
    user_game_state[message.chat.id] = 'knb'

@bot.message_handler(func=lambda message: message.text == "Кубик 🎲")
def select_dice_game(message):
    """Выбор игры Кубик."""
    dice_game.start_dice_game(bot, message)
    user_game_state[message.chat.id] = 'dice'


# --- Основной обработчик сообщений (диспетчеризация) ---

@bot.message_handler(content_types=['text'])
def handle_text_messages(message):
    chat_id = message.chat.id
    user_text = message.text

    current_state = user_game_state.get(chat_id, 'main_menu') # Получаем текущее состояние или 'main_menu' по умолчанию

    if current_state == 'knb':
        if user_text in knb_game.KNB_CHOICES:
            knb_game.handle_knb_choice(bot, message)
        else:
            # Неверный ввод в игре КНБ
            spam_handler.send_invalid_input_response(bot, chat_id)
            bot.send_message(chat_id, "Пожалуйста, выберите 'Камень', 'Ножницы' или 'Бумага' с клавиатуры.", parse_mode='HTML')
    elif current_state == 'dice':
        if user_text == "Бросить кубик 🎲":
            dice_game.handle_dice_roll(bot, message)
        else:
            # Неверный ввод в игре Кубик
            spam_handler.send_invalid_input_response(bot, chat_id)
            bot.send_message(chat_id, "Пожалуйста, нажмите 'Бросить кубик'.")

    elif current_state == 'main_menu':
        # Неверный ввод в главном меню
        spam_handler.send_invalid_input_response(bot, chat_id)
        bot.send_message(chat_id, "Пожалуйста, выберите игру с клавиатуры.")
    else:
        # Неизвестное состояние (очень редко)
        spam_handler.send_invalid_input_response(bot, chat_id)
        send_main_menu(chat_id)


# --- Запуск бота ---
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()