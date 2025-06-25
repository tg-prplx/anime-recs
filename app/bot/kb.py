from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)

def get_main_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="➕ Добавить аниме"), KeyboardButton(text="🌸 Мой список")],
        [KeyboardButton(text="🔥 Рекомендации"), KeyboardButton(text="❌ Очистить список")]
    ], resize_keyboard=True)

def get_confirm_inline_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, очистить!", callback_data="clearlist_confirm"),
            InlineKeyboardButton(text="🙅 Нет", callback_data="clearlist_cancel")
        ]
    ])

def get_list_inline_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔥 Получить рекомендации", callback_data="getrecs"),
        ],
        [
            InlineKeyboardButton(text="❌ Очистить список", callback_data="clearreq"),
        ]
    ])    

def get_anime_inline_kb(anime_title, in_list):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ℹ️ Подробнее", callback_data=f"details:{anime_title}")],
            [InlineKeyboardButton(
                text="✅ Уже в списке" if in_list else "➕ Добавить в список",
                callback_data=f"{'remove' if in_list else 'add'}:{anime_title}"
            )],
            [InlineKeyboardButton(text="🔍 Похожие", callback_data=f"similar:{anime_title}")]
        ]
    )