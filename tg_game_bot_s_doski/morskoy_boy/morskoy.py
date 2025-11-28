import copy
import os

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# Создаем объекты бота и диспетчера
bot = Bot(token="7674634367:AAGsST4OHXRN5iRFOFWNCZcm3TzCH9bQylY")
dp = Dispatcher()

# Инициализируем константу размера игрового поля
FIELD_SIZE = 8

# Создаем словарь соответствий
LEXICON = {
    "/start": "Вот твоё поле. Можешь делать ход",
    0: " ",
    1: "🌊",
    2: "💥",
    "miss": "Мимо!",
    "hit": "Попал!",
    "used": "Вы уже стреляли сюда!",
    "next_move": "Делайте ваш следующий ход",
}

# Хардкодим расположение кораблей на игровом поле
ships = [
    [1, 0, 1, 1, 1, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 1, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0],
]

# Инициализируем "базу данных" пользователей
users: dict[int, dict[str, list]] = {}


# Создаём свой класс фабрики коллбэков, указывая префикс
# и структуру callback_data
class FieldCallbackFactory(CallbackData, prefix="user_field"):
    x: int
    y: int


# Функция, которая пересоздает новое поле для каждого игрока
def reset_field(user_id: int) -> None:
    users[user_id]["ships"] = copy.deepcopy(ships)
    users[user_id]["field"] = [
        [0 for _ in range(FIELD_SIZE)] for _ in range(FIELD_SIZE)
    ]


# Функция, генерирующая клавиатуру в зависимости от данных из
# матрицы ходов пользователя
def get_field_keyboard(user_id: int) -> InlineKeyboardMarkup:
    array_buttons: list[list[InlineKeyboardButton]] = []

    for i in range(FIELD_SIZE):
        array_buttons.append([])
        for j in range(FIELD_SIZE):
            array_buttons[i].append(
                InlineKeyboardButton(
                    text=LEXICON[users[user_id]["field"][i][j]],
                    callback_data=FieldCallbackFactory(x=i, y=j).pack(),
                )
            )

    return InlineKeyboardMarkup(inline_keyboard=array_buttons)


# Этот хэндлер будет срабатывать на команду /start, записывать
# пользователя в "базу данных", обнулять игровое поле и отправлять
# пользователю сообщение с клавиатурой
@dp.message(CommandStart())
async def process_start_command(message: Message):
    if message.from_user.id not in users:
        users[message.from_user.id] = {}
    reset_field(message.from_user.id)
    await message.answer(
        text=LEXICON["/start"],
        reply_markup=get_field_keyboard(message.from_user.id)
    )


# Этот хэндлер будет срабатывать на нажатие любой инлайн-кнопки на поле,
# запускать логику проверки результата нажатия и формирования ответа
@dp.callback_query(FieldCallbackFactory.filter())
async def process_category_press(
    callback: CallbackQuery, callback_data: FieldCallbackFactory
):
    field = users[callback.from_user.id]["field"]
    ships = users[callback.from_user.id]["ships"]
    if (
        field[callback_data.x][callback_data.y] == 0
        and ships[callback_data.x][callback_data.y] == 0
    ):
        answer = LEXICON["miss"]
        field[callback_data.x][callback_data.y] = 1
    elif (
        field[callback_data.x][callback_data.y] == 0
        and ships[callback_data.x][callback_data.y] == 1
    ):
        answer = LEXICON["hit"]
        field[callback_data.x][callback_data.y] = 2
    else:
        answer = LEXICON["used"]

    try:
        await callback.message.edit_text(
            text=LEXICON["next_move"],
            reply_markup=get_field_keyboard(callback.from_user.id),
        )
    except TelegramBadRequest:
        pass

    await callback.answer(answer)


if __name__ == "__main__":
    dp.run_polling(bot)