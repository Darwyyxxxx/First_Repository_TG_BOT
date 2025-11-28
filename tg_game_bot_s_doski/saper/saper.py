import copy
import os
import random

from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# --- Настройки бота и поля ---
# Рекомендуется использовать переменные окружения или config.py для токена
# bot = Bot(token=os.getenv("BOT_TOKEN"))
bot = Bot(token="8450809023:AAHqJRmqcyQ43sl6awh6iNTJQ9NAOxLkTSU") # <-- ЗАМЕНИТЕ НА СВОЙ ТОКЕН!
dp = Dispatcher()

# Инициализируем константы размера игрового поля и количества мин
FIELD_SIZE = 8
NUM_MINES = 10 # Количество мин на поле

# Создаем словарь соответствий для отображения клеток
LEXICON = {
    "/start": "Добро пожаловать в Сапер! Выберите режим и сделайте ход.",
    "mine_lose": "💣", # Мина, проигрыш
    "mine_win": "🚩", # Мина (для отображения флажка)
    "closed": "⬜", # Закрытая клетка
    "flag": "🚩", # Флажок
    "mode_click": "Клик",
    "mode_flag": "Флаг",
    "switch_mode": "Переключить режим",
    "lose": "💥 БУМ! Вы проиграли!",
    "win": "🎉 Поздравляем! Вы выиграли!",
    "already_opened": "Эта клетка уже открыта!",
    "game_over": "Игра окончена. Начните новую игру командой /start.",
    "choose_action": "Выберите действие:",
}

# Добавляем числа для отображения количества мин вокруг
for i in range(9): # От 0 до 8 мин
    if i == 0:
        LEXICON[i] = " " # Пустая клетка, если 0 мин вокруг
    else:
        LEXICON[i] = str(i) # Числа 1-8

# Инициализируем "базу данных" пользователей
# users[user_id] = {
#   "game_over": bool,
#   "game_mode": "click" | "flag",
#   "field_mines": list[list[int]], # Расположение мин и числа мин вокруг (-1 = мина)
#   "field_user": list[list[int]],  # Что видит пользователь (0=закрыто, 1=открыто, 2=флаг)
# }
users: dict[int, dict] = {}


# --- Фабрики коллбэков ---
class FieldCallbackFactory(CallbackData, prefix="sapper_field"):
    x: int
    y: int

class ModeCallbackFactory(CallbackData, prefix="sapper_mode"):
    action: str # 'switch'

# --- Вспомогательные функции для логики Сапера ---

# Функция для генерации поля с минами и числами
def generate_field(size: int, num_mines: int) -> list[list[int]]:
    field = [[0 for _ in range(size)] for _ in range(size)]
    mines_placed = 0

    # Размещаем мины
    while mines_placed < num_mines:
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        if field[x][y] != -1: # -1 означает мину
            field[x][y] = -1
            mines_placed += 1

    # Заполняем числа
    for i in range(size):
        for j in range(size):
            if field[i][j] == -1:
                continue

            mine_count = 0
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = i + dx, j + dy
                    if 0 <= nx < size and 0 <= ny < size and field[nx][ny] == -1:
                        mine_count += 1
            field[i][j] = mine_count
    return field

# Функция рекурсивного открытия пустых клеток (flood fill)
def open_empty_cells(user_id: int, x: int, y: int) -> None:
    field_mines = users[user_id]["field_mines"]
    field_user = users[user_id]["field_user"]
    size = FIELD_SIZE

    if not (0 <= x < size and 0 <= y < size):
        return # Выход за границы поля

    if field_user[x][y] != 0: # Уже открыта или флаг
        return

    field_user[x][y] = 1 # Открываем клетку

    if field_mines[x][y] == 0: # Если 0 мин вокруг, открываем соседей
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                open_empty_cells(user_id, x + dx, y + dy)


# Проверка на победу
def check_win(user_id: int) -> bool:
    field_mines = users[user_id]["field_mines"]
    field_user = users[user_id]["field_user"]
    size = FIELD_SIZE

    for i in range(size):
        for j in range(size):
            # Если минная клетка не помечена флагом, или не-минная клетка не открыта
            if (field_mines[i][j] == -1 and field_user[i][j] != 2) or \
               (field_mines[i][j] != -1 and field_user[i][j] == 0):
                return False
    return True

# --- Игровой процесс ---

# Функция, которая пересоздает новое поле для каждого игрока
def reset_game(user_id: int) -> None:
    users[user_id]["game_over"] = False
    users[user_id]["game_mode"] = "click" # Режим по умолчанию
    users[user_id]["field_mines"] = generate_field(FIELD_SIZE, NUM_MINES)
    users[user_id]["field_user"] = [
        [0 for _ in range(FIELD_SIZE)] for _ in range(FIELD_SIZE) # 0 = закрыто, 1 = открыто, 2 = флаг
    ]


# Функция, генерирующая клавиатуру
def get_sapper_keyboard(user_id: int) -> InlineKeyboardMarkup:
    array_buttons: list[list[InlineKeyboardButton]] = []
    field_user = users[user_id]["field_user"]
    field_mines = users[user_id]["field_mines"] # Для отображения мин при проигрыше
    game_over = users[user_id]["game_over"]

    for i in range(FIELD_SIZE):
        array_buttons.append([])
        for j in range(FIELD_SIZE):
            cell_text = LEXICON["closed"] # По умолчанию - закрытая клетка
            if game_over:
                if field_mines[i][j] == -1:
                    cell_text = LEXICON["mine_lose"] # Показываем мины при проигрыше
                elif field_user[i][j] == 1: # Открытая (не мина)
                     cell_text = LEXICON[field_mines[i][j]]
                else: # Закрытые не мины при проигрыше
                     cell_text = LEXICON["closed"]
            elif field_user[i][j] == 1: # Клетка открыта
                cell_text = LEXICON[field_mines[i][j]]
            elif field_user[i][j] == 2: # Флажок
                cell_text = LEXICON["flag"]

            array_buttons[i].append(
                InlineKeyboardButton(
                    text=cell_text,
                    callback_data=FieldCallbackFactory(x=i, y=j).pack(),
                )
            )

    # Добавляем кнопку переключения режима
    current_mode = users[user_id]["game_mode"]
    mode_text = f"{LEXICON['switch_mode']}: {LEXICON[f'mode_{current_mode}']}"
    array_buttons.append([
        InlineKeyboardButton(
            text=mode_text,
            callback_data=ModeCallbackFactory(action="switch").pack(),
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=array_buttons)


# --- Хэндлеры ---

# Хэндлер на команду /start
@dp.message(CommandStart())
async def process_start_command(message: Message):
    if message.from_user.id not in users:
        users[message.from_user.id] = {}
    reset_game(message.from_user.id)
    await message.answer(
        text=LEXICON["/start"],
        reply_markup=get_sapper_keyboard(message.from_user.id)
    )

# Хэндлер на переключение режима (Клик / Флаг)
@dp.callback_query(ModeCallbackFactory.filter(F.action == "switch"))
async def process_switch_mode(callback: CallbackQuery):
    if users[callback.from_user.id]["game_over"]:
        await callback.answer(LEXICON["game_over"], show_alert=True)
        return

    current_mode = users[callback.from_user.id]["game_mode"]
    users[callback.from_user.id]["game_mode"] = "flag" if current_mode == "click" else "click"

    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_sapper_keyboard(callback.from_user.id)
        )
    except TelegramBadRequest:
        pass # Игнорируем, если изменений в клавиатуре нет

    current_mode_key = users[callback.from_user.id]["game_mode"] # Получаем 'click' или 'flag'
    await callback.answer(f"Режим изменен на '{LEXICON[f'mode_{current_mode_key}']}'") # Используем переменную


# Хэндлер на нажатие инлайн-кнопки поля
@dp.callback_query(FieldCallbackFactory.filter())
async def process_field_press(
    callback: CallbackQuery, callback_data: FieldCallbackFactory
):
    user_id = callback.from_user.id
    if users[user_id]["game_over"]:
        await callback.answer(LEXICON["game_over"], show_alert=True)
        return

    x, y = callback_data.x, callback_data.y
    field_mines = users[user_id]["field_mines"]
    field_user = users[user_id]["field_user"]
    game_mode = users[user_id]["game_mode"]

    answer_text = ""
    game_just_ended = False

    if game_mode == "click":
        if field_user[x][y] == 1: # Уже открыта
            answer_text = LEXICON["already_opened"]
        elif field_user[x][y] == 2: # Стоит флажок, не кликаем
            answer_text = "Сначала снимите флажок!"
        elif field_mines[x][y] == -1: # Наступили на мину
            field_user[x][y] = 1 # Открываем мину
            users[user_id]["game_over"] = True
            game_just_ended = True
            answer_text = LEXICON["lose"]
        else: # Открываем безопасную клетку
            open_empty_cells(user_id, x, y)
            if check_win(user_id):
                users[user_id]["game_over"] = True
                game_just_ended = True
                answer_text = LEXICON["win"]
            else:
                answer_text = LEXICON[field_mines[x][y]] if field_mines[x][y] != 0 else "" # Пустой текст для 0

    elif game_mode == "flag":
        if field_user[x][y] == 1: # Уже открыта, флаг не ставим
            answer_text = LEXICON["already_opened"]
        elif field_user[x][y] == 0: # Закрыта, ставим флаг
            field_user[x][y] = 2
            if check_win(user_id): # Проверка победы после установки флага
                users[user_id]["game_over"] = True
                game_just_ended = True
                answer_text = LEXICON["win"]
            else:
                answer_text = "Флажок установлен."
        elif field_user[x][y] == 2: # Стоит флаг, снимаем
            field_user[x][y] = 0
            answer_text = "Флажок снят."

    # Обновляем клавиатуру
    try:
        if game_just_ended:
            # Если игра закончилась, текст сообщения меняется, чтобы показать результат
            await callback.message.edit_text(
                text=answer_text,
                reply_markup=get_sapper_keyboard(user_id) # Показываем все мины при проигрыше
            )
        else:
            await callback.message.edit_reply_markup(
                reply_markup=get_sapper_keyboard(user_id)
            )
    except TelegramBadRequest:
        pass # Игнорируем, если клавиатура не изменилась

    await callback.answer(answer_text)


if __name__ == "__main__":
    print("Бот запущен!")
    dp.run_polling(bot)