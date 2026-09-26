import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Configuration
FLOWS_FILE = r"../../data/processed/wheat_imports.csv"
WEIGHT_VAR = "quantity_tonnes"
YEARS = None
NORMALISE = "row"

# Geography: COUNTRIES capitals (lat, lon)

CAPITALS = {
    "AT": (48.2082, 16.3738), "BG": (42.6977, 23.3219),
    "CY": (35.1856, 33.3823), "CZ": (50.0755, 14.4378), "DE": (52.5200, 13.4050),
    "EE": (59.4370, 24.7536), "ES": (40.4168, -3.7038),
    "FI": (60.1699, 24.9384), "FR": (48.8566, 2.3522),  "GR": (37.9838, 23.7275),
    "HU": (47.4979, 19.0402), "IE": (53.3498, -6.2603),
    "IT": (41.9028, 12.4964), "LT": (54.6872, 25.2797), "LU": (49.6116, 6.1319),
    "LV": (56.9496, 24.1052), "MT": (35.8989, 14.5146),
    "PL": (52.2297, 21.0122), "PT": (38.7223, -9.1393), "RO": (44.4268, 26.1025),
    "SE": (59.3293, 18.0686), "SI": (46.0569, 14.5058), "SK": (48.1486, 17.1077),
}
COUNTRIES = list(CAPITALS.keys())

ADJACENCY = {
    "AT": {"DE", "CZ", "SK", "HU", "SI", "IT"},
    "BG": {"RO", "GR"},
    "CY": set(),
    "CZ": {"DE", "AT", "SK", "PL"},
    "DE": {"PL", "CZ", "AT", "FR", "LU"},
    "EE": {"LV"},
    "ES": {"FR", "PT"},
    "FI": {"SE"},
    "FR": {"LU", "DE", "ES", "IT"},
    "GR": {"BG"},
    "HU": {"AT", "SK", "RO", "SI"},
    "IE": set(),
    "IT": {"FR", "AT", "SI"},
    "LT": {"LV", "PL"},
    "LU": {"FR", "DE"},
    "LV": {"EE", "LT"},
    "MT": set(),
    "PL": {"DE", "CZ", "SK", "LT"},
    "PT": {"ES"},
    "RO": {"BG", "HU"},
    "SE": {"FI"},
    "SI": {"AT", "IT", "HU"},
    "SK": {"CZ", "AT", "HU", "PL"},
}

# Navigable river systems relevant to bulk grain barge transport.
RHINE = {"DE", "FR", "LU"}
DANUBE = {"AT", "DE", "SK", "HU", "RO", "BG"}
LANDLOCKED = {"AT", "CZ", "HU", "LU", "SK"}

def haversine_km(a: str, b: str) -> float:
    lat1, lon1 = np.radians(CAPITALS[a])
    lat2, lon2 = np.radians(CAPITALS[b])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(h))


def build_geo_table() -> pd.DataFrame:
    """All ordered pairs i != j with distance + friction covariates."""
    rows = []
    for i in COUNTRIES:
        for j in COUNTRIES:
            if i == j:
                continue
            rows.append({
                "reporter": i,
                "partner": j,
                "dist_km": haversine_km(i, j),
                "contig": int(j in ADJACENCY[i]),
                "river": int((i in RHINE and j in RHINE) or
                            (i in DANUBE and j in DANUBE)),
                "coastal": int(i not in LANDLOCKED and j not in LANDLOCKED),
            })
    geo = pd.DataFrame(rows)
    geo["log_dist"] = np.log(geo["dist_km"])
    return geo


def load_avg_flows(path: str, years) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"reporter": str, "partner": str,
                                  "time_period": int})
    df = df[df["reporter"].isin(COUNTRIES) & df["partner"].isin(COUNTRIES)]
    df = df[df["reporter"] != df["partner"]]
    if years is not None:
        df = df[df["time_period"].isin(list(years))]
    return (df.groupby(["reporter", "partner"], as_index=False)[WEIGHT_VAR]
              .mean()
              .rename(columns={WEIGHT_VAR: "flow"}))


def fit_gravity(panel: pd.DataFrame):
    panel = panel.copy()
    panel["pair_id"] = panel.apply(
        lambda r: "-".join(sorted([r["reporter"], r["partner"]])), axis=1)

    model = smf.glm(
        "flow ~ log_dist + contig + river + coastal + C(reporter) + C(partner)",
        data=panel, family=sm.families.Poisson(),
    )
    result = model.fit(cov_type="cluster", cov_kwds={"groups": panel["pair_id"]})
    return result


def friction_index(result, geo: pd.DataFrame) -> pd.DataFrame:
    b = result.params
    lin = (b["log_dist"] * geo["log_dist"]
           + b["contig"] * geo["contig"]
           + b["river"] * geo["river"]
           + b["coastal"] * geo["coastal"])
    geo = geo.copy()
    geo["friction"] = np.exp(lin)
    M = (geo.pivot(index="reporter", columns="partner", values="friction")
            .reindex(index=COUNTRIES, columns=COUNTRIES)
            .fillna(0.0))
    arr = np.array(M.to_numpy(), copy=True)   # force a writable buffer
    np.fill_diagonal(arr, 0.0)
    M = pd.DataFrame(arr, index=M.index, columns=M.columns)
    return M


def normalise(M: pd.DataFrame, how: str | None) -> pd.DataFrame:
    X = M.to_numpy(dtype=float).copy()
    if how == "row":
        rs = X.sum(axis=1, keepdims=True)
        X = np.divide(X, rs, out=np.zeros_like(X), where=rs > 0)
    elif how == "spectral":
        lam = np.max(np.abs(np.linalg.eigvals(X)))
        if lam > 0:
            X = X / lam
    elif how == "doubly":
        for _ in range(500):
            rs = X.sum(axis=1, keepdims=True)
            X = np.divide(X, rs, out=np.zeros_like(X), where=rs > 0)
            cs = X.sum(axis=0, keepdims=True)
            X = np.divide(X, cs, out=np.zeros_like(X), where=cs > 0)
    return pd.DataFrame(X, index=M.index, columns=M.columns)


def report(result) -> None:
    print(result.summary())
    b, se = result.params, result.bse
    print("\nFriction terms (expect: dist < 0, contig/river/coastal > 0):")
    for term in ["log_dist", "contig", "river", "coastal"]:
        z = b[term] / se[term]
        print(f"  {term:10s} beta={b[term]:+.3f}  se={se[term]:.3f}  z={z:+.2f}")


if __name__ == "__main__":
    geo = build_geo_table()
    avg_flow = load_avg_flows(FLOWS_FILE, YEARS)

    panel = geo.merge(avg_flow, on=["reporter", "partner"], how="left")
    panel["flow"] = panel["flow"].fillna(0.0)   # true zero, not missing

    result = fit_gravity(panel)
    report(result)

    raw = friction_index(result, geo)
    W = normalise(raw, NORMALISE)

    raw.to_csv(r"../../data/raw/W_gravity_raw.csv")
    W.to_csv(r"../../data/processed/W_gravity.csv")

    check = panel[panel["flow"] > 0].copy()
    check["friction"] = raw.stack().reindex(
        pd.MultiIndex.from_frame(check[["reporter", "partner"]])).values
    rho = check[["flow", "friction"]].corr(method="spearman").iloc[0, 1]
    print(f"Spearman corr on nonzero pairs: {rho:.3f}")