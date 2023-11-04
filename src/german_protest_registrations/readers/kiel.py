from pathlib import Path

import pandas as pd


def kiel():
    path = Path("data/interim/csv/Kiel")
    dfs = []
    for file in path.glob("*.csv"):
        if file.name == "2022_2020.csv":
            continue
        elif file.name == "2022_2021.csv":
            df = pd.read_csv(file, skiprows=1)
        else:
            df = pd.read_csv(file)
        df = df.rename(
            columns={
                "Datum": "event_date",
                "Thema": "topic",
                "Standort": "location",
                "Personenzahl": "participants_registered",
            },
        )
        dfs.append(df)
    df = pd.concat(dfs)
    df = df[["event_date", "topic", "location", "participants_registered"]]
    df["city"] = "Kiel"
    df["region"] = "Schleswig-Holstein"
    df["is_regional_capital"] = True
    return df


if __name__ == "__main__":
    df = kiel()
    print(df.sample(10))
