from pathlib import Path

import pandas as pd


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
    df = df[["event_date", "topic", "location", "participants_registered"]]
    df["city"] = "Saarbrücken"
    df["region"] = "Saarland"
    df["is_regional_capital"] = True
    return df


if __name__ == "__main__":
    df = saarbruecken()
    print(df.sample(20))
