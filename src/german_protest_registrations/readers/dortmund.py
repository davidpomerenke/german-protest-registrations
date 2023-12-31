import pandas as pd

from german_protest_registrations.paths import data

# Dortmund does not have topics
# but starting from 2023 they will have them!


def dortmund():
    path = data / "interim/csv/Dortmund"
    df = pd.read_csv(path / "2022_2019 - 2022.csv")
    df = df.rename(
        columns={
            "Datum": "event_date",
            "ang. TN-Zahl": "participants_registered",
            "Ort": "location",
        },
    )
    df = df[["event_date", "participants_registered", "location"]]
    df["city"] = "Dortmund"
    df["region"] = "Nordrhein-Westfalen"
    df["is_regional_capital"] = False
    return pd.DataFrame()


if __name__ == "__main__":
    df = dortmund()
    print(df.sample(10))
