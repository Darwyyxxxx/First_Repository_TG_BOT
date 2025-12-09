import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.text_decorations import html, html_decoration

bot = Bot(
    token='8564722957:AAEniZZJw8CE1a_m_4FFYvEo30ec9wBjzVM',
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text="Привет!\n\nЯ бот, демонстрирующий как работает "
             f"{html_decoration.code('html.escape')} и "
             f"{html_decoration.code('html_decoration')} в aiogram.\n"
             "Отправь команду из списка ниже:\n\n"
             "/html_decoration - обёртка для html-тегов\n"
             "/html_escape - обёртка для экранирования\n"
             "/html_error - демонстрация ошибки"
    )


# Этот хэндлер будет срабатывать на команду "/html_decoration"
@dp.message(Command(commands="html_decoration"))
async def process_html_decoration_command(message: Message):
    await message.answer(
        text=f"{html_decoration.bold('Это жирный текст')}\n"
             f"{html_decoration.italic('Это курсив')}\n"
             f"{html_decoration.underline('Это подчёркнутый текст')}\n"
             f"{html_decoration.strikethrough('Это перечёркнутый текст')}\n"
             f"{html_decoration.spoiler('Это спойлер')}\n"
             f"{html_decoration.code('Это моноширинный текст')}\n"
             f"{html_decoration.pre('Это отдельный блок текста')}\n"
             f"{html_decoration.quote('Это цитата')}\n"
             f"{html_decoration.link(value='Это ссылка', link='https://тут ссылка')}\n"
    )


# Этот хэндлер будет срабатывать на команду "/html_escape"
@dp.message(Command(commands="html_escape"))
async def process_html_escape_command(message: Message):
    await message.answer(
        text=html.escape(
            '''Метод html.escape позволяет писать в сообщениях символы,
            используемые в html-тегах, когда установлен <code>ParseMode.HTML</code>,
            без замены их специальными экранирующими последовательностями.
            Без данного метода телеграм не сможет корректно
            обработать текст, содержащий <, > и &.'''
        )
    )



# Этот хэндлер не сможет отправить текст при `ParseMode.HTML`
@dp.message(Command(commands="html_error"))
async def process_html_error_command(message: Message):
    await message.answer(
        text="Без html.escape не получится использовать символы <, > и & "
             "вне поддерживаемых html-тегов, если используется ParseMode.HTML"
    )


# Запускаем поллинг
if __name__ == "__main__":
    dp.run_polling(bot)