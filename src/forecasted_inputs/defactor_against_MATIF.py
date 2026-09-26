import numpy as np
import pandas as pd
import statsmodels.api as sm

INFILE = r"../../data/processed/df.csv"

df = pd.read_csv(INFILE)


matif = pd.read_csv(r"../../data/raw/Milling Wheat N2 Futures Historical Data (2).csv")

matif["Date"] = pd.to_datetime(matif["Date"], format="%m/%d/%Y")
matif["Date"] = matif["Date"].dt.strftime("%Y-%m")

matif = matif.rename(columns = { "Date":"time",
                                 "Price":"MATIF"})
matif = matif[['time', 'MATIF']]
merged = df.merge(
    matif,
    on="time",
    how="left"
)


merged['idio_price'] = merged['MP Market Price'] - merged['MATIF']

print(merged)

merged.to_csv(r"../../data/processed/wheat_prices_defactored.csv", index=False)