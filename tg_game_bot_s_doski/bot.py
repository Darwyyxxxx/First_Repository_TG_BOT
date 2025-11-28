# bot.py
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from config import TOKEN

# --- Логирование ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------- Главное меню ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Камень, ножницы, бумага", callback_data="rps")],
        [InlineKeyboardButton("🎲 Бросить кубик", callback_data="dice")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # обязательно await
    await update.message.reply_text("Выбери игру:", reply_markup=reply_markup)


# ---------- Обработка кнопок ----------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    # обязательно подтвердить callback сразу
    try:
        await query.answer()
    except Exception as e:
        # логируем, но продолжаем — иногда answer уже был отправлен
        logger.exception("Ошибка при query.answer(): %s", e)

    try:
        data = query.data  # безопасно взять в переменную
        logger.info("Callback data: %s from user %s", data, query.from_user.id)

        if data == "rps":
            keyboard = [
                [
                    InlineKeyboardButton("🪨 Камень", callback_data="rock"),
                    InlineKeyboardButton("✂️ Ножницы", callback_data="scissors"),
                    InlineKeyboardButton("📄 Бумага", callback_data="paper"),
                ],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back")],
            ]
            await query.edit_message_text("Выбери вариант:", reply_markup=InlineKeyboardMarkup(keyboard))

        elif data in ["rock", "scissors", "paper"]:
            choices = {"rock": "🪨 Камень", "scissors": "✂️ Ножницы", "paper": "📄 Бумага"}
            bot_choice = random.choice(list(choices.keys()))
            user_choice = data

            if user_choice == bot_choice:
                result = "Ничья!"
            elif (user_choice == "rock" and bot_choice == "scissors") or \
                 (user_choice == "scissors" and bot_choice == "paper") or \
                 (user_choice == "paper" and bot_choice == "rock"):
                result = "Ты выиграл!"
            else:
                result = "Ты проиграл!"

            await query.edit_message_text(
                f"Ты выбрал {choices[user_choice]}\nБот выбрал {choices[bot_choice]}\n\n{result}"
            )

        elif data == "dice":
            number = random.randint(1, 6)
            keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]
            await query.edit_message_text(
                f"🎲 Выпало число: {number}",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

        elif data == "back":
            keyboard = [
                [InlineKeyboardButton("🎮 Камень, ножницы, бумага", callback_data="rps")],
                [InlineKeyboardButton("🎲 Бросить кубик", callback_data="dice")],
            ]
            await query.edit_message_text("Выбери игру:", reply_markup=InlineKeyboardMarkup(keyboard))

        else:
            # на всякий случай — если пришли неожиданные данные
            logger.warning("Неизвестный callback_data: %s", data)
            await query.edit_message_text("Неизвестная команда. Вернись в меню /start")

    except Exception as ex:
        # логируем исключение, чтобы не оставлять кнопку "висеть"
        logger.exception("Ошибка при обработке callback: %s", ex)
        # пробуем уведомить пользователя текстом (не редактируем, т.к. может быть ошибка)
        try:
            await query.message.reply_text("Произошла ошибка — посмотри консоль бота.")
        except Exception:
            pass


# ---------- Обработка неверных сообщений (без GIF) ----------