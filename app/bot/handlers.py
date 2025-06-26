import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from .kb import get_main_kb, get_confirm_inline_kb, get_list_inline_kb, get_anime_inline_kb
from .utils import load_user_views, save_user_views, anime_preview, load_anime_dataframe, ANIME_DB_PATH, USER_DATA_PATH, TOKEN
from recs.tag_genres import top_similar_by_tags_genres
from recs.fuzzy_search import find_by_synonyms_fuzzy


bot = Bot(token=TOKEN)
dp = Dispatcher()

df = load_anime_dataframe()
user_views = load_user_views()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_views.setdefault(message.from_user.id, set())
    await message.answer(
        "йоу! я найду твой топчик аниме 🍥\n\n"
        "жми на кнопки (или просто пиши название тайтла, можно с ошибками):",
        reply_markup=get_main_kb()
    )

@dp.message(F.text == "➕ Добавить аниме")
async def add_anime_instruction(message: Message):
    await message.answer(
        "Введи название аниме (по одному или через запятую). Можно с опечатками — найду по смыслу!",
        reply_markup=get_main_kb()
    )

@dp.message(F.text == "🌸 Мой список")
async def show_my_list(message: Message):
    user_id = message.from_user.id
    user_list = user_views.get(user_id, set())
    if not user_list:
        await message.answer("Пока пусто! Добавь что-нибудь через кнопку 👇", reply_markup=get_main_kb())
        return
    txt = "🌸 <b>Твой список:</b>\n" + "\n".join(f"• {t}" for t in sorted(user_list))
    await message.answer(txt, reply_markup=get_list_inline_kb(), parse_mode="HTML")

@dp.message(F.text == "❌ Очистить список")
async def pre_clear_list(message: Message):
    user_id = message.from_user.id
    user_list = user_views.get(user_id, set())
    if not user_list:
        await message.answer("Список и так пуст 🫥", reply_markup=get_main_kb())
        return
    await message.answer(
        "❗️ <b>Точно хочешь всё удалить?</b>\nЭто навсегда!",
        reply_markup=get_confirm_inline_kb(),
        parse_mode="HTML"
    )

@dp.message(F.text == "🔥 Рекомендации")
async def get_recs_message(message: Message):
    user_id = message.from_user.id
    await send_recommendations(user_id, message)

# --------- INLINE CALLBACKS

@dp.callback_query(lambda cq: cq.data == "clearreq")
async def cb_clear_req(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "❗️ <b>Точно хочешь всё удалить?</b>\nЭто навсегда!",
        reply_markup=get_confirm_inline_kb(),
        parse_mode="HTML"
    )

@dp.callback_query(lambda cq: cq.data == "clearlist_confirm")
async def cb_clear_confirm(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_views[user_id] = set()
    save_user_views(user_views)
    await callback.answer("Список очищен 👻")
    await callback.message.answer("Готово! У тебя новый чистый список 🌈", reply_markup=get_main_kb())

@dp.callback_query(lambda cq: cq.data == "clearlist_cancel")
async def cb_clear_cancel(callback: CallbackQuery):
    await callback.answer("Отмена.")
    await callback.message.answer("Фух. Ничего не очищено 😅", reply_markup=get_main_kb())

@dp.callback_query(lambda cq: cq.data == "getrecs")
async def cb_getrecs(callback: CallbackQuery):
    user_id = callback.from_user.id
    await send_recommendations(user_id, callback.message)
    await callback.answer()

@dp.callback_query(lambda cq: cq.data.startswith("add:"))
async def cb_add_anime(callback: CallbackQuery):
    anime_title = callback.data.split(":", 1)[1]
    user_id = callback.from_user.id
    user_views.setdefault(user_id, set())
    if anime_title in user_views[user_id]:
        await callback.answer("Уже в твоём списке!", show_alert=True)
    else:
        user_views[user_id].add(anime_title)
        save_user_views(user_views)
        await callback.answer("Добавлено!")
    await callback.message.edit_reply_markup(reply_markup=get_anime_inline_kb(anime_title, True))

@dp.callback_query(lambda cq: cq.data.startswith("remove:"))
async def cb_remove_anime(callback: CallbackQuery):
    anime_title = callback.data.split(":", 1)[1]
    user_id = callback.from_user.id
    if anime_title in user_views.get(user_id, set()):
        user_views[user_id].remove(anime_title)
        save_user_views(user_views)
        await callback.answer("Удалено из твоего списка.")
    else:
        await callback.answer("Этого аниме и так нет в твоём списке.")
    await callback.message.edit_reply_markup(reply_markup=get_anime_inline_kb(anime_title, False))

@dp.callback_query(lambda cq: cq.data.startswith("details:"))
async def cb_show_details(callback: CallbackQuery):
    anime_title = callback.data.split(":", 1)[1]
    row = df[df["title"] == anime_title]
    if row.empty:
        await callback.answer("Что-то пошло не так 😅")
        return
    row = row.iloc[0]
    desc = row.get("description", "(нет описания)")
    link = row.get("link") or row.get("url") or row.get("siteUrl")
    text = f"📰 <b>{anime_title}</b>\n\n{desc[:2000]}\n"
    if link:
        text += f"\n<a href='{link}'>Подробнее / Shikimori</a>"
    await callback.answer()
    await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=False)

@dp.callback_query(lambda cq: cq.data.startswith("similar:"))
async def cb_show_similar(callback: CallbackQuery):
    anime_title = callback.data.split(":", 1)[1]
    top_recs = top_similar_by_tags_genres(df, [anime_title], top_n=3)
    await callback.answer()
    if top_recs.empty:
        await callback.message.answer("Похожих тайтлов не нашлось 🥹")
        return
    for _, row in top_recs.iterrows():
        preview = anime_preview(row)
        in_list = row['title'] in user_views.get(callback.from_user.id, set())
        if preview["picture"]:
            await callback.message.answer_photo(
                photo=preview["picture"],
                caption=preview["text"][:1024],
                parse_mode="HTML",
                reply_markup=get_anime_inline_kb(row['title'], in_list)
            )
        else:
            await callback.message.answer(
                preview["text"],
                parse_mode="HTML",
                reply_markup=get_anime_inline_kb(row['title'], in_list)
            )

@dp.message()
async def handle_anime_titles(message: Message):
    if message.text in [
        "➕ Добавить аниме", "🌸 Мой список", "🔥 Рекомендации", "❌ Очистить список"
    ]:
        return
    titles = [x.strip() for x in message.text.split(",") if x.strip()]
    user_id = message.from_user.id
    user_views.setdefault(user_id, set())
    if not titles:
        await message.answer("Ничего не ввёл, попробуй ещё раз 🫠", reply_markup=get_main_kb())
        return
    for t in titles:
        matches = find_by_synonyms_fuzzy(df, t, top_n=1)
        if not matches.empty:
            row = matches.iloc[0]
            anime_title = row['title']
            in_list = anime_title in user_views[user_id]
            preview = anime_preview(row)
            if preview["picture"]:
                await message.answer_photo(
                    photo=preview["picture"], 
                    caption=preview["text"][:1024], 
                    parse_mode='HTML',
                    reply_markup=get_anime_inline_kb(anime_title, in_list)
                )
            else:
                await message.answer(
                    preview["text"], 
                    parse_mode='HTML',
                    reply_markup=get_anime_inline_kb(anime_title, in_list)
                )
        else:
            await message.answer(
                f"❌ Не найдено: <b>{t}</b>",
                parse_mode="HTML"
            )
    await message.answer("Добавь больше или запроси <b>рекомендации</b> 👇", parse_mode="HTML", reply_markup=get_main_kb())

async def send_recommendations(user_id, message):
    user_list = user_views.get(user_id, set())
    if not user_list:
        await message.answer("У тебя пока нет просмотренных аниме. Добавь хотя бы одно через кнопку!", reply_markup=get_main_kb())
        return
    await message.answer("Генерю топчик для тебя... 🎲")
    try:
        top_recs = top_similar_by_tags_genres(df, list(user_list), top_n=5)
        if top_recs.empty:
            await message.answer("Что-то похожее не нашлось 🥲 Добавь больше аниме в свой список!", reply_markup=get_main_kb())
            return
        for _, row in top_recs.iterrows():
            preview = anime_preview(row)
            in_list = row['title'] in user_list
            if preview["picture"]:
                await message.answer_photo(
                    preview["picture"], 
                    preview["text"][:1024], 
                    parse_mode="HTML",
                    reply_markup=get_anime_inline_kb(row['title'], in_list)
                )
            else:
                await message.answer(
                    preview["text"], 
                    parse_mode="HTML",
                    reply_markup=get_anime_inline_kb(row['title'], in_list)
                )
        await message.answer("Всё! Можешь бахнуть /start или добавить ещё аниме 🙃", reply_markup=get_main_kb())
    except Exception as e:
        await message.answer(f"Ошибка при подборе: {e}", reply_markup=get_main_kb())