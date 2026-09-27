import pandas as pd
import scipy.sparse as spar
from linearmodels.panel import PanelOLS
from statsmodels.tsa.stattools import adfuller

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

MIN_OBS_ADF = 60
ADF_ALPHA = 0.05

USE_LAG = False

print("\nADF test on Y directly, by country:")
stationary_countries = []
for entity in df.index.get_level_values('entity').unique():
    y = df['Y'].xs(entity, level='entity').dropna()
    if len(y) < MIN_OBS_ADF:
        print(f"  {entity}: only {len(y)} obs, skipping")
        continue
    stat, pval, *_ = adfuller(y, autolag='AIC')
    stationary = pval < ADF_ALPHA
    if stationary:
        stationary_countries.append(entity)
    print(f"  {entity}: ADF stat={stat:.3f}  p={pval:.4f}  "
          f"[{'STATIONARY' if stationary else 'non-stationary'}]")

if USE_LAG:
    df['X_used'] = df.groupby(level='entity')['X'].shift(1)
else:
    df['X_used'] = df['X']

model_df = df.dropna(subset=['Y', 'X_used', 'ukraine_dummy'])

# --- pooled panel FE model
pooled_model = PanelOLS(model_df['Y'], model_df[['X_used', 'ukraine_dummy']],
                        entity_effects=True)
pooled_res = pooled_model.fit(cov_type='clustered', cluster_entity=True)
print(pooled_res)
print(f"\npooled beta = {pooled_res.params['X_used']:.4f}  "
      f"(p={pooled_res.pvalues['X_used']:.4f})")

# --- country-specific beta 
entity_dummies = pd.get_dummies(model_df.index.get_level_values('entity'), prefix='ENT')
entity_dummies.index = model_df.index
x_interacted = entity_dummies.multiply(model_df['X_used'], axis=0).astype(float)

het_exog = pd.concat([x_interacted, model_df[['ukraine_dummy']]], axis=1)
het_model = PanelOLS(model_df['Y'], het_exog, entity_effects=True)
het_res = het_model.fit(cov_type='clustered', cluster_entity=True)
print(het_res)

beta_by_country = het_res.params.filter(like='ENT_')
beta_by_country.index = beta_by_country.index.str.replace('ENT_', '').str.replace('_X_used', '')
beta_by_country = beta_by_country.sort_values()

print("\nCountry-specific beta:")
print(beta_by_country)

beta_by_country.to_csv(r"..\..\data\processed\results_panel_fe.csv")
