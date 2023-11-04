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
        dfs.append(df)
    df = pd.concat(dfs)
    df = df[["event_date", "topic", "location", "participants_registered"]]
    df["city"] = "Potsdam"
    df["region"] = "Brandenburg"
    df["is_regional_capital"] = True
    return df


if __name__ == "__main__":
    df = potsdam()
    print(df.sample(10))
