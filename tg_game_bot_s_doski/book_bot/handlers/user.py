from copy import deepcopy

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from filters.filters import IsDelBookmarkCallbackData, IsDigitCallbackData
from keyboards.bookmarks_kb import create_bookmarks_keyboard,create_edit_keyboard
from keyboards.pagination_kb import create_pagination_keyboard
from lexicon.lexicon import LEXICON

user_router = Router()


@user_router.message(CommandStart())
async def process_start_command(message: Message, db: dict):
    await message.answer(LEXICON[message.text])
    if message.from_user.id not in db["users"]:
        db["users"][message.from_user.id] = deepcopy(db.get("user_template"))


@user_router.message(Command(commands="help"))
async def process_help_command(message: Message):
    await message.answer(LEXICON[message.text])


@user_router.message(Command(commands="beginning"))
async def process_beginning_command(message: Message, book: dict, db: dict):
    db["users"][message.from_user.id]["page"] = 1
    text = book[1]
    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard(
            "backward",
            f"1/{len(book)}",
            "forward",
        ),
    )


@user_router.message(Command(commands="continue"))
async def process_continue_command(message: Message, book: dict, db: dict):
    text = book[db["users"][message.from_user.id]["page"]]
    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard(
            "backward",
            f"{db['users'][message.from_user.id]['page']}/{len(book)}",
            "forward",
        ),
    )


@user_router.message(Command(commands="bookmarks"))
async def process_bookmarks_command(message: Message, book: dict, db: dict):
    if db["users"][message.from_user.id]["bookmarks"]:
        await message.answer(
            text=LEXICON[message.text],
            reply_markup=create_bookmarks_keyboard(
                *db["users"][message.from_user.id]["bookmarks"], book=book
            ),
        )
    else:
        await message.answer(text=LEXICON["no_bookmarks"])


@user_router.callback_query(F.data =="forward")
async def process_forward_press(callback: CallbackQuery,book: dict, db: dict):
    current_page = db["users"][callback.from_user.id]["page"]
    if current_page < len(book):
        db["users"][callback.from_user.id]["page"]+=1
        text = book[current_page + 1]
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                "backward",
                f"{current_page + 1}/{len(book)}",
                "forward",
            ),
        )
    await callback.answer()


@user_router.callback_query(F.data =="backward")
async def process_backward_press(callback: CallbackQuery,book: dict, db: dict):
    current_page = db["users"][callback.from_user.id]["page"]
    if current_page < 1:
        db["users"][callback.from_user.id]["page"] -=1
        text = book[current_page - 1]
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                "backward",
                f"{current_page - 1}/{len(book)}",
                "forward",
            ),
        )
    await callback.answer()


@user_router.callback_query(
    lambda x: "/" in x.data and x.data.replace("/","").isdigit()
 )
async def process_page_press(callback: CallbackQuery, db: dict):
    db["users"][callback.from_user.id]["bookmarks"].add(
        db["users"][callback.from_user.id]["page"]
    )
    await callback.answer("Страница добавлена в закладки!")


@user_router.callback_query(IsDigitCallbackData())
async def process_bookmark_press(callback: CallbackQuery, book: dict, db: dict):
    text = book[int(callback.data)]
    db["users"][callback.from_user.id]["page"] = int(callback.data)
    await callback.message.edit_text(
        text=text,
        reply_markup=create_pagination_keyboard(
            "backward",
            f"{db['users'][callback.from_user.id]['page']}/{len(book)}",
            "forward",
        ),
    )


@user_router.callback_query(F.data == "edit_bookmarks")
async def process_edit_press(callback: CallbackQuery, book: dict, db: dict):
    await callback.message.edit_text(
        text=LEXICON[callback.data],
        reply_markup=create_edit_keyboard(
            *db["users"][callback.from_user.id]["bookmarks"], book=book
        ),
    )


@user_router.callback_query(F.data == "cancel")
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON["cancel_text"])


@user_router.callback_query(IsDelBookmarkCallbackData())
async def process_del_bookmark_press(callback: CallbackQuery,book: dict, db: dict):
    db["users"][callback.from_user.id]["bookmarks"].remove(int(callback.data[:-3]))
    if db["users"][callback.from_user.id]["bookmarks"]:
        await callback.message.edit_text(
            text=LEXICON["/bookmarks"],
            reply_markup=create_edit_keyboard(
                *db["users"][callback.from_user.id]["bookmarks"], book=book
            ),
        )
    else:
        await callback.message.edit_text(text=LEXICON["no_bookmarks"])
