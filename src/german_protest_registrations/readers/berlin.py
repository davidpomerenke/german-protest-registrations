from pathlib import Path

import pandas as pd


def berlin():
    path = Path("data/interim/csv/Berlin")
    dfs = []
    fds_path = path / "2020.csv"
    df = pd.read_csv(fds_path)
    df = df.rename(
        columns={
            "Datum": "event_date",
            "Thema": "topic",
            "Teilnehmende (Angemeldet)": "participants_registered",
            "Teilnehmende (tatsächlich)": "participants_actual",
        }
    )
    # there is an overlap between the two files, so we cut off the first file
    df = df[pd.to_datetime(df["event_date"], format="%d.%m.%Y") < pd.to_datetime("2020-07-01")]
    df = df[["event_date", "topic", "participants_registered", "participants_actual"]]
    dfs.append(df)
    for file in path.glob("*.csv"):
        if file.resolve() == fds_path.resolve():
            continue
        df = pd.read_csv(file)
        df = df.rename(
            columns={
                "Datum": "event_date",
                "Von": "start",
                "Bis": "end",
                "Thema": "topic",
                "Strasse": "street",
                "Nr": "number",
                "PLZ": "zip",
                "Aufzugsstrecke": "route",
                "Teilnehmende (angemeldet)": "participants_registered",
                "Teilnehmende (tatsächlich)": "participants_actual",
            },
        )
        df["start"] = df["start"].str.replace("24:00", "23:59")
        df["end"] = df["end"].str.replace("24:00", "23:59")
        df["start"] = pd.to_datetime(df["start"], format="%H:%M").dt.time
        df["end"] = pd.to_datetime(df["end"], format="%H:%M").dt.time
        df = df[
            [
                "event_date",
                "start",
                "end",
                "topic",
                "participants_registered",
                "participants_actual",
            ]
        ]
        dfs.append(df)
    df = pd.concat(dfs)
    df["city"] = "Berlin"
    df["region"] = "Berlin"
    df["is_regional_capital"] = True
    return df


if __name__ == "__main__":
    df = berlin()
    print(df.sample(10))
