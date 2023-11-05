import pandas as pd

from german_protest_registrations.paths import data


def magdeburg():
    path = data / "interim/csv/Magdeburg"
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        # skip the second row
        df = df.iloc[1:]
        df = df.rename(
            columns={
                "Datum der Vers": "event_date",
                "Thema der Versammlung": "topic",
                "Ort der Vers": "location",
                "Unnamed: 6": "participants_registered",  # TN angemeldet
                "Unnamed: 7": "participants_actual",  # TN anwesend
            },
        )
        dfs.append(df)
    df = pd.concat(dfs)
    df = df[["event_date", "topic", "location", "participants_registered", "participants_actual"]]
    df = df.drop_duplicates(subset=["event_date", "topic", "location"], keep="last")
    df["city"] = "Magdeburg"
    df["region"] = "Sachsen-Anhalt"
    df["is_regional_capital"] = True
    return df


if __name__ == "__main__":
    df = magdeburg()
    print(df.sample(10))
