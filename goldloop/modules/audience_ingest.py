import os
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine


def load_audience(csv_path: str, db_url: str) -> None:
    """Read a CSV file and load audience records into the database."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)

    df = pd.read_csv(csv_path)
    df = df.drop_duplicates(subset=["email"]).reset_index(drop=True)

    engine = create_engine(db_url)
    with engine.begin() as conn:
        df.to_sql("audience", conn, if_exists="append", index=False)

    print(f"Loaded {len(df)} audience records into the database.")


def load_all(csv_folder: str, db_url: str) -> None:
    for filename in os.listdir(csv_folder):
        if filename.endswith(".csv"):
            load_audience(os.path.join(csv_folder, filename), db_url)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    db_url = os.getenv("DB_URL", "sqlite:///goldloop.db")
    load_all("data", db_url)
