from pathlib import Path

import pandas as pd


def bremen():
    path = Path("data/interim/csv/Bremen")
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        df = df.rename(
            columns={
                "Beginn": "event_date",
                "Ende": "event_date_end",
                "Versammlungsthema": "topic",
                "Ort": "location",
            },
        )
        df["event_date"] = df["event_date"].str.replace("NV", "")
        df["event_date_end"] = df["event_date_end"].str.replace("NV", "")
        df["event_date"] = pd.to_datetime(df["event_date"], format="%Y-%m-%d").dt.date
        df["event_date_end"] = pd.to_datetime(df["event_date_end"], format="%Y-%m-%d").dt.date
        dfs.append(df)
    df = pd.concat(dfs)
    df["city"] = "Bremen"
    return df


if __name__ == "__main__":
    df = bremen()
    print(df.sample(10))
