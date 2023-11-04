from pathlib import Path

import pandas as pd


def dortmund():
    path = Path("data/interim/csv/Dortmund")
    df = pd.read_csv(path / "2022_2019 - 2022.csv")
    df = df.rename(
        columns={
            "Datum": "event_date",
            "ang. TN-Zahl": "participants_registered",
            "Ort": "location",
        },
    )
    df = df[["event_date", "participants_registered", "location"]]
    df["city"] = "Dortmund"
    df["region"] = "Nordrhein-Westfalen"
    df["is_regional_capital"] = False
    return df


if __name__ == "__main__":
    df = dortmund()
    print(df.sample(10))
