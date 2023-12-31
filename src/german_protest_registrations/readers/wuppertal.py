import pandas as pd

from german_protest_registrations.paths import data


def wuppertal():
    path = data / "interim/csv/Wuppertal"
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        df = df.rename(
            columns={
                "Datum": "event_date",
                "Veranstalter": "organizer",
                "Thema": "topic",
                "Versammlungsort": "location",
                "Teilnehmer": "participants_registered",
            },
        )
        df = df.dropna(subset=["event_date"])
        dfs.append(df)
    df = pd.concat(dfs)
    df = df[["event_date", "organizer", "topic", "location", "participants_registered"]]
    df["city"] = "Wuppertal"
    df["region"] = "Nordrhein-Westfalen"
    df["is_regional_capital"] = False
    return df


if __name__ == "__main__":
    df = wuppertal()
    print(df.sample(20))
