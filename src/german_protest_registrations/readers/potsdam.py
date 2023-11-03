from pathlib import Path

import pandas as pd


def potsdam():
    path = Path("data/interim/csv/Potsdam")
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        df.columns = [
            "event_date",
            "event_time",
            "city",
            "topic",
            "participants_registered",
            "location",
        ]
        df["event_date"] = df["event_date"].str.replace(
            r"(\d{2})\.(\d{2})\.(\d{4})", r"\3-\2-\1 00:00:00", regex=True
        )
        df["event_date"] = pd.to_datetime(
            df["event_date"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
        ).dt.date
        dfs.append(df)
    df = pd.concat(dfs)
    df = df[["event_date", "topic", "location", "participants_registered"]]
    df["city"] = "Potsdam"
    return df


if __name__ == "__main__":
    df = potsdam()
    print(df.sample(10))
