from pathlib import Path

import pandas as pd


def koeln():
    path = Path("data/interim/csv/Köln")
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        df = df.rename(
            columns={
                "Datum": "event_date",
                "Datum\n": "event_date",
                "Thema": "topic",
                "Ort(e) der Kundgebung": "location",
                "Ort/e der Kundgebung": "location",
                "Zahl der Teilnehm er / -\ninnen": "participants_registered",
                "erwartete TN-Zahl\n": "participants_registered",
            },
        )
        dfs.append(df)
    df = pd.concat(dfs)
    df = df[["event_date", "topic", "location", "participants_registered"]]
    df["city"] = "Köln"
    return df


if __name__ == "__main__":
    df = koeln()
    print(df.sample(10))
