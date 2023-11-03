from pathlib import Path

import pandas as pd


def wiesbaden():
    path = Path("data/interim/csv/Wiesbaden")
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file, skiprows=2)
        df = df.rename(
            columns={
                "Datum": "event_date",
                "Organisation / verantwortliche Person": "organizer",
                "Thema": "topic",
                "Ort": "location",
                "Teilnehmerzahl": "participants_registered",
            },
        )
        df = df.dropna(subset=["event_date"])
        dfs.append(df)
    df = pd.concat(dfs)
    df = df[["event_date", "organizer", "topic", "location", "participants_registered"]]
    df["city"] = "Wiesbaden"
    return df


if __name__ == "__main__":
    df = wiesbaden()
    print(df.sample(20))
