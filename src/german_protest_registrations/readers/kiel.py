import pandas as pd

from german_protest_registrations.paths import data


def kiel():
    path = data / "interim/csv/Kiel"
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
                "Standort/Strecke": "location",  # 2023 column name
                "Personenzahl": "participants_registered",
            },
        )
        # 2023 file has dates without year (e.g., "02.01.") - add the year from filename
        if "event_date" in df.columns and "2023" in file.name:
            # Add ".2023" to dates that are just "DD.MM."
            df["event_date"] = df["event_date"].astype(str).apply(
                lambda x: x + "2023" if x.endswith(".") and len(x) < 10 else x
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
