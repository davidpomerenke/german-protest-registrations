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
    return df


if __name__ == "__main__":
    df = berlin()
    print(df.sample(10))
