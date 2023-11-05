import pandas as pd

from german_protest_registrations.paths import data


def dresden():
    path = data / "interim/csv/Dresden"
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        df = df.rename(
            columns={
                "Datum von": "event_date",
                "Thema": "topic",
                "Ort (ausschließlich Dresden)": "location",
                "Teilnehmerzahl Anmeldung": "participants_registered",
            },
        )
        dfs.append(df)
    df = pd.concat(dfs)
    df["city"] = "Dresden"
    df["region"] = "Sachsen"
    df["is_regional_capital"] = True
    return df


if __name__ == "__main__":
    df = dresden()
    print(df.sample(10))
