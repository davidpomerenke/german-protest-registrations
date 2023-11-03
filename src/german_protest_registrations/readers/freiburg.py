from pathlib import Path

import pandas as pd


def freiburg():
    path = Path("data/interim/csv/Freiburg")
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        df = df.rename(
            columns={
                "Datum": "event_date",
                "Grund/Anlass": "topic",
                "Ort bzw. Wegstrecke": "location",
            },
        )
        dfs.append(df)
    df = pd.concat(dfs)
    df = df[["event_date", "topic", "location"]]
    df["city"] = "Freiburg"
    return df


if __name__ == "__main__":
    df = freiburg()
    print(df.sample(10))
