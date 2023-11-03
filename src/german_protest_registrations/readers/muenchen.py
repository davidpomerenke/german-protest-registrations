import pandas as pd


def muenchen():
    # red color means cancelled event

    from openpyxl import load_workbook

    path = "data/raw/München/2022.xlsx"
    wb = load_workbook(path, data_only=True)

    dfs = []
    for sheet in wb.worksheets:
        df = pd.read_excel(
            path,
            sheet_name=sheet.title,
            engine="openpyxl",
            skiprows=2,
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
        cancelled = pd.Series([isinstance(cell.font.color.rgb, str) for cell in sheet["A:A"][3:]])
        df_ = df[~cancelled]
        # print(len(df), len(df_))
        dfs.append(df_)
    df = pd.concat(dfs)
    df = df[["event_date", "organizer", "topic", "location", "participants_registered"]]
    df["city"] = "München"
    return df


if __name__ == "__main__":
    df = muenchen()
    print(df.sample(20))
