from time import sleep

import pandas as pd
import qwikidata.sparql
from dotenv import load_dotenv

from german_protest_registrations.unify import cache, get_unified_dataset

load_dotenv()

german_regions = [
    {"name": "Baden-Württemberg", "capital": "Stuttgart"},
    {"name": "Bayern", "capital": "München"},
    {"name": "Berlin", "capital": "Berlin"},
    {"name": "Brandenburg", "capital": "Potsdam"},
    {"name": "Bremen", "capital": "Bremen"},
    {"name": "Hamburg", "capital": "Hamburg"},
    {"name": "Hessen", "capital": "Wiesbaden"},
    {"name": "Mecklenburg-Vorpommern", "capital": "Schwerin"},
    {"name": "Niedersachsen", "capital": "Hannover"},
    {"name": "Nordrhein-Westfalen", "capital": "Düsseldorf"},
    {"name": "Rheinland-Pfalz", "capital": "Mainz"},
    {"name": "Saarland", "capital": "Saarbrücken"},
    {"name": "Sachsen", "capital": "Dresden"},
    {"name": "Sachsen-Anhalt", "capital": "Magdeburg"},
    {"name": "Schleswig-Holstein", "capital": "Kiel"},
    {"name": "Thüringen", "capital": "Erfurt"},
]


@cache
def get_population(city, region, country="Deutschland"):
    sleep(1)
    if city == "Freiburg":
        city = "Freiburg im Breisgau"
    query = f"""
    SELECT ?city ?cityLabel ?country ?countryLabel ?population
    WHERE
    {{
      ?city rdfs:label "{city}"@de.
      ?city wdt:P1082 ?population.
      ?city wdt:P17 ?country.
      ?city rdfs:label ?cityLabel.
      ?country rdfs:label ?countryLabel.
      FILTER(LANG(?cityLabel) = "de").
      FILTER(LANG(?countryLabel) = "de").
      FILTER(CONTAINS(?countryLabel, "{country}")).
    }}
    """
    res = qwikidata.sparql.return_sparql_query_results(query)
    out = res["results"]["bindings"][0]
    pop = int(out["population"]["value"])
    return pop


def is_capital(city, region):
    return city == [r["capital"] for r in german_regions if r["name"] == region][0]


def overview_table():
    df = get_unified_dataset()
    df["year"] = df["event_date"].dt.year.astype(str).apply(lambda x: x[-2:])
    agg_df = df.groupby(["region", "city", "year"]).size().unstack().fillna(0).astype(int)
    # add column to agg_df whether or not the "Teilnehmer" column is available
    agg_df["registrations"] = df.groupby(["region", "city"]).apply(
        lambda x: x["participants_registered"].mean() > 10
    )
    agg_df["observations"] = df.groupby(["region", "city"]).apply(
        lambda x: x["participants_actual"].mean() > 10
    )

    agg_df["capital"] = agg_df.apply(lambda x: is_capital(x.name[1], x.name[0]), axis=1)
    agg_df["kpop"] = agg_df.apply(lambda x: get_population(x.name[1], x.name[0]), axis=1)
    return agg_df


def pretty_overview_table(symbol="✓"):
    # symbol: "✓" or "x"
    df = overview_table()
    # calculate sums row (add later)
    sums = df.sum(numeric_only=False)
    sums.name = ("", "sum", "")
    # insert empty rows for regions that are not in the data
    for region in german_regions:
        if region["name"] not in df.index:
            df.loc[(region["name"], "–"), :] = ""
            df.loc[(region["name"], "–"), "kpop"] = "–"
    # sort by region name
    df = df.sort_index()
    # add sum row at the bottom
    df = pd.concat([df, sums.to_frame().T])
    df["#reg?"] = df["registrations"].replace({0: " ", 1: symbol})
    df["#obs?"] = df["observations"].replace({0: " ", 1: symbol})
    df["cap?"] = df["capital"].replace({0: " ", 1: symbol})
    df["kpop"] = df["kpop"].apply(lambda x: f"{int(x/1000):,}" if x not in ["–", ""] else x)
    years = [col for col in df.columns if col.isnumeric()]
    for col in years:
        df[col] = df[col].apply(lambda x: f"{int(x):,}" if x != "" else "")
    df = df.replace(0, "")
    df = df.replace("0", "")
    # reorder columns
    df = df[["kpop", "cap?", "#reg?", "#obs?", *years]]
    df = df.rename(index={"Mecklenburg-Vorpommern": "Meck.-Vorpommern"})
    df = df.reset_index().rename(columns={"level_0": "region", "level_1": "city"})
    df = df.rename_axis(None, axis=1)
    return df


if __name__ == "__main__":
    print(overview_table())
    print(pretty_overview_table())
