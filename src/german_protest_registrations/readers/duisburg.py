from pathlib import Path

import pandas as pd


def duisburg():
    path = Path("data/interim/csv/Duisburg")
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        df = df.rename(
            columns={
                "Datum": "event_date",
                "Thema": "topic",
                "Ort, Aufzugsweg": "location",
                "TN-Zahl": "participants_registered",
            },
        )
        # remove time from date
        df["event_date"] = df["event_date"].str.replace(
            r"(\d{2})\.(\d{2})\.(\d{4})", r"\3-\2-\1", regex=True
        )
        df["event_date"] = df["event_date"].str.replace(r"(\d{4}-\d{2}-\d{2}).*", r"\1", regex=True)
        df["event_date"] = df["event_date"].str.replace(r"^\s*(-|\?)+\s*$", "", regex=True)
        df["event_date"] = pd.to_datetime(df["event_date"], format="%Y-%m-%d").dt.date
        dfs.append(df)
    df = pd.concat(dfs)
    df = df[["event_date", "topic", "location", "participants_registered"]]
    df["city"] = "Duisburg"
    return df


if __name__ == "__main__":
    df = duisburg()
    print(df.sample(10))
