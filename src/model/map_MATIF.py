import pandas as pd
import plotly.express as px

# --- Configuration -----------------------------------------------------------
RESULTS_FILE = r'..\..\data\processed\results_MATIF.csv'

COUNTRY_INFO = {
    "AT": ("Austria", "AUT"), "BE": ("Belgium", "BEL"), "BG": ("Bulgaria", "BGR"),
    "CY": ("Cyprus", "CYP"), "CZ": ("Czechia", "CZE"), "DE": ("Germany", "DEU"),
    "DK": ("Denmark", "DNK"), "EE": ("Estonia", "EST"), "ES": ("Spain", "ESP"),
    "FI": ("Finland", "FIN"), "FR": ("France", "FRA"),
    "GR": ("Greece", "GRC"), "EL": ("Greece", "GRC"),
    "HR": ("Croatia", "HRV"), "HU": ("Hungary", "HUN"), "IE": ("Ireland", "IRL"),
    "IT": ("Italy", "ITA"), "LT": ("Lithuania", "LTU"), "LU": ("Luxembourg", "LUX"),
    "LV": ("Latvia", "LVA"), "NL": ("Netherlands", "NLD"),
    "PL": ("Poland", "POL"), "PT": ("Portugal", "PRT"), "RO": ("Romania", "ROU"),
    "SE": ("Sweden", "SWE"), "SI": ("Slovenia", "SVN"), "SK": ("Slovakia", "SVK"),
}



alpha_df = pd.read_csv(RESULTS_FILE)
alpha_df = alpha_df.rename(columns={
    "country": "code",
    "ECT": "alpha"
})
def build_map_df(alpha_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    unmatched = []
    for _, row in alpha_df.iterrows():
        info = COUNTRY_INFO.get(row["code"])
        name, iso3 = info
        rows.append({"code": row["code"], "country": name, "iso3": iso3,
                 "alpha": row["alpha"]})
    return pd.DataFrame(rows)


def make_map(map_df: pd.DataFrame, out_prefix: str = "alpha_map"):
    mean_alpha = map_df["alpha"].mean()
    max_dev = map_df["alpha"].sub(mean_alpha).abs().max()

    fig = px.choropleth(
        map_df,
        locations="iso3",
        color="alpha",
        hover_name="country",
        hover_data={"iso3": False, "alpha": ":.3f"},
        color_continuous_scale="RdYlGn_r",   # red = slow, green = fast
        range_color=(mean_alpha - max_dev, mean_alpha + max_dev),
        color_continuous_midpoint=mean_alpha,
        scope="europe",
        title="Spatial ECM reversion speed (alpha) by country",
        labels={"alpha": "alpha (ECT_lag1)"},
    )
    fig.update_geos(
        showcountries=True, countrycolor="lightgray",
        lataxis_range=[33, 71], lonaxis_range=[-11, 32],
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        coloraxis_colorbar=dict(title="alpha"),
    )
    try:
        fig.write_image(f"..\output\{out_prefix}_MATIF.png", scale=2, width=900, height=700)
        print(f"wrote ..\output\{out_prefix}.png")
    except Exception as e:
        print(f"(static PNG export skipped -- {e}; "
              f"run 'pip install -U kaleido' if you want a PNG too)")

    return fig


if __name__ == "__main__":
    map_df = build_map_df(alpha_df)
    print(map_df.sort_values("alpha"))
    make_map(map_df)
