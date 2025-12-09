import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

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
             "HTML-разметка. Отправь команду из списка ниже:\n\n"
             "/bold - жирный текст\n"
             "/italic - наклонный текст\n"
             "/underline - подчёркнутый текст\n"
             "/strike - зачёркнутый текст\n"
             "/spoiler - спойлер\n"
             "/link - внешняя ссылка\n"
             "/tglink - внутренняя ссылка\n"
             "/code - моноширинный текст\n"
             "/pre - предварительно форматированный текст\n"
             "/precode - предварительно форматированный блок кода\n"
             "/blockquote - цитата\n"
             "/blockquoteexp - раскрывающаяся цитата\n"
             "/boldi - жирный наклонный текст\n"
             "/iu - наклонный подчёркнутый текст\n"
             "/biu - жирный наклонный подчёркнутый текст"
    )


# Этот хэндлер будет срабатывать на команду "/help"
@dp.message(Command(commands="help"))
async def process_help_command(message: Message):
    await message.answer(
        text="Я бот, демонстрирующий как работает "
             "HTML-разметка. Отправь команду из списка ниже:\n\n"
             "/bold - жирный текст\n"
             "/italic - наклонный текст\n"
             "/underline - подчёркнутый текст\n"
             "/strike - зачёркнутый текст\n"
             "/spoiler - спойлер\n"
             "/link - внешняя ссылка\n"
             "/tglink - внутренняя ссылка\n"
             "/code - моноширинный текст\n"
             "/pre - предварительно форматированный текст\n"
             "/precode - предварительно форматированный блок кода\n"
             "/blockquote - цитата\n"
             "/blockquoteexp - раскрывающаяся цитата\n"
             "/boldi - жирный наклонный текст\n"
             "/iu - наклонный подчёркнутый текст\n"
             "/biu - жирный наклонный подчёркнутый текст"
    )


# Этот хэндлер будет срабатывать на команду "/bold"
@dp.message(Command(commands="bold"))
async def process_bold_command(message: Message):
    await message.answer(
        text="&lt;b&gt;Это жирный текст&lt;/b&gt;:\n"
             "<b>Это жирный текст</b>\n\n"
             "&lt;strong&gt;И это тоже жирный текст&lt;/strong&gt;:\n"
             "<strong>И это тоже жирный текст</strong>"
    )


# Этот хэндлер будет срабатывать на команду "/italic"
@dp.message(Command(commands="italic"))
async def process_italic_command(message: Message):
    await message.answer(
        text="&lt;i&gt;Это наклонный текст&lt;/i&gt;:\n"
             "<i>Это наклонный текст</i>\n\n"
             "&lt;em&gt;И это тоже наклонный текст&lt;/em&gt;:\n"
             "<em>И это тоже наклонный текст</em>"
    )


# Этот хэндлер будет срабатывать на команду "/underline"
@dp.message(Command(commands="underline"))
async def process_underline_command(message: Message):
    await message.answer(
        text="&lt;u&gt;Это подчёркнутый текст&lt;/u&gt;:\n"
             "<u>Это подчёркнутый текст</u>\n\n"
             "&lt;ins&gt;И это тоже подчёркнутый текст&lt;/ins&gt;:\n"
             "<ins>И это тоже подчёркнутый текст</ins>"
    )


# Этот хэндлер будет срабатывать на команду "/strike"
@dp.message(Command(commands="strike"))
async def process_strike_command(message: Message):
    await message.answer(
        text="&lt;s&gt;Это зачёркнутый текст&lt;/s&gt;:\n"
             "<s>Это зачёркнутый текст</s>\n\n"
             "&lt;strike&gt;И это зачёркнутый текст&lt;/strike&gt;:\n"
             "<strike>И это зачёркнутый текст</strike>\n\n"
             "&lt;del&gt;И это тоже зачёркнутый текст&lt;/del&gt;:\n"
             "<del>И это тоже зачёркнутый текст</del>"
    )


# Этот хэндлер будет срабатывать на команду "/spoiler"
@dp.message(Command(commands="spoiler"))
async def process_spoiler_command(message: Message):
    await message.answer(
        text='&lt;span class="tg-spoiler"&gt;Это текст '
             "под спойлером&lt;/span&gt;:\n"
             '<span class="tg-spoiler">Это текст под '
             "спойлером</span>\n\n"
             "&lt;tg-spoiler&gt;И это текст под "
             "спойлером&lt;/tg-spoiler&gt;:\n"
             "<tg-spoiler>И это текст под спойлером</tg-spoiler>"
    )


# Этот хэндлер будет срабатывать на команду "/link"
@dp.message(Command(commands="link"))
async def process_link_command(message: Message):
    await message.answer(
        text='&lt;a href="https://тут ссылка'
             "ссылка&lt;/a&gt;:\n"
             '<a href="https://тут ссылка">Внешняя ссылка</a>'
    )


# Этот хэндлер будет срабатывать на команду "/tglink"
@dp.message(Command(commands="tglink"))
async def process_tglink_command(message: Message):
    await message.answer(
        text='&lt;a href="tg://user?id=ид пользователя"&gt;Внутренняя '
             "ссылка&lt;/a&gt;:\n"
             '<a href="tg://user?id=ид пользователя">Внутренняя ссылка</a>'
    )


# Этот хэндлер будет срабатывать на команду "/code"
@dp.message(Command(commands="code"))
async def process_code_command(message: Message):
    await message.answer(
        text="&lt;code&gt;Это моноширинный текст&lt;/code&gt;:\n"
             "<code>Это моноширинный текст</code>"
    )


# Этот хэндлер будет срабатывать на команду "/pre"
@dp.message(Command(commands="pre"))
async def process_pre_command(message: Message):
    await message.answer(
        text="&lt;pre&gt;Предварительно отформатированный "
             "текст&lt;/pre&gt;:\n"
             "<pre>Предварительно отформатированный текст</pre>"
    )


# Этот хэндлер будет срабатывать на команду "/precode"
@dp.message(Command(commands="precode"))
async def process_precode_command(message: Message):
    await message.answer(
        text='&lt;pre&gt;&lt;code class="language-'
             'python"&gt;Предварительно отформатированный '
             "блок кода на языке Python&lt;/code&gt;&lt;/pre&gt;:\n"
             '<pre><code class="language-python">Предварительно '
             "отформатированный блок кода на языке Python</code></pre>"
    )


# Этот хэндлер будет срабатывать на команду "/blockquote"
@dp.message(Command(commands="blockquote"))
async def process_blockquote_command(message: Message):
    await message.answer(
        text="&lt;blockquote&gt;Это цитата&lt;/blockquote&gt;:\n\n"
             "<blockquote>Это цитата</blockquote>"
    )


# Этот хэндлер будет срабатывать на команду "/blockquoteexp"
@dp.message(Command(commands="blockquoteexp"))
async def process_blockquoteexp_command(message: Message):
    await message.answer(
        text="&lt;blockquote expandable&gt;Это цитата, которая рскрывается. "
             "Видимой остаётся только её часть. Чтобы увидеть цитату полностью - "
             "нужно нажать на её правый нижний угол. Тогда она раскроется на всю "
             "ширину и можно будет прочитать полный текст данной "
             "цитаты&lt;/blockquote&gt;:\n\n"
             "<blockquote expandable>Это цитата, которая рскрывается. Видимой "
             "остаётся только её часть. Чтобы увидеть цитату полностью - нужно "
             "нажать на её правый нижний угол. Тогда она раскроется на всю ширину "
             "и можно будет прочитать полный текст данной цитаты</blockquote>"
    )


# Этот хэндлер будет срабатывать на команду "/boldi"
@dp.message(Command(commands="boldi"))
async def process_boldi_command(message: Message):
    await message.answer(
        text="&lt;b&gt;&lt;i&gt;Это жирный наклонный "
             "текст&lt;/i&gt;&lt;/b&gt;:\n\n"
             "<b><i>Это жирный наклонный текст</i></b>"
    )


# Этот хэндлер будет срабатывать на команду "/iu"
@dp.message(Command(commands="iu"))
async def process_iu_command(message: Message):
    await message.answer(
        text="&lt;i&gt;&lt;u&gt;Это наклонный подчёркнутый "
             "текст&lt;/u&gt;&lt;/i&gt;:\n\n"
             "<i><u>Это наклонный подчёркнутый текст</u></i>"
    )


# Этот хэндлер будет срабатывать на команду "/biu"
@dp.message(Command(commands="biu"))
async def process_biu_command(message: Message):
    await message.answer(
        text="&lt;b&gt;&lt;i&gt;&lt;u&gt;Это жирный "
             "наклонный подчёркнутый "
             "текст&lt;/u&gt;&lt;/i&gt;&lt;/b&gt;:\n\n"
             "<b><i><u>Это жирный наклонный подчёркнутый "
             "текст</u></i></b>"
    )


# Этот хэндлер будет срабатывать на любые сообщения, кроме команд,
# отлавливаемых хэндлерами выше
async def send_echo(message: Message):
    await message.answer(
        text="Я даже представить себе не могу, "
             "что ты имеешь в виду\n\n"
             "Чтобы посмотреть список доступных команд - "
             "отправь команду /help"
    )


# Запускаем поллинг
if __name__ == "__main__":
    dp.run_polling(bot)