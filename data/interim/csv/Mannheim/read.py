from pathlib import Path

import pandas as pd


def mannheim():
    path = Path("data/interim/csv/Mannheim")
    dfs = []
    for file in path.glob("*.csv"):
        df = pd.read_csv(file)
        dfs.append(df)
    df = pd.concat(dfs)
    df["city"] = "Mannheim"
    return pd.DataFrame()


if __name__ == "__main__":
    df = mannheim()
    print(df.sample(10))
