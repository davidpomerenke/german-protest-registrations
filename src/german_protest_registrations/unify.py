import json
import re
import warnings

import pandas as pd
import swifter
from dateparser import parse
from joblib import Memory
from tqdm import tqdm

from german_protest_registrations.readers.augsburg import augsburg
from german_protest_registrations.readers.berlin import berlin
from german_protest_registrations.readers.bremen import bremen
from german_protest_registrations.readers.dortmund import dortmund
from german_protest_registrations.readers.dresden import dresden
from german_protest_registrations.readers.duisburg import duisburg
from german_protest_registrations.readers.erfurt import erfurt
from german_protest_registrations.readers.freiburg import freiburg
from german_protest_registrations.readers.karlsruhe import karlsruhe
from german_protest_registrations.readers.kiel import kiel
from german_protest_registrations.readers.koeln import koeln
from german_protest_registrations.readers.magdeburg import magdeburg
from german_protest_registrations.readers.mainz import mainz
from german_protest_registrations.readers.mannheim import mannheim
from german_protest_registrations.readers.muenchen import muenchen
from german_protest_registrations.readers.potsdam import potsdam
from german_protest_registrations.readers.saarbruecken import saarbruecken
from german_protest_registrations.readers.wiesbaden import wiesbaden
from german_protest_registrations.readers.wuppertal import wuppertal

warnings.filterwarnings("ignore", module="dateparser")
cache = Memory(".cache", verbose=0).cache
_ = swifter  # just so it doesn't get dropped from the imports


def read_dfs() -> pd.DataFrame:
    df_readers = [
        augsburg,
        berlin,
        bremen,
        dortmund,
        dresden,
        duisburg,
        erfurt,
        freiburg,
        karlsruhe,
        kiel,
        koeln,
        magdeburg,
        mainz,
        mannheim,
        muenchen,
        potsdam,
        saarbruecken,
        wiesbaden,
        wuppertal,
    ]
    dfs = {read.__name__: read() for read in tqdm(df_readers, mininterval=1)}
    df = pd.concat(dfs, ignore_index=True)
    return df


@cache
def parse_dates(df):
    """Automatically parse dates from the event_date column.

    On the original data set, `dateparser` fails to parse 656 of 54246 dates, and the additional rules reduce this to 82.
    """
    df["event_date"] = df["event_date"].astype(str)
    df["event_date_text"] = df["event_date"].copy()
    df = df[~df["event_date"].isna() & (df["event_date"].str.len() > 0)]
    df = df[~df["event_date"].str.lower().str.contains(r"abges|absag|gesamt", regex=True)]
    df["event_date"] = df["event_date"].str.replace("\n", " ")
    # 01.01.2020 ... 31.12.2020 -> 01.01.2020
    df["event_date"] = df["event_date"].str.replace(
        r"^[^\d]*(\d\d)\.(\d\d)\.(\d{2,4}).*$", r"\1.\2.\3", regex=True
    )
    # 01.01. ... 31.12.20 -> 01.01.20
    df["event_date"] = df["event_date"].str.replace(
        r"^[^\d]*(\d?\d)\.(\d?\d)\.[^\d].*\d?\d\.\d?\d\.(\d{2,4}).*$", r"\1.\2.\3", regex=True
    )
    # 01. ... 31.02.20 -> 01.02.20
    df["event_date"] = df["event_date"].str.replace(
        r"^[^\d]*(\d?\d)\.[^\d].*\d?\d\.(\d?\d)\.(\d{2,4}).*$", r"\1.\2.\3", regex=True
    )
    df["event_date"] = (
        df["event_date"]
        .astype(str)
        .swifter.apply(
            parse,
            date_formats=["%d.%m.%Y", "%Y-%m-%d %H:%M:%S"],
            settings={"STRICT_PARSING": True},
        )
    )
    print(f"Could not parse {df['event_date'].isnull().sum()} of {len(df)} dates")
    return df


def add_unparsable_dates(df):
    # write the original texts of the unparsable dates to a json file
    keys = df["event_date_text"][df["event_date"].isnull()].tolist()
    file = "data/interim/unparsable_dates.json"
    if False:
        with open(file, "w") as f:
            json.dump(dict(zip(keys, [""] * len(keys))), f, indent=4, ensure_ascii=False)
    else:
        # assume that a human has entered the correct dates as values into the json file and read them back in
        with open(file) as f:
            unparseable_dates = json.load(f)
        unparseable_dates = pd.Series(unparseable_dates).astype(str).apply(parse).values
        df.loc[df["event_date"].isnull(), "event_date"].update(unparseable_dates)
        df = df[~df["event_date"].isnull()]
    return df


def process_dates(df):
    df = df.dropna(subset=["event_date"])
    df = parse_dates(df)
    df = add_unparsable_dates(df)
    df = df.drop(columns=["event_date_text"])
    # event details are missing before these dates
    df = df[
        ~((df["city"] == "Kiel") & (df["event_date"] < pd.to_datetime("2021-04-01")))
        & ~((df["city"] == "Saarbrücken") & (df["event_date"] < pd.to_datetime("2021-06-01")))
        & ~((df["city"] == "Freiburg") & (df["event_date"] < pd.to_datetime("2013-01-01")))
        & ~((df["city"] == "Bremen") & (df["event_date"] < pd.to_datetime("2019-01-01")))
        & ~((df["city"] == "Dresden") & (df["event_date"] < pd.to_datetime("2020-07-01")))
        & ~((df["city"] == "Köln") & (df["event_date"] < pd.to_datetime("2018-01-01")))
        & ~((df["city"] == "Magdeburg") & (df["event_date"] < pd.to_datetime("2015-01-01")))
        & ~((df["city"] == "Erfurt") & (df["event_date"] < pd.to_datetime("2012-01-01")))
    ]
    # remove weird dates
    df = df[
        (df["event_date"] < pd.to_datetime("2023-01-01"))
        & (df["event_date"] >= pd.to_datetime("2010-01-01"))
    ]
    return df


@cache
def parse_participant_numbers(df, column):
    df[column] = (
        df[column]
        .astype(str)
        .str.lower()
        .str.replace(r"\.0$", "", regex=True)
        .str.replace(r"\.", "", regex=True)
        .str.replace(r"^(ca|max|mind|bis zu|bis|unter|<|)|\+|plus|-$", "", regex=True)
        .str.strip()
        .str.replace(r"^(.*\D)?(\d+)\s*(personen|tn|menschen|teilnehm.*).*$", r"\2", regex=True)
        .str.replace(
            r"^(.*\D)?(\d+)\s*(fahrzeugen?|kfz|autos?|traktor(en)?|fahrrädern?).*$",
            r"\2",
            regex=True,
        )
        .str.replace(r"\n?neu:\s*(\d+)$", r"\1", regex=True)
        .astype(int, errors="ignore")
    )
    df[f"{column}_type"] = (
        df[column]
        .replace(r"^\d+\s*(-|–|/|bis)\s*\d+$", "SPAN", regex=True)
        .str.replace(r"^\d+$", "NUMBER", regex=True)
        .replace(
            r"^(nan|-+|\?+||/|wechselnd|offen|unbekannt|ka|nb|noch offen|keine\sangaben?|nicht angegeben|nicht bekannt|ohne)$",
            "UNK",
            regex=True,
        )
        .replace(r"^(?!SPAN|NUMBER|UNK)(.|\n)*$", r"UNPARSABLE", regex=True)
    )
    df.loc[df[f"{column}_type"] == "UNK", column] = None
    return df


@cache
def parse_participant_number_spans(df, column):
    # 150 - 200 -> 175
    def parse_span(s):
        parts = re.split(r"\s*(-|–|/|bis)\s*", s)
        if len(parts) == 3:
            return int((int(parts[0]) + int(parts[2])) / 2)
        return s

    df.loc[df[f"{column}_type"] == "SPAN", column] = (
        df.loc[df[f"{column}_type"] == "SPAN", column].astype(str).map(parse_span)
    )
    return df


def add_unparsable_participant_numbers(df, column):
    unparsable_participant_numbers = df[column][df[f"{column}_type"] == "UNPARSABLE"].tolist()
    # write the original texts of the unparsable participants to a json file
    file = "data/interim/unparsable_participant_numbers.json"
    if False:
        with open(file, "w") as f:
            json.dump(
                dict(
                    zip(unparsable_participant_numbers, [""] * len(unparsable_participant_numbers))
                ),
                f,
                indent=4,
                ensure_ascii=False,
            )
    else:
        # assume that a human has entered the correct numbers as values into the json file and read them back in
        with open(file) as f:
            unparseable_participant_numbers = json.load(f)
        df.loc[df[f"{column}_type"] == "UNPARSABLE", column] = df.loc[
            df[f"{column}_type"] == "UNPARSABLE", column
        ].update(unparseable_participant_numbers)
    return df


def process_participant_numbers(df):
    df = parse_participant_numbers(df, column="participants_registered")
    df = add_unparsable_participant_numbers(df, column="participants_registered")
    df = parse_participant_number_spans(df, column="participants_registered")
    df["participants_registered"] = df["participants_registered"].astype(float)
    df = parse_participant_numbers(df, column="participants_actual")
    df = add_unparsable_participant_numbers(df, column="participants_actual")
    df = parse_participant_number_spans(df, column="participants_actual")
    df["participants_actual"] = df["participants_actual"].astype(float)
    return df


def get_unified_dataset() -> pd.DataFrame:
    df = read_dfs()
    df = process_dates(df)
    df = process_participant_numbers(df)
    df = df.sort_values(["region", "city", "event_date"])
    return df


if __name__ == "__main__":
    df = get_unified_dataset()
    df = df[
        [
            "region",
            "city",
            "event_date",
            "organizer",
            "topic",
            "participants_registered",
            "participants_actual",
        ]
    ]
    df["event_date"] = df["event_date"].dt.strftime("%Y-%m-%d")
    df.to_csv("data/processed/german_protest_registrations.csv", index=False)
    print(df.shape)
