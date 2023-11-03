from pathlib import Path

import pandas as pd


def erfurt():
    path = Path("data/interim/csv/Erfurt")
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        df = df.rename(
            columns={
                "Datum der Vers.": "event_date",
                "Datum der Versammlung": "event_date",
                "Datum der\nVersammlung": "event_date",
                "Thema": "topic",
                "Versammlungsort": "location",
                "Ort der Versammlung / Aufzugsstrecke": "location",
                "Ort der Versammlung / Aufzuggstrecke": "location",
                "Ort d. Versammlung / Aufzugsstrecke": "location",
                "Ort der Versammlung /": "location",
                "Veranstalter/Vertreter": "organizer",
                "Versammlungsanmelder": "organizer",
                "Versammlungsmelder": "organizer",
            },
        )
        df = df.dropna(subset=["event_date", "organizer", "topic", "location"], how="all")
        # convert 04.01. - 25.01.2021 (montags) to 2021-01-04
        df["event_date"] = df["event_date"].str.replace(
            r"(\d{2})\.(\d{2}\.)?(\d{2,4})?\s*(-|\+)\s*(\d{2})\.-?(\d{2})\.(\d{4}).*",
            r"\6-\5-\1 00:00:00",
            regex=True,
        )
        df["event_date"] = pd.to_datetime(
            df["event_date"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
        ).dt.date
        dfs.append(df)
    df = pd.concat(dfs)
    df = df[["event_date", "organizer", "topic", "location"]]
    df["city"] = "Erfurt"
    return df


if __name__ == "__main__":
    df = erfurt()
    print(df.sample(10))
