import logging
import os  # Добавлено для работы с файлами отчетов
from datetime import datetime

# Импорты для Bot, DP, Router и нового синтаксиса parse_mode
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, StateFilter
from aiogram.client.default import DefaultBotProperties # НОВЫЙ ИМПОРТ ДЛЯ ParseMode

# Импорт настроек и "базы данных"
from config import BOT_TOKEN, ADMIN_ID
from db import DB, get_user, save_user_data, is_registered, generate_user_report, generate_event_report

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация роутера
router = Router()

# --- 1. FSM СТАТУСЫ ---
class ProfileStates(StatesGroup):
    name = State()
    surname = State()
    age = State()
    gender = State()
    region = State()
    interests = State()
    photo = State()

class EventCreationStates(StatesGroup):
    name = State()
    datetime = State()
    address = State()
    description = State()
    notification = State()
    img = State()
    invite = State()
    confirm_save = State()

class SearchStates(StatesGroup):
    age_min = State()
    age_max = State()
    gender = State()
    interest = State()
    region = State()


# --- 2. КЛАВИАТУРЫ (ИСПРАВЛЕНА ValidationError) ---

phone_request_kb = types.ReplyKeyboardMarkup(
    keyboard=[[types.KeyboardButton(text="📱 Предоставить номер", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)

main_menu_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="👤 Мой профиль"), types.KeyboardButton(text="👥 Общение")],
        [types.KeyboardButton(text="🗓 Мероприятие")]
    ],
    resize_keyboard=True
)

event_menu_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="➕ Создать мероприятие"), types.KeyboardButton(text="🗓 Мои мероприятия")],
        [types.KeyboardButton(text="👥 Мероприятия друзей"), types.KeyboardButton(text="🔙 В главное меню")]
    ],
    resize_keyboard=True
)

# Клавиатура для выбора пола (используется в FSM)
gender_kb = types.ReplyKeyboardMarkup(
    keyboard=[[types.KeyboardButton(text="Мужской"), types.KeyboardButton(text="Женский")]],
    resize_keyboard=True
)

# Клавиатура для подтверждения (используется в FSM)
confirm_kb = types.ReplyKeyboardMarkup(
    keyboard=[[types.KeyboardButton(text="✅ Сохранить"), types.KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True
)


# --- 3. АВТОРИЗАЦИЯ И НАЧАЛО РЕГИСТРАЦИИ ---

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    """Первый вход в бот и запрос номера телефона."""
    user_id = message.from_user.id

    if is_registered(user_id):
        await message.answer("С возвращением! Главное меню:", reply_markup=main_menu_kb)
    else:
        # Сценарий 2.2.1: Запрос номера
        await message.answer(
            "Добро пожаловать! Для начала работы предоставьте ваш номер телефона.",
            reply_markup=phone_request_kb
        )

@router.message(F.content_type == types.ContentType.CONTACT)
async def handle_contact(message: types.Message, state: FSMContext):
    """Обработка контакта и начало регистрации."""
    user_id = message.from_user.id
    phone_number = message.contact.phone_number

    # Сценарий 2.2.2: Сохранение номера и начало регистрации (Таблица 2.1.1, п. 1)
    save_user_data(user_id, {'phone': phone_number})

    await message.answer(
        "Спасибо! Теперь заполним ваш профиль. Введите ваше Имя:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(ProfileStates.name)


# --- 4. FSM: РЕГИСТРАЦИЯ/РЕДАКТИРОВАНИЕ ПРОФИЛЯ (ДОПОЛНЕНЫ ШАГИ) ---

@router.message(ProfileStates.name)
async def process_name(message: types.Message, state: FSMContext):
    if not message.text or any(char.isdigit() or not char.isalpha() and char not in ' -' for char in message.text):
        return await message.answer("Имя должно содержать только буквы и быть не менее 2 символов. Попробуйте еще раз.")

    await state.update_data(name=message.text)
    await message.answer("Введите вашу Фамилию:")
    await state.set_state(ProfileStates.surname)

@router.message(ProfileStates.surname)
async def process_surname(message: types.Message, state: FSMContext):
    if not message.text or any(char.isdigit() or not char.isalpha() and char not in ' -' for char in message.text):
        return await message.answer("Фамилия должна содержать только буквы. Попробуйте еще раз.")

    await state.update_data(surname=message.text)
    await message.answer("Укажите ваш Возраст (обязательно):")
    await state.set_state(ProfileStates.age)

@router.message(ProfileStates.age)
async def process_age(message: types.Message, state: FSMContext):
    # Валидация возраста согласно ТЗ
    if not message.text.isdigit() or not (14 <= int(message.text) <= 99):
        return await message.answer("Возраст должен быть числом в диапазоне 14-99. Попробуйте еще раз.")

    await state.update_data(age=int(message.text))

    await message.answer("Укажите ваш Пол (обязательно):", reply_markup=gender_kb)
    await state.set_state(ProfileStates.gender)

@router.message(ProfileStates.gender, F.text.in_({"Мужской", "Женский"}))
async def process_gender(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)

    # Клавиатура регионов (предполагаем, что DB['regions'] содержит список регионов)
    region_kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=r)] for r in DB.get('regions', ['Москва', 'СПБ', 'Другой'])],
        resize_keyboard=True
    )
    await message.answer("Выберите ваш Регион (обязательно):", reply_markup=region_kb)
    await state.set_state(ProfileStates.region)

@router.message(ProfileStates.region) # Здесь нужен более сложный валидатор, но для примера используем простой
async def process_region(message: types.Message, state: FSMContext):
    # Упрощенная валидация, чтобы не ломать логику
    await state.update_data(region=message.text)

    # Клавиатура интересов (предполагаем, что DB['interests'] содержит список интересов)
    interests_kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=i)] for i in DB.get('interests', ['Спорт', 'Музыка', 'Программирование'])
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите ваш Интерес (обязательно):", reply_markup=interests_kb)
    await state.set_state(ProfileStates.interests)

@router.message(ProfileStates.interests)
async def process_interests(message: types.Message, state: FSMContext):
    # Упрощенная валидация
    await state.update_data(interests=message.text)

    await message.answer("Загрузите вашу Фотографию (jpeg, jpg, png):",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ProfileStates.photo)

@router.message(ProfileStates.photo, F.content_type == types.ContentType.PHOTO)
async def process_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id

    user_data = await state.update_data(photo_id=photo_id)

    # Завершение FSM, сохранение данных
    save_user_data(message.from_user.id, user_data)

    await state.clear()
    await message.answer("🎉 Регистрация завершена! Вы в Главном меню.", reply_markup=main_menu_kb)

@router.message(ProfileStates.photo, F.content_type != types.ContentType.PHOTO)
async def process_photo_invalid(message: types.Message):
    # Правило валидации 4: Неверный формат фото
    await message.answer("🖼 Не похоже на нужный формат. Загрузите пожалуйста фото в формате jpg, jpeg или png.")


# --- 5. МЕНЮ "МОЙ ПРОФИЛЬ" ---

@router.message(F.text == "👤 Мой профиль")
async def show_profile(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user(user_id)

    if not is_registered(user_id):
        return await message.answer("Пожалуйста, закончите регистрацию.", reply_markup=phone_request_kb)

    profile_text = f"""


👤 Мой профиль

    Имя: {user_data.get('name', 'Не указано')}
    Фамилия: {user_data.get('surname', 'Не указано')}
    Возраст: {user_data.get('age', 'Не указано')}
    Пол: {user_data.get('gender', 'Не указано')}
    Регион: {user_data.get('region', 'Не указано')}
    Интересы: {user_data.get('interests', 'Не указано')}
    """

    # ИСПРАВЛЕНА КЛАВИАТУРА
    profile_kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="✏️ Редактировать данные")],
            [types.KeyboardButton(text="🔙 В главное меню")]
        ],
        resize_keyboard=True
    )

    if user_data.get('photo_id'):
        await message.answer_photo(user_data['photo_id'], caption=profile_text, reply_markup=profile_kb)
    else:
        await message.answer(profile_text, reply_markup=profile_kb)

@router.message(F.text == "✏️ Редактировать данные")
async def start_profile_edit(message: types.Message, state:FSMContext):
    # Сценарий 2.3.1.1: Переход к блоку вопросов (Таблица 2.1.1)
    await message.answer("Вы перешли в режим редактирования. Введите новое Имя:",
                          reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ProfileStates.name)

@router.message(F.text == "🔙 В главное меню")
async def back_to_main(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_menu_kb)


# --- 6. МЕНЮ "ОБЩЕНИЕ" И "ПОИСК" (ДОПОЛНЕНЫ ШАГИ) ---

@router.message(F.text == "👥 Общение")
async def communication_menu(message: types.Message):
    # ИСПРАВЛЕНА КЛАВИАТУРА
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🔎 Поиск друзей")],
            [types.KeyboardButton(text="🔙 В главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("Меню общения:", reply_markup=kb)

@router.message(F.text == "🔎 Поиск друзей")
async def start_search(message: types.Message, state: FSMContext):
    # Сценарий 1.2.2.1: Условие поиска - Возраст
    age_kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="18-20"), types.KeyboardButton(text="20-25"), types.KeyboardButton(text="26-30")],
            [types.KeyboardButton(text="30-35"), types.KeyboardButton(text="36-40"), types.KeyboardButton(text="40+")]
        ],
        resize_keyboard=True
    )
    await message.answer("Укажите Возраст:", reply_markup=age_kb)
    await state.set_state(SearchStates.age_min) # Используем age_min для начала

# 6.2. Обработка возраста и переход к полу
@router.message(SearchStates.age_min)
async def process_search_age(message: types.Message, state: FSMContext):
    # Упрощенное сохранение диапазона
    await state.update_data(search_age=message.text)

    await message.answer("Укажите Пол:", reply_markup=gender_kb)
    await state.set_state(SearchStates.gender)

# 6.3. Обработка пола и переход к интересам
@router.message(SearchStates.gender, F.text.in_({"Мужской", "Женский"}))
async def process_search_gender(message: types.Message, state: FSMContext):
    await state.update_data(search_gender=message.text)

    interests_kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=i)] for i in DB.get('interests', ['Спорт', 'Музыка', 'Программирование'])
        ] + [[types.KeyboardButton(text="Пропустить")]],
        resize_keyboard=True
    )
    await message.answer("Укажите Интерес:", reply_markup=interests_kb)
    await state.set_state(SearchStates.interest)

# 6.4. Обработка интересов и переход к региону
@router.message(SearchStates.interest)
async def process_search_interest(message: types.Message, state: FSMContext):
    await state.update_data(search_interest=message.text)

    region_kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=r)] for r in DB.get('regions', ['Москва', 'СПБ', 'Другой'])]
        + [[types.KeyboardButton(text="Начать поиск")]],
        resize_keyboard=True
    )
    await message.answer("Укажите Регион или нажмите Начать поиск:", reply_markup=region_kb)
    await state.set_state(SearchStates.region) # Переходим в состояние, где ожидаем регион или кнопку поиска

@router.message(F.text == "Начать поиск", StateFilter(SearchStates.region))
async def start_searching_results(message: types.Message, state: FSMContext):
    # Сценарий 1.2.2.5: Начало поиска
    search_data = await state.get_data()
    await state.clear()

    # Здесь должна быть логика поиска в БД по собранным критериям (search_data)
    results = [u_id for u_id, u_data in DB['users'].items() if u_id != message.from_user.id] # Заглушка

    if results:
        await message.answer(f"✅ Совпадения найдены. Найдено {len(results)} пользователей. Вывод списка:",
                              reply_markup=main_menu_kb)
        # В реальной жизни: отправка карточек с Inline-кнопкой "Добавить в друзья"
    else:
        # Сценарий 1.2.2.5: Совпадений не найдено
        await message.answer("😔 Совпадений не найдено. Попробуйте изменить условия поиска.", reply_markup=main_menu_kb)


# --- 7. МЕНЮ "МЕРОПРИЯТИЕ" (ДОПОЛНЕНЫ ШАГИ) ---

@router.message(F.text == "🗓 Мероприятие")
async def event_menu(message: types.Message):
    await message.answer("Меню мероприятий:", reply_markup=event_menu_kb)

@router.message(F.text == "➕ Создать мероприятие")
async def start_event_creation(message: types.Message, state: FSMContext):
    # Сценарий 1.3.3: Создать мероприятие (Таблица 2.3.1, п. 1)
    await message.answer("Начнем создание мероприятия. Введите Название мероприятия:",
                          reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(EventCreationStates.name)

# 7.1. Название
@router.message(EventCreationStates.name)
async def process_event_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите Дату начала мероприятия в формате дд.мм.гггг:")
    await state.set_state(EventCreationStates.datetime)

# 7.2. Дата и Время
@router.message(EventCreationStates.datetime)
async def process_event_datetime(message: types.Message, state: FSMContext):
    # Упрощенная валидация
    try:
        dt = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
    except ValueError:
        return await message.answer("Неверный формат даты или времени. Введите в формате дд.мм.гггг чч:мм.")

    await state.update_data(datetime=dt.isoformat())
    await message.answer("Добавьте Адрес места проведения мероприятия:")
    await state.set_state(EventCreationStates.address)

# ... (Остальные шаги FSM event creation должны быть добавлены по аналогии) ...

# 7.9. Последний шаг FSM: Сохранение
@router.message(EventCreationStates.confirm_save)
async def confirm_event_save(message: types.Message, state: FSMContext):
    if message.text == "✅ Сохранить":
        data = await state.get_data()

        data['id'] = len(DB['events']) + 1
        data['participants'] = [message.from_user.id]

        DB['events'].append(data)

        await message.answer("Мероприятие успешно создано и сохранено!", reply_markup=event_menu_kb)
    elif message.text == "❌ Отмена":
        await message.answer("Создание мероприятия отменено.", reply_markup=event_menu_kb)
    else:
        return await message.answer("Выберите кнопку 'Сохранить' или 'Отмена'.")

    await state.clear()


# --- 8. АДМИНИСТРИРОВАНИЕ ---

@router.message(F.text.in_({"Отчет по пользователям", "Отчет по мероприятиям"}))
async def cmd_admin_report(message: types.Message):
    """Отправка отчета по пользователям и мероприятиям (Сценарий 3.1.2/3.1.3)."""

    if message.from_user.id != ADMIN_ID:
        return

    try:
        if message.text == "Отчет по пользователям":
            report_file_path = generate_user_report()
            caption = "Отчет по пользователям успешно выгружен."
        else: # Отчет по мероприятиям
            report_file_path = generate_event_report()
            caption = "Отчет по мероприятиям успешно выгружен."

        # Отправка файла
        with open(report_file_path, 'rb') as f:
            await message.answer_document(types.FSInputFile(f.name), caption=caption)

        # Удаляем файл после отправки
        os.remove(report_file_path)

    except Exception as e:
        logging.error(f"Ошибка при генерации отчета: {e}")
        await message.answer("Произошла ошибка при выгрузке отчета.")

# Обработчик для входа в меню админа
@router.message(F.text.in_({"Админ-меню", "/admin"}), F.from_user.id == ADMIN_ID)
async def admin_menu(message: types.Message):
    # ИСПРАВЛЕНА КЛАВИАТУРА
    admin_kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Отчет по пользователям"), types.KeyboardButton(text="Отчет по мероприятиям")],
            [types.KeyboardButton(text="🔙 В главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("Административное меню:", reply_markup=admin_kb)


# --- 9. ЗАПУСК БОТА ---

# НОВАЯ КОНСТРУКЦИЯ ДЛЯ parse_mode (ИСПРАВЛЕНИЕ ОШИБКИ 2)
default_bot_properties = DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)

async def main():
    bot = Bot(token=BOT_TOKEN, default_bot_properties=default_bot_properties) # ИСПРАВЛЕН Bot
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    if ADMIN_ID:
        await bot.set_my_commands([
            types.BotCommand(command="start", description="Начать работу с ботом"),
            types.BotCommand(command="admin", description="Админ-меню (только для администратора)")
        ])

    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())