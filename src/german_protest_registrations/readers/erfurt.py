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
        dfs.append(df)
    df = pd.concat(dfs)
    df = df[["event_date", "organizer", "topic", "location"]]
    df["city"] = "Erfurt"
    df["region"] = "Thüringen"
    df["is_regional_capital"] = True
    return df


if __name__ == "__main__":
    df = erfurt()
    print(df.sample(10))
