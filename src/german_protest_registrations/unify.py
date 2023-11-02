from os import sys

from tqdm import tqdm

sys.path.append("data/interim/csv")
from Augsburg.read import augsburg


def main():
    df_readers = [augsburg]
    dfs = []
    for df_reader in tqdm(df_readers):
        dfs += df_reader()
    for df in dfs:
        print(df.head())


if __name__ == "__main__":
    main()
