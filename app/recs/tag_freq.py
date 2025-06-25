from collections import Counter
import pandas as pd

def get_featured_tag_genre_freq(df: pd.DataFrame, featured_titles: list):
    if 'tags' not in df.columns:
        df['tags'] = [[] for _ in range(len(df))]
    if 'genres' not in df.columns:
        df['genres'] = [[] for _ in range(len(df))]
    featured_df = df[df['title'].isin(featured_titles)]

    all_tags = []
    all_genres = []
    for tags in featured_df['tags']:
        if isinstance(tags, list):
            all_tags.extend(tags)
    for genres in featured_df['genres']:
        if isinstance(genres, list):
            all_genres.extend(genres)
    tag_counter = Counter(all_tags)
    genre_counter = Counter(all_genres)
    anime_count = len(featured_df)
    tag_coef = {tag: max(0.1, count / anime_count) for tag, count in tag_counter.items()}
    genre_coef = {genre: max(0.1, count / anime_count) for genre, count in genre_counter.items()}
    return tag_coef, genre_coef, featured_df
