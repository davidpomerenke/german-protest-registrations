import pandas as pd

from german_protest_registrations.paths import data


def freiburg():
    path = data / "interim/csv/Freiburg"
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        df = df.rename(
            columns={
                "Datum": "event_date",
                "Grund/Anlass": "topic",
                "Ort bzw. Wegstrecke": "location",
            },
        )
        dfs.append(df)
    df = pd.concat(dfs)
    df = df[["event_date", "topic", "location"]]
    df["city"] = "Freiburg"
    df["region"] = "Baden-Württemberg"
    df["is_regional_capital"] = False
    return df


if __name__ == "__main__":
    df = freiburg()
    print(df.sample(10))
