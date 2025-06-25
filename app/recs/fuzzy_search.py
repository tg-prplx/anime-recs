import pandas as pd
from difflib import get_close_matches

def find_by_synonyms_fuzzy(df: pd.DataFrame, name: str, top_n: int = 3) -> pd.DataFrame:
    name = name.strip().lower()
    mask_title = df["title"].apply(lambda title: name == title.lower())
    mask_syn = df["synonyms"].apply(
        lambda syns: any(name == s.lower() for s in syns) if isinstance(syns, list) else False
    )
    filtered = df[mask_syn | mask_title]

    if 'score' in df.columns:
        filtered = filtered.copy()
        filtered['agm'] = filtered['score'].apply(lambda d: d.get('arithmeticGeometricMean') if isinstance(d, dict) else None)
        filtered = filtered.sort_values(by='agm', ascending=False)
        
    return filtered.head(top_n)