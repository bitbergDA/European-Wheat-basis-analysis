import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#Import data
df = pd.read_csv(r'../../data/raw/market-prices-vegetal-products_en.csv')
df = df[df["Product code"] == "BLTPAN"]
df["time"] = pd.to_datetime(df["Period"], format="%Y%m").dt.to_period("M")
df = df.sort_values("time")


# Check missing values
all_combinations = pd.MultiIndex.from_product(
    [df["Country"].unique(), df["time"].unique()],
    names=["Country", "time"]
)

existing = pd.MultiIndex.from_frame(df[["Country", "time"]].drop_duplicates())

missing = all_combinations.difference(existing)
missing = missing.to_frame(index=False)

df = pd.concat([df, missing], ignore_index=True)
missing_summary = (
    df.groupby("Country")
    .agg(
        missing_count=("MP Market Price", lambda x: x.isna().sum()),
        most_recent_missing=("time", lambda x: x[df.loc[x.index, "MP Market Price"].isna()].max())
    )
)

print(missing_summary)


# Plot missing values


missing = (
    df
    .assign(missing=df["MP Market Price"].isna())
    .pivot(index="Country", columns="time", values="missing")
)

plt.figure(figsize=(15, 8))
sns.heatmap(missing, cmap=["white", "red"], cbar=False)

plt.xlabel("Period")
plt.ylabel("Country")
plt.title("Missing values over time")
plt.tight_layout()
plt.show()

# Filter out data with too much missing values
df = df[df['time'] > '2004-12']
df = df[~df["Country"].isin(["DK", "NL", "BE", "HR"])]

# Acceptable amount to fill missing values
df["MP Market Price"] = df.groupby("Country")["MP Market Price"].transform(
    lambda x: x.ffill().bfill()
)

# Save only relevant variables
df = df[["Country", "time", "MP Market Price"]]

df.to_csv(r"../../data/processed/df.csv", index=False)


