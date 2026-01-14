import pandas as pd

from german_protest_registrations.paths import data

# Dortmund 2023 data now includes topics!


def dortmund():
    path = data / "interim/csv/Dortmund"
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        df = df.rename(
            columns={
                "Datum": "event_date",
                "ang. TN-Zahl": "participants_registered",
                "Ort": "location",
                "Thema": "topic",  # Added for 2023 data
            },
        )
        # Select available columns (some may not exist in older data)
        cols = ["event_date"]
        if "topic" in df.columns:
            cols.append("topic")
        if "participants_registered" in df.columns:
            cols.append("participants_registered")
        cols.append("location")
        df = df[cols]
        dfs.append(df)
    df = pd.concat(dfs)
    df["city"] = "Dortmund"
    df["region"] = "Nordrhein-Westfalen"
    df["is_regional_capital"] = False
    return df


if __name__ == "__main__":
    df = dortmund()
    print(df.sample(10))
