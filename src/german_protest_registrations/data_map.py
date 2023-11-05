# title: Map of data avilability in the German Protest Registrations Dataset
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib_inline.backend_inline import set_matplotlib_formats

from german_protest_registrations.data_description import overview_table
from german_protest_registrations.paths import data

# | label: data-official-map
# | fig-cap: 'Map of official data. Blue = data including the number of registered protesters is available for the political capital of the region; gray-blue = some other data is available, e. g. without protester numbers or only for other cities than the capital; gray = no data is available or the data is so unstructured that it is not included in the dataset.'
# | column: margin


def has_data(x, df):
    return df[(df["region"] == x) & (df["22"] > 0)].size > 0


def has_good_data(x, df):
    return (
        df[
            (df["region"] == x)
            & (df["22"] > 0)
            & (df["capital"] == True)
            & (df["registrations"] == True)
        ].size
        > 0
    )
    return any(
        [
            a
            for a in df.iterrows()
            if a[1]["region"] == x and df.loc[a, "cap?"] == "✓" and df.loc[a, "#reg?"] == "✓"
        ]
    )


def get_map():
    df = overview_table().reset_index()
    # load administrative boundaries:

    gdf = gpd.read_file(data / "external/diva-gis/DEU_adm1.shp")
    gdf = gdf.to_crs("EPSG:4326")
    gdf["color"] = gdf["NAME_1"].apply(
        lambda x: "blue"
        if has_data(x, df) and has_good_data(x, df)
        else ("steelblue" if has_data(x, df) else "lightgray")
    )
    gdf["color"] = gdf["color"].astype("category")
    gdf["color"] = gdf["color"].cat.set_categories(["lightgray", "steelblue", "blue"])

    # plot:

    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(ax=ax, color=gdf["color"], edgecolor="black", linewidth=0.5)
    ax.set_axis_off()
    legend_elements = [
        Patch(facecolor="lightgray", edgecolor="black", label="No data"),
        Patch(facecolor="steelblue", edgecolor="black", label="Some data"),
        Patch(facecolor="blue", edgecolor="black", label="Good data"),
    ]
    ax.legend(
        handles=legend_elements,
        loc="lower center",
        ncol=3,
        bbox_to_anchor=(0.5, -0.05),
        frameon=False,
        fontsize=14,
    )
    return fig, ax


if __name__ == "__main__":
    fig, ax = get_map()
    set_matplotlib_formats("png")
    plt.savefig("reports/data-official-map.png", bbox_inches="tight")
