"""Create the `cleaned` directory."""

from pathlib import Path

import pandas as pd


def main():
    """Read all files from data/tabular."""
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
                    dfs = {file.stem: pd.read_csv(file, delimiter=delimiter)}
                case ".tsv":
                    dfs = {file.stem: pd.read_csv(file, delimiter="\t")}
                case ".xlsx" | ".xls":
                    dfs = pd.read_excel(file, sheet_name=None)
                    dfs = {f"{file.stem}_{k}": v for k, v in dfs.items()}
                case ".ods":
                    dfs = pd.read_excel(file, engine="odf", sheet_name=None)
                    dfs = {f"{file.stem}_{k}": v for k, v in dfs.items()}
            for name, df in dfs.items():
                if len(df) == 0:
                    continue
                folder = Path("data/interim/csv") / file.parent.stem
                folder.mkdir(parents=True, exist_ok=True)
                df.to_csv(folder / f"{name}.csv", index=False)


if __name__ == "__main__":
    main()
