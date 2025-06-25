import os
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ANIME_DB_PATH = os.getenv("ANIME_DB_PATH")
USER_DATA_PATH = os.getenv("USER_DATA_PATH")

def load_anime_dataframe():
    anime_list = []
    try:
        with open(ANIME_DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            anime_list = data.get("data", [])
    except Exception as e:
        print(f"ошибка при загрузке базы аниме: {e}")
    df = pd.DataFrame(anime_list)
    for col in ('synonyms', 'genres', 'tags', 'producers'):
        if col not in df.columns:
            df[col] = [[] for _ in range(len(df))]
        df[col] = df[col].apply(lambda x: x if isinstance(x, list) else [])
    return df

def load_user_views():
    views = {}
    if os.path.exists(USER_DATA_PATH):
        try:
            with open(USER_DATA_PATH, "r", encoding="utf-8") as f:
                views = json.load(f)
                views = {int(uid): set(lst) for uid, lst in views.items()}
        except Exception as e:
            print(f"битый user json: {e}")
            views = {}
    return views

def save_user_views(user_views):
    try:
        with open(USER_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({str(uid): list(lst) for uid, lst in user_views.items()}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"ошибка сохранения user_views: {e}")

def anime_preview(row: pd.Series) -> dict:
    title = row.get("title", "???")
    typ = row.get("type", "???")
    episodes = row.get("episodes", "?")
    status = row.get("status", "?")
    year = row.get("animeSeason", {}).get("year") if isinstance(row.get("animeSeason"), dict) else ""
    genres = ', '.join(row.get("genres", [])) if "genres" in row else ""
    score = row.get("score", {}).get("arithmeticGeometricMean") if isinstance(row.get("score"), dict) else ""
    picture = row.get("picture", None)
    producers = ', '.join(row.get("producers", [])) if "producers" in row else ""
    tags = ', '.join(row.get("tags", [])) if "tags" in row else ""
    text = (
        f"<b>{title}</b>  {('⭐️' + str(score)) if score else ''}\n"
        f"Тип: {typ} | Эп.: {episodes} | {status or '?'} | {year or ''}\n"
        f"Жанры: {genres}\n"
        f"Теги: {tags}\n"
        f"Продюсеры: {producers or '-'}"
    )
    return {"text": text.strip(), "picture": picture}