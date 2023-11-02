from pathlib import Path

import pandas as pd


def karlsruhe():
    path = Path("data/interim/csv/Karlsruhe")
    dfs = []
    for file in path.glob("*.csv"):
        # skip the first row and use the second row as header
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
        df["event_date"] = pd.to_datetime(
            df["event_date"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
        ).dt.date
        df = df[df["cancelled"] != "x"]
        dfs.append(df)
    df = pd.concat(dfs)
    df = df[["event_date", "topic", "location", "participants_registered"]]
    df["city"] = "Karlsruhe"
    return df


if __name__ == "__main__":
    df = karlsruhe()
    print(df.sample(10))
