from pathlib import Path

import pandas as pd


def mainz():
    path = Path("data/interim/csv/Mainz")
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file, skiprows=2)
        df = df.iloc[1:]
        df = df.drop(columns=["Lfd Nr."])
        df = df.dropna(how="all")
        df = df.rename(
            columns={
                "Datum": "event_date",
                "Datum der Veranstaltung": "event_date",
                "Datum\n": "event_date",
                "Thema": "topic",
                "Versammlungsort": "location",
                "Erwartete TN": "participants_registered",
            },
        )
        dfs.append(df)
    df = pd.concat(dfs)
    df = df[["event_date", "topic", "location", "participants_registered"]]
    df["city"] = "Mainz"
    df["region"] = "Rheinland-Pfalz"
    df["is_regional_capital"] = True
    return df


if __name__ == "__main__":
    df = mainz()
    print(df.sample(10))
