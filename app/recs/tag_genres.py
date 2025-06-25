import pandas as pd
from .tag_freq import get_featured_tag_genre_freq

def top_similar_by_tags_genres(df: pd.DataFrame, featured_titles: list, top_n: int = 10):
    tag_coef, genre_coef, featured_df = get_featured_tag_genre_freq(df, featured_titles)
    tag_coef = tag_coef or dict()
    genre_coef = genre_coef or dict()
    tag_coef_keys = set(tag_coef.keys())
    genre_coef_keys = set(genre_coef.keys())
    is_not_featured = ~df['title'].isin(featured_titles)
    candidates = df[is_not_featured].copy()
    sim_scores = []
    tags_series = candidates['tags'].fillna("").apply(lambda x: x if isinstance(x, list) else [])
    genres_series = candidates['genres'].fillna("").apply(lambda x: x if isinstance(x, list) else [])
    for tags, genres in zip(tags_series, genres_series):   
        score = 0.0
        intersect_tags = tag_coef_keys & set(tags)
        score += sum(tag_coef[tag] for tag in intersect_tags)
        intersect_genres = genre_coef_keys & set(genres)
        score += sum(genre_coef[genre] for genre in intersect_genres)
        sim_scores.append(score)
    candidates['sim_score'] = sim_scores
    return candidates.sort_values(by='sim_score', ascending=False).head(top_n)

