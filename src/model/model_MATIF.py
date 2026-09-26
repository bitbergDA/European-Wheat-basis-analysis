import pandas as pd
from linearmodels.panel import PanelOLS
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import coint
import statsmodels.api as sm



df = pd.read_csv(r"../../data/processed/wheat_prices_defactored.csv")
df = df[df.Country != "EU"]
data_countries = df["Country"].unique()
df["time"] = pd.to_datetime(
    df["time"],
    format="%Y-%m"
)



df = df.sort_values(["Country", "time"])

df["dy"] = df.groupby("Country")["MP Market Price"].diff()
df["dx"] = df.groupby("Country")["MATIF"].diff()

df["y_lag"] = df.groupby("Country")["MP Market Price"].shift(1)
df["x_lag"] = df.groupby("Country")["MATIF"].shift(1)

df["dy_lag"] = df.groupby("Country")["dy"].shift(1)
df["dx_lag"] = df.groupby("Country")["dx"].shift(1)
df = df.set_index(["Country", "time"])


# Test if series are I(0), I(1), and cointegrated with MATIF if I(1)

def adf_test(series, regression="c"):
    series = series.dropna()

    result = adfuller(
        series,
        regression=regression,
        autolag="AIC"
    )

    return {
        "ADF statistic": result[0],
        "p-value": result[1],
        "lags": result[2],
        "nobs": result[3]
    }


results = []

for n, group in df.groupby("Country"):
    group = group.sort_values("time")

    level = adf_test(group["MP Market Price"])
    diff = adf_test(group["MP Market Price"].diff())

    results.append({
        "Country": n,
        "level_pvalue": level["p-value"],
        "diff_pvalue": diff["p-value"]
    })

results = pd.DataFrame(results)

print(results)


# Test for cointegration with MATIF
results = []

for n, group in df.groupby("Country"):
    group = group.sort_values("time").dropna(subset=["MP Market Price", "MATIF"])

    stat, pvalue, critical_values = coint(
        group["MP Market Price"],
        group["MATIF"],
        trend="c"
    )

    results.append({
        "Country": n,
        "pvalue": pvalue,
        "cointegrated": pvalue < 0.05
    })

coint_results = pd.DataFrame(results)

print(coint_results)


# Cointegration exists, run ECM

# Long term model
model = PanelOLS(
    df["MP Market Price"],
    df[["MATIF"]],
    entity_effects=True
)

res = model.fit(
    cov_type="clustered",
    cluster_entity=True
)

print(res)


beta = res.params["MATIF"]


# Dynamic model
df["ect"] = (
    df["MP Market Price"].groupby(level="Country").shift(1)
    - beta * df["MATIF"].groupby(level="Country").shift(1)
)
ecm = PanelOLS(
    df["dy"],
    df[["ect", "dx", "dx_lag"]],
    entity_effects=True
)

ecm_res = ecm.fit(
    cov_type="clustered",
    cluster_entity=True
)

print(ecm_res)






# Do for every country seperatly

# Sort panel

df = df.sort_values(["Country", "time"]).copy()


def estimate_ecm(country_data):

    d = country_data.sort_values("time").copy()

    # Long run model
    long_data = d[["MP Market Price", "MATIF"]].dropna()

    Y_long = long_data["MP Market Price"]
    X_long = sm.add_constant(long_data["MATIF"])

    long_model = sm.OLS(Y_long, X_long).fit()

    alpha = long_model.params["const"]
    beta = long_model.params["MATIF"]

    # Residuals
    d["ECT"] = (
        d["MP Market Price"]
        - alpha
        - beta * d["MATIF"]
    )

    # LAGGAD ECT
    d["ECT_lag1"] = d["ECT"].shift(1)
    d["d_MP"] = d["MP Market Price"].diff()
    d["d_MATIF"] = d["MATIF"].diff()

    #ECM-MODELL

    short_data = d[
        ["d_MP", "ECT_lag1", "d_MATIF"]
    ].dropna()

    Y_short = short_data["d_MP"]

    X_short = sm.add_constant(
        short_data[["ECT_lag1", "d_MATIF"]]
    )

    short_model = sm.OLS(Y_short, X_short).fit()

    return long_model, short_model, d


results = {}

for country, country_data in df.groupby("Country"):

    long_model, short_model, ecm_data = estimate_ecm(
        country_data
    )

    results[country] = {
        "long_run": long_model,
        "short_run": short_model,
        "data": ecm_data
    }

summary = []

for country, result in results.items():

    long_model = result["long_run"]
    short_model = result["short_run"]

    summary.append({
        "country": country,

        # Long run
        "alpha": long_model.params["const"],
        "beta_long_run": long_model.params["MATIF"],
        "beta_pvalue": long_model.pvalues["MATIF"],

        # ECM
        "ECT": short_model.params["ECT_lag1"],
        "ECT_pvalue": short_model.pvalues["ECT_lag1"],
        "d_MATIF": short_model.params["d_MATIF"],
        "d_MATIF_pvalue": short_model.pvalues["d_MATIF"],

        "R2_long": long_model.rsquared,
        "R2_short": short_model.rsquared
    })

results_df = pd.DataFrame(summary)

print(results_df[["country","ECT"]].sort_values(by="ECT"))
df_save = results_df[["country","ECT"]].sort_values(by="ECT")



df_save.to_csv(r'..\..\data\processed\results_MATIF.csv')
