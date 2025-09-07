import json
import os
from typing import List, Dict

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import create_engine
import openai


OPENAI_MODEL = "gpt-4o"


def load_audience(db_url: str) -> pd.DataFrame:
    engine = create_engine(db_url)
    return pd.read_sql("SELECT * FROM audience", engine)


def cluster_audience(df: pd.DataFrame, n_clusters: int = 3) -> List[List[int]]:
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df["tags"].fillna(""))
    kmeans = KMeans(n_clusters=n_clusters, n_init=10)
    labels = kmeans.fit_predict(X)
    clusters = [[] for _ in range(n_clusters)]
    for idx, label in enumerate(labels):
        clusters[label].append(idx)
    return clusters


def generate_persona(cluster: pd.DataFrame) -> Dict:
    prompt = (
        "Create a fictional persona description for the following audience segment. "
        "Provide tone, interests and behavior traits.\n\n"
        + cluster.to_csv(index=False)
    )
    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    persona_text = response["choices"][0]["message"]["content"].strip()
    return {"persona": persona_text}


def build_personas(db_url: str) -> List[Dict]:
    df = load_audience(db_url)
    clusters = cluster_audience(df)
    personas = []
    for cluster_idx in clusters:
        cluster_df = df.iloc[cluster_idx]
        personas.append(generate_persona(cluster_df))
    with open("logs/personas.json", "w") as f:
        json.dump(personas, f, indent=2)
    return personas


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    db_url = os.getenv("DB_URL", "sqlite:///goldloop.db")
    build_personas(db_url)
