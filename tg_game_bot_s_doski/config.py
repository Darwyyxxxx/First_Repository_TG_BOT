import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

class Config:
    """Класс для хранения конфигурации бота."""
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    if BOT_TOKEN is None:
        raise ValueError("BOT_TOKEN не найден в .env файле или переменных окружения.")

# Создаем экземпляр конфигурации
config = Config()
