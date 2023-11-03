import warnings

import pandas as pd
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

warnings.filterwarnings("ignore", module="dateparser")


def main():
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
    ]
    dfs = {read.__name__: read() for read in tqdm(df_readers, mininterval=1)}
    for name, df in dfs.items():
        # detect duplicate columns
        duplicates = df.columns.duplicated()
        if duplicates.any():
            print(f"Duplicate columns in {name}: {df.columns[duplicates]}")
        # detect duplicate rows
        duplicates = df.duplicated()
        if duplicates.any():
            print(f"Duplicate rows in {name} ({len(df[duplicates])} rows): {df[duplicates]}")
    df = pd.concat(dfs, ignore_index=True)
    df.to_csv("data/processed/german_protest_registrations.csv", index=False)
    print(df.shape)


if __name__ == "__main__":
    main()
