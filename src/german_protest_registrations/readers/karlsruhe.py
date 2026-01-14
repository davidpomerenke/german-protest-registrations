import pandas as pd

from german_protest_registrations.paths import data


def karlsruhe():
    path = data / "interim/csv/Karlsruhe"
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file, skiprows=1)
        df = df.rename(
            columns={
                "Datum": "event_date",
                "Thema": "topic",
                "Ort": "location",
                "Teilnehmende": "participants_registered",
                "Angemeldete Teilnehmerzahl": "participants_registered",  # 2023 column name
                "Absage": "cancelled",
            },
        )
        # Filter cancelled events only if the column exists
        if "cancelled" in df.columns:
            df = df[df["cancelled"] != "x"]
        dfs.append(df)
    df = pd.concat(dfs)
    # Select only available columns
    cols = ["event_date", "topic"]
    if "location" in df.columns:
        cols.append("location")
    if "participants_registered" in df.columns:
        cols.append("participants_registered")
    df = df[cols]
    df["city"] = "Karlsruhe"
    df["region"] = "Baden-Württemberg"
    df["is_regional_capital"] = False
    return df


if __name__ == "__main__":
    df = karlsruhe()
    print(df.sample(10))
