from openpyxl import Workbook
import os
import time

# Имитация базы данных
DB = {
    # {user_id: {'name': 'Иван', 'surname': 'Иванов', 'phone': '+7...', 'age': 30, ...}}
    'users': {},

    # [{'id': 1, 'name': 'Поход', 'date': '2025-12-31', 'creator_id': 12345, 'participants': [id], ...}]
    'events': [],

    # Справочники (будут обновляться администратором)
    'regions': ['Москва', 'Санкт-Петербург', 'Казань', 'Самара'],
    'interests': ['Спорт', 'Искусство', 'IT', 'Кулинария', 'Путешествия']
}

def get_user(user_id):
    """Возвращает данные пользователя или пустой словарь."""
    return DB['users'].get(user_id, {})

def save_user_data(user_id, data):
    """Обновляет или создает запись пользователя."""
    if user_id not in DB['users']:
        DB['users'][user_id] = {}
    DB['users'][user_id].update(data)

def is_registered(user_id):
    """Проверяет, зарегистрирован ли пользователь (по наличию имени)."""
    return user_id in DB['users'] and DB['users'][user_id].get('name') is not None

def generate_user_report():
    """Генерирует Excel-отчет по пользователям (Сценарий 3.2)."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Отчет по пользователям"

    # Заголовки таблицы (по ТЗ, п. 3.2)
    headers = ["№ п/п", "Телефон", "Имя/Фамилия", "Возраст", "Пол", "Регион", "Интересы", "Путь к фото"]
    ws.append(headers)

    for i, (user_id, data) in enumerate(DB['users'].items(), 1):
        row = [
            i,
            data.get('phone', ''),
            f"{data.get('name', '')} {data.get('surname', '')}",
            data.get('age', ''),
            data.get('gender', ''),
            data.get('region', ''),
            data.get('interests', ''), # В реальном проекте: список интересов
            data.get('photo_id', 'Нет')
        ]
        ws.append(row)

    filename = f'user_report_{time.strftime("%Y%m%d_%H%M%S")}.xlsx'
    wb.save(filename)
    return filename

def generate_event_report():
    """Генерирует Excel-отчет по мероприятиям (Сценарий 3.3)."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Отчет по мероприятиям"

    # Заголовки таблицы (по ТЗ, п. 3.3)
    headers = [
        "№ п/п", "Название мероприятия", "Дата начала мероприятия", "Время начала мероприятия",
        "Адрес мероприятия", "Имя организатора мероприятия", "Фамилия организатора мероприятия",
        "Количество участников мероприятия", "Ссылка изображение мероприятия", "Оповещение",
        "Описание мероприятия"
    ]
    ws.append(headers)

    for i, data in enumerate(DB['events'], 1):
        creator_id = data.get('creator_id')
        creator = DB['users'].get(creator_id, {})

        # Разделяем дату и время (для упрощения, если хранятся вместе)
        datetime_str = data.get('datetime', ' ').split(' ')
        date_part = datetime_str[0] if len(datetime_str) > 0 else ''
        time_part = datetime_str[1] if len(datetime_str) > 1 else ''

        row = [
            i,
            data.get('name', ''),
            date_part,
            time_part,
            data.get('address', ''),
            creator.get('name', 'Неизвестно'),
            creator.get('surname', 'Неизвестно'),
            len(data.get('participants', [])), # Кол-во участников
            data.get('img_id', 'Нет'),
            data.get('notification', 'Нет'),
            data.get('description', '')
        ]
        ws.append(row)

    filename = f'event_report_{time.strftime("%Y%m%d_%H%M%S")}.xlsx'
    wb.save(filename)
    return filename