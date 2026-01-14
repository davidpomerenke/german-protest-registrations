import pandas as pd

from german_protest_registrations.paths import data


def duisburg():
    path = data / "interim/csv/Duisburg"
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        # Skip files that don't have the Datum column (template/header sheets)
        if "Datum" not in df.columns:
            continue
        df = df.rename(
            columns={
                "Datum": "event_date",
                "Thema": "topic",
                "Ort, Aufzugsweg": "location",
                "TN-Zahl": "participants_registered",
                "TN-Zahl angezeigt": "participants_registered",  # 2023 column name
            },
        )
        if "event_date" in df.columns:
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
