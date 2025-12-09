import telebot
import random

# ID чата -> текущий статус игры
dice_states = {}

def create_dice_keyboard():
    """Создает клавиатуру для игры Кубик."""
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add("Бросить кубик 🎲")
    keyboard.add("⬅️ Назад в меню")
    return keyboard

def start_dice_game(bot_instance: telebot.TeleBot, message: telebot.types.Message):
    """Начинает игру Кубик."""
    chat_id = message.chat.id
    dice_states[chat_id] = 'playing'
    bot_instance.send_message(chat_id, "<b>Вы выбрали Кубик! Нажмите 'Бросить кубик', чтобы узнать число.</b>", reply_markup=create_dice_keyboard(),parse_mode='HTML')

def handle_dice_roll(bot_instance: telebot.TeleBot, message: telebot.types.Message):
    """Обрабатывает бросок кубика."""
    chat_id = message.chat.id

    if chat_id not in dice_states or dice_states[chat_id] != 'playing':
        bot_instance.send_message(chat_id, "<b>Кажется, игра не активна. Начните сначала.</b>", parse_mode='HTML')
        return

    roll = random.randint(1, 6)
    bot_instance.send_message(chat_id, f"<b>Выпало: {roll} 🎲</b>", parse_mode='HTML')
    # Кнопки остаются, так что можно бросать еще