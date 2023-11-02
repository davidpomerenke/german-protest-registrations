from pathlib import Path

import pandas as pd
from dateparser import parse


def saarbruecken():
    path = Path("data/interim/csv/Saarbrücken")
    dfs = []
    for filename in [
        "2022_2021 V+A.csv",
        "2022_2022 V+A.csv",
        "2022_2023 V+A.csv",
    ]:
        df = pd.read_csv(path / filename)
        df1 = df.iloc[:, :9]  # gatherings
        df1 = df1.rename(
            columns={
                "Datum ": "event_date",
                "Thema": "topic",
                "Versammlungen Ort": "location",
                "erwartete Teilnehmerzahl": "participants_registered",
            },
        )
        dfs.append(df1)
        df2 = df.iloc[:, 9:]  # marches
        df2 = df2.rename(
            columns={
                "Datum": "event_date",
                "Thema.1": "topic",
                "Anzahl Teilnehmer": "participants_registered",
            },
        )
        dfs.append(df2)
    df = pd.concat(dfs)
    df = df.dropna(subset=["event_date"])
    df["event_date"] = df["event_date"].str.replace("erl.", "").str.strip()
    df["event_date"] = (
        df["event_date"]
        .astype(str)
        .apply(
            parse, date_formats=["%d.%m.%Y", "%Y-%m-%d %H:%M:%S"], settings={"STRICT_PARSING": True}
        )
    )
    # only keep records after 2021-05-21, prior records contain no topics
    df = df[df["event_date"] >= "2021-05-21"]
    df = df[["event_date", "event_date", "topic", "location", "participants_registered"]]
    df["city"] = "Saarbrücken"
    return df


if __name__ == "__main__":
    df = saarbruecken()
    print(df.sample(20))
