import pandas as pd

from german_protest_registrations.paths import data


def bremen():
    path = data / "interim/csv/Bremen"
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        # Handle both old (2022) and new (2023) column names
        df = df.rename(
            columns={
                "Beginn": "event_date",
                "Ende": "event_date_end",
                "Datum": "event_date",  # 2023 column name
                "Versammlungsthema": "topic",
                "Thema/Motto": "topic",  # 2023 column name
                "Ort": "location",
            },
        )
        if "event_date" in df.columns:
            df["event_date"] = df["event_date"].str.replace("NV", "")
        if "event_date_end" in df.columns:
            df["event_date_end"] = df["event_date_end"].str.replace("NV", "")
        dfs.append(df)
    df = pd.concat(dfs)
    df = df[["event_date", "topic", "location"]]
    df["city"] = "Bremen"
    df["region"] = "Bremen"
    df["is_regional_capital"] = True
    return df


if __name__ == "__main__":
    df = bremen()
    print(df.sample(10))
