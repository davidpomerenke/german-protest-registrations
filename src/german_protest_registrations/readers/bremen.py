import pandas as pd

from german_protest_registrations.paths import data


def bremen():
    path = data / "interim/csv/Bremen"
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        df = df.rename(
            columns={
                "Beginn": "event_date",
                "Ende": "event_date_end",
                "Versammlungsthema": "topic",
                "Ort": "location",
            },
        )
        df["event_date"] = df["event_date"].str.replace("NV", "")
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
