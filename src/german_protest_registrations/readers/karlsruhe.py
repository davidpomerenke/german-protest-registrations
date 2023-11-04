from pathlib import Path

import pandas as pd


def karlsruhe():
    path = Path("data/interim/csv/Karlsruhe")
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file, skiprows=1)
        df = df.rename(
            columns={
                "Datum": "event_date",
                "Thema": "topic",
                "Ort": "location",
                "Teilnehmende": "participants_registered",
                "Absage": "cancelled",
            },
        )
        df = df[df["cancelled"] != "x"]
        dfs.append(df)
    df = pd.concat(dfs)
    df = df[["event_date", "topic", "location", "participants_registered"]]
    df["city"] = "Karlsruhe"
    df["region"] = "Baden-Württemberg"
    df["is_regional_capital"] = False
    return df


if __name__ == "__main__":
    df = karlsruhe()
    print(df.sample(10))
