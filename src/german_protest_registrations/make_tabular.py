"""Create the `tabular` directory."""

import contextlib
from pathlib import Path


def main():
    """Read all files from data/raw and if they are already tabular, create symlinks to data/interim/tabular."""
    for file in Path("data/raw").glob("*/*"):
        table_formats = [".csv", ".tsv", ".xlsx", ".xls", ".ods"]
        if file.is_file() and file.suffix in table_formats:
            with contextlib.suppress(FileExistsError):
                symlink = Path("data/interim/tabular") / file.relative_to("data/raw")
                symlink.parent.mkdir(parents=True, exist_ok=True)
                symlink.symlink_to(file.resolve())
        else:
            todo_file = Path("data/interim/tabular") / file.relative_to("data/raw").with_suffix(
                ".todo"
            )
            todo_file.parent.mkdir(parents=True, exist_ok=True)
            todo_file.touch()


if __name__ == "__main__":
    main()
