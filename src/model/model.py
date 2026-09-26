import pandas as pd
import scipy.sparse as spar
from linearmodels.panel import PanelOLS
from statsmodels.tsa.stattools import adfuller
import numpy as np
from scipy.stats import spearmanr
from statsmodels.stats.diagnostic import acorr_breusch_godfrey

W = pd.read_csv(r"../../data/processed/W_gravity.csv")
W = W.set_index("reporter")
W.index = W.index.str.replace("GR", "EL")
W.columns = W.columns.str.replace("GR", "EL")
assert set(W.index) == set(W.columns)

df = pd.read_csv(r"../../data/processed/wheat_prices_defactored.csv")
df = df[df.Country != "EU"]
data_countries = df["Country"].unique()
print(data_countries)

extra = W.index.difference(data_countries)
W = W.drop(index=extra, columns=extra)
df = df.sort_values(by=["time", "Country"])
df['idio_price'] = pd.to_numeric(df['idio_price'], errors='coerce')
df = df.dropna()

# Align together
w_order = W.index.tolist()
W_sparse = spar.csr_matrix(W.values)

lagged_results = []
for time_step, group in df.groupby('time'):
    group_indexed = group.set_index('Country')
    aligned_group = group_indexed.reindex(w_order)
    y_vector = aligned_group['idio_price'].fillna(0).astype(float).values
    W_y_vector = W_sparse @ y_vector
    lagged_df = pd.DataFrame({'Country': w_order, 'time': time_step, 'W_y': W_y_vector})
    lagged_results.append(lagged_df)

spatial_lags_df = pd.concat(lagged_results, ignore_index=True)

panel_df = df.drop(columns=['MATIF', 'MP Market Price'])
panel_df = panel_df.merge(spatial_lags_df, on=['Country', 'time'], how='left')

df = panel_df.rename(columns={"idio_price": "Y", "W_y": "X", "Country": "entity"})
df['time'] = pd.to_datetime(df['time'])
df = df.set_index(['entity', 'time'])

df["ukraine_dummy"] = (
    (df.index.get_level_values("time") >= pd.Timestamp("2022-02-01")) &
    (df.index.get_level_values("time") < pd.Timestamp("2022-03-01"))
).astype(int)

# Spatial Error-Correction Model (SpECM)
N_OWN_LAGS = 2
MIN_OBS_ADF = 60
ADF_ALPHA = 0.05

# Step 1: long-run cointegrating regression
coint_model = PanelOLS(df['Y'], df[['X']], entity_effects=True)
coint_res = coint_model.fit(cov_type='clustered', cluster_entity=True)
print(coint_res)
df['ECT'] = coint_res.resids

# Stationarity check
print("\nADF test on ECT by country:")
stationary_countries = []
for entity in df.index.get_level_values('entity').unique():
    e = df['ECT'].xs(entity, level='entity').dropna()
    if len(e) < MIN_OBS_ADF:
        print(f"  {entity}: only {len(e)} obs, skipping")
        continue
    stat, pval, *_ = adfuller(e, autolag='AIC')
    stationary = pval < ADF_ALPHA
    if stationary:
        stationary_countries.append(entity)
    print(f"  {entity}: ADF stat={stat:.3f}  p={pval:.4f}  "
          f"[{'STATIONARY' if stationary else 'non-stationary'}]")

n_entities = df.index.get_level_values('entity').nunique()


# Step 2: dynamic ECM
g = df.groupby(level='entity')
df['dY'] = g['Y'].diff()
df['dX'] = g['X'].diff()
df['ECT_lag1'] = g['ECT'].shift(1)
df['dX_lag1'] = g['dX'].shift(1)
for k in range(1, N_OWN_LAGS + 1):
    df[f'dY_lag{k}'] = g['dY'].shift(k)

lag_cols = ['ECT_lag1', 'dX_lag1'] + [f'dY_lag{k}' for k in range(1, N_OWN_LAGS + 1)]
ecm_df = df.dropna(subset=['dY'] + lag_cols + ['ukraine_dummy'])

ecm_model = PanelOLS(ecm_df['dY'], ecm_df[lag_cols + ["ukraine_dummy"]], entity_effects=True)
ecm_res = ecm_model.fit(cov_type='clustered', cluster_entity=True)
print(ecm_res)


alpha = ecm_res.params['ECT_lag1']
print(f"\nPooled alpha = {alpha:.4f}  (p={ecm_res.pvalues['ECT_lag1']:.4f})")
if -1 < alpha < 0:
    print(f"Implied half-life: {np.log(0.5) / np.log(1 + alpha):.1f} periods")
else:
    print("alpha outside the stable (-1, 0) range -- no valid half-life; "
          "check sign/magnitude before treating this as mean reversion.")


# Optional: heterogeneous alpha per country
entity_dummies = pd.get_dummies(ecm_df.index.get_level_values('entity'), prefix='ECT')
entity_dummies.index = ecm_df.index
ect_interacted = entity_dummies.multiply(ecm_df['ECT_lag1'], axis=0).astype(float)

other_cols = ['dX_lag1'] + [f'dY_lag{k}' for k in range(1, N_OWN_LAGS + 1)]
het_exog = pd.concat([ect_interacted, ecm_df[other_cols]], axis=1)
het_model = PanelOLS(ecm_df['dY'], het_exog, entity_effects=True)
het_res = het_model.fit(cov_type='clustered', cluster_entity=True)

print("\nHeterogeneous alpha per country:")
alpha_by_country = het_res.params.filter(like='ECT_')
alpha_by_country.index = alpha_by_country.index.str.replace('ECT_', '')
print(alpha_by_country.sort_values())

# Save alpha per coutry

results = alpha_by_country.sort_values()
results.to_csv(r'..\..\data\processed\results.csv')

# Save 2 countries for new project, in order to demonstrate how this knowledge can be useful
valda_entities = ['SE', 'FR']
vald_kolumn = 'ECT_lag1'

# Filter
nytt_df = df.loc[df.index.get_level_values('entity').isin(valda_entities), [vald_kolumn]]

# Save
nytt_df.to_csv(r'..\..\data\processed\filtrerad_data.csv')