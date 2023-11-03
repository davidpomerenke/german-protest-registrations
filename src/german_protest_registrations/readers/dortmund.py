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
    # replace dates like 01.01. - 01.02.2023 with 01.01.2023
    df["event_date"] = df["event_date"].str.replace(
        r"(\d{2})\.(\d{2})\.? *- *\d{2}\.\d{2}\.(\d{4})", r"\3-\2-\1 00:00:00", regex=True
    )
    df["event_date"] = df["event_date"].str.replace(
        r"(\d{2})\.(\d{2})\.? *- *\d{2}\.\d{2}\.(\d{2})", r"20\3-\2-\1 00:00:00", regex=True
    )
    df["event_date"] = df["event_date"].str.replace(
        r"(\d{2})\.? *- *\d{2}\.(\d{2})\.(\d{4})", r"\3-\2-\1 00:00:00", regex=True
    )
    df["event_date"] = df["event_date"].str.replace(
        r"(\d{2})\.? *- *\d{2}\.(\d{2})\.(\d{2})", r"20\3-\2-\1 00:00:00", regex=True
    )
    df["event_date"] = pd.to_datetime(df["event_date"], format="%Y-%m-%d %H:%M:%S").dt.date
    df = df[["event_date", "participants_registered", "location"]]
    df["city"] = "Dortmund"
    return df


if __name__ == "__main__":
    df = dortmund()
    print(df.sample(10))
