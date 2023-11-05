import pandas as pd

from german_protest_registrations.paths import data


def duisburg():
    path = data / "interim/csv/Duisburg"
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        df = df.rename(
            columns={
                "Datum": "event_date",
                "Thema": "topic",
                "Ort, Aufzugsweg": "location",
                "TN-Zahl": "participants_registered",
            },
        )
        df["event_date"] = df["event_date"].str.replace(r"^\s*(-|\?)+\s*$", "", regex=True)
        dfs.append(df)
    df = pd.concat(dfs)
    df = df[["event_date", "topic", "location", "participants_registered"]]
    df["city"] = "Duisburg"
    df["region"] = "Nordrhein-Westfalen"
    df["is_regional_capital"] = False
    return df


if __name__ == "__main__":
    df = duisburg()
    print(df.sample(10))
