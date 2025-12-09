import telebot
import random

# Варианты выбора для КНБ
KNB_CHOICES = ['Камень ✊', 'Ножницы ✌️', 'Бумага ✋']

# ID чата -> текущий статус игры (нужно для main.py)
knb_states = {}

def create_knb_keyboard():
    """Создает клавиатуру для игры Камень, ножницы, бумага."""
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(*KNB_CHOICES)
    keyboard.add("⬅️ Назад в меню")
    return keyboard

def start_knb_game(bot_instance: telebot.TeleBot, message: telebot.types.Message):
    """Начинает игру Камень, ножницы, бумага."""
    chat_id = message.chat.id
    knb_states[chat_id] = 'playing'
    bot_instance.send_message(chat_id, "<u>Вы выбрали Камень, ножницы, бумага! Сделайте свой выбор:</u>", reply_markup=create_knb_keyboard(), parse_mode='HTML')

def handle_knb_choice(bot_instance: telebot.TeleBot, message: telebot.types.Message):
    """Обрабатывает выбор пользователя в игре Камень, ножницы, бумага."""
    chat_id = message.chat.id
    user_choice = message.text

    if chat_id not in knb_states or knb_states[chat_id] != 'playing':
        # Этого не должно произойти, если main.py правильно управляет состоянием,
        # но для подстраховки.
        bot_instance.send_message(chat_id, "<u>Кажется, игра не активна. Начните сначала.</u>", parse_mode='HTML')
        return

    bot_choice = random.choice(KNB_CHOICES)

    result_message = f"<u>Твой выбор: {user_choice}\nМой выбор: {bot_choice}\n</u>"

    if user_choice == bot_choice:
        result_message += "<u>Ничья! 🤝</u>"
    elif (user_choice == 'Камень ✊' and bot_choice == 'Ножницы ✌️') or \
         (user_choice == 'Ножницы ✌️' and bot_choice == 'Бумага ✋') or \
         (user_choice == 'Бумага ✋' and bot_choice == 'Камень ✊'):
        result_message += "<u>Ты победил! 🎉</u>"
    else:
        result_message += "<u>Я победил! 🤖</u>"

    bot_instance.send_message(chat_id, result_message,parse_mode='HTML')
    # Можно предложить сыграть еще раз или вернуться в меню, но кнопки уже есть