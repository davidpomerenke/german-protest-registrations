import pandas as pd

from german_protest_registrations.paths import data


def muenchen():
    # red color means cancelled event

    from openpyxl import load_workbook

    base_path = data / "raw/München"
    dfs = []

    # Process all XLSX files in the directory (2022.xlsx, 2023_2023.xlsx, etc.)
    for xlsx_path in sorted(base_path.glob("*.xlsx")):
        wb = load_workbook(xlsx_path, data_only=True)

        # 2023 file has different header structure (needs 5 rows skipped instead of 2)
        skiprows = 5 if '2023' in xlsx_path.name else 2

        for sheet in wb.worksheets:
            df = pd.read_excel(
                xlsx_path,
                sheet_name=sheet.title,
                engine="openpyxl",
                skiprows=skiprows,
            )
            df = df.rename(
                columns={
                    "Datum": "event_date",
                    "Datum Versammlung": "event_date",
                    "Organisation": "organizer",
                    "Thema": "topic",
                    "Örtlichkeit (ink. AKG + SKG)": "location",
                    "TN-Zahl": "participants_registered",
                    "angezeigte Teilnehmerzahl": "participants_registered",
                },
            )
            cancelled = pd.Series([
                isinstance(getattr(cell.font.color, 'rgb', None), str)
                for cell in sheet["A:A"][3:]
            ])
            df_ = df[~cancelled]
            # print(len(df), len(df_))
            dfs.append(df_)

    df = pd.concat(dfs)
    df = df[["event_date", "organizer", "topic", "location", "participants_registered"]]
    df["city"] = "München"
    df["region"] = "Bayern"
    df["is_regional_capital"] = True
    return df


if __name__ == "__main__":
    df = muenchen()
    print(df.sample(20))
