"""Create the `cleaned` directory."""

from collections import defaultdict
from pathlib import Path

import pandas as pd


def main():
    """Read all files from data/tabular."""
    dfs = defaultdict(list)
    for file in Path("data/raw").glob("*/*"):
        table_formats = [".csv", ".tsv", ".xlsx", ".xls", ".ods"]
        print(file.absolute())
        if file.suffix in table_formats:
            match file.suffix:
                case ".csv":
                    # detect which delimiter is used
                    delimiter = None
                    with file.open() as f:
                        first_line = f.readline()
                        if "\t" in first_line:
                            delimiter = "\t"
                        elif ";" in first_line:
                            delimiter = ";"
                        elif "," in first_line:
                            delimiter = ","
                    if delimiter is None:
                        raise ValueError(f"Could not detect delimiter for {file}")
                    # read file
                    dfs_ = [pd.read_csv(file, delimiter=delimiter)]
                case ".tsv":
                    dfs_ = [pd.read_csv(file, delimiter="\t")]
                case ".xlsx" | ".xls":
                    # read every sheet
                    dic = pd.read_excel(file, sheet_name=None)
                    dfs_ = list(dic.values())
                case ".ods":
                    dic = pd.read_excel(file, engine="odf", sheet_name=None)
                    dfs_ = list(dic.values())
            dfs[file.parent.name].extend(dfs_)
    print([(k, len(v)) for k, v in dfs.items()])


if __name__ == "__main__":
    main()
