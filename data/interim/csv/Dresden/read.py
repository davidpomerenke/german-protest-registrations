from pathlib import Path

import pandas as pd


def dresden():
    path = Path("data/interim/csv/Dresden")
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        df = df.rename(
            columns={
                "Datum von": "event_date",
                "Thema": "topic",
                "Ort (ausschließlich Dresden)": "location",
                "Teilnehmerzahl Anmeldung": "participants_registered",
            },
        )
        df["event_date"] = pd.to_datetime(df["event_date"], format="%Y-%m-%d").dt.date
        dfs.append(df)
    df = pd.concat(dfs)
    df["city"] = "Dresden"
    return df


if __name__ == "__main__":
    df = dresden()
    print(df.sample(10))
