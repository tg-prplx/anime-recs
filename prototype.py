import pandas as pd
import json
from collections import Counter
import time

with open('anime-offline-database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

anime_list = data['data']
df = pd.DataFrame(anime_list)

def find_by_synonyms(df: pd.DataFrame, name: str, id: int = 1) -> pd.DataFrame:
    name = name.strip().lower()
    mask_title = df["title"].apply(lambda title: name == title.lower())
    mask_syn = df["synonyms"].apply(lambda syns: syns is not None and name in list(map(lambda x: x.lower(), syns)))
    filtered = df[mask_syn | mask_title]
    filtered = filtered.copy()
    filtered['agm'] = filtered['score'].apply(
        lambda d: d.get('arithmeticGeometricMean') if isinstance(d, dict) else None
    )
    fr = filtered.sort_values(by='agm', ascending=False).head(id)
    return fr

def get_featured_tag_genre_freq(df: pd.DataFrame, featured_titles: list):
    if 'tags' not in df.columns:
        df['tags'] = [[] for _ in range(len(df))]
    if 'genres' not in df.columns:
        df['genres'] = [[] for _ in range(len(df))]
    featured_df = df[df['title'].isin(featured_titles)]
    all_tags = sum(featured_df['tags'], [])
    all_genres = sum(featured_df['genres'], [])
    tag_counter = Counter(all_tags)
    genre_counter = Counter(all_genres)
    anime_count = len(featured_df)
    tag_coef = {tag: max(0.1, count / anime_count) for tag, count in tag_counter.items()}
    genre_coef = {genre: max(0.1, count / anime_count) for genre, count in genre_counter.items()}
    return tag_coef, genre_coef, featured_df

def top_similar_by_tags_genres(df: pd.DataFrame, featured_titles: list, top_n: int = 10):
    tag_coef, genre_coef, featured_df = get_featured_tag_genre_freq(df, featured_titles)
    mask_non_feat = ~df['title'].isin(featured_titles)
    candidates = df[mask_non_feat].copy()
    def score_row(row):
        score = 0.0
        for tag in row['tags']:
            score += tag_coef.get(tag, 0)
        for genre in row['genres']:
            score += genre_coef.get(genre, 0)
        return score
    candidates['sim_score'] = candidates.apply(score_row, axis=1)
    top = candidates.sort_values(by='sim_score', ascending=False).head(top_n)
    return top

list_vieved = ["KonoSuba", 'Death Note', 'JoJo no Kimyō na Bōken', 'Vermeil in Gold: The Failing Student and the Strongest Scourge Plunge Into the World of Magic', 'Kobayashi-san Chi no Maid Dragon', 'Jujutsu Kaisen', 'Rascal Does Not Dream of Bunny Girl Senpai', 'My Dress-Up Darling', 'Fuufu Ijou, Koibito Miman']
time_b = time.time()
result = top_similar_by_tags_genres(df, list_vieved)
time_a = time.time()
print(time_a - time_b)
print(result)
