import os
from dotenv import load_dotenv
import io
import time
import requests
import pandas as pd


load_dotenv()
BASE = os.getenv("EUROSTAT_URL")
DATASET = "DS-045409"
EU27 = [
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR",
    "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO",
    "SE", "SI", "SK",
]
REPORTERS = EU27
PARTNERS = EU27
PRODUCT = "1001"
FREQ = "A"
FLOW = "1"
INDICATORS = "VALUE_IN_EUROS+QUANTITY_IN_100KG"
START_PERIOD = "2005"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "intra-eu-wheat-imports/1.0"})


def build_url(reporter: str, partners: list[str]) -> str:
    partner_key = "+".join(p for p in partners if p != reporter)
    key = f"{FREQ}.{reporter}.{partner_key}.{PRODUCT}.{FLOW}.{INDICATORS}"
    return f"{BASE}/{DATASET}/{key}"


def fetch_reporter(reporter: str, retries: int = 3) -> pd.DataFrame:
    url = build_url(reporter, PARTNERS)
    params = {"format": "SDMX-CSV", "startPeriod": START_PERIOD}

    for attempt in range(retries):
        r = SESSION.get(url, params=params, timeout=180)

        if r.status_code == 200:
            if r.text.lstrip().startswith("<"):
                print(f"  {reporter}: server returned XML (queued or fault)")
                print(f"  {r.text[:400]}")
                return pd.DataFrame()
            return pd.read_csv(io.StringIO(r.text), dtype=str)

        if r.status_code == 413:
            raise RuntimeError(
                f"{reporter}: EXTRACTION_TOO_BIG - narrow the filters. {r.text[:300]}"
            )
        if r.status_code in (429, 500, 502, 503, 504):
            wait = 10 * (attempt + 1)
            print(f"  {reporter}: HTTP {r.status_code}, retrying in {wait}s")
            time.sleep(wait)
            continue

        raise RuntimeError(f"{reporter}: HTTP {r.status_code} - {r.text[:300]}")

    return pd.DataFrame()


def main() -> pd.DataFrame:
    frames = []
    for i, reporter in enumerate(REPORTERS, 1):
        print(f"[{i}/{len(REPORTERS)}] {reporter}")
        df = fetch_reporter(reporter)
        if not df.empty:
            frames.append(df)
        time.sleep(2)          # serial requests only - do not parallelise

    if not frames:
        raise SystemExit("No data returned.")

    data = pd.concat(frames, ignore_index=True)
    data.columns = [c.lower() for c in data.columns]

    # Long -> tidy: one row per reporter/partner/product/year, indicators as columns
    idx = [c for c in ["reporter", "partner", "product", "flow", "time_period"]
           if c in data.columns]
    tidy = (
        data.pivot_table(index=idx, columns="indicators",
                         values="obs_value", aggfunc="first")
        .reset_index()
        .rename(columns={"value_in_euros": "value_eur",
                         "quantity_in_100kg": "quantity_100kg",
                         "VALUE_IN_EUROS": "value_eur",
                         "QUANTITY_IN_100KG": "quantity_100kg"})
    )
    for col in ("value_eur", "quantity_100kg"):
        if col in tidy.columns:
            tidy[col] = pd.to_numeric(tidy[col], errors="coerce")
    if "quantity_100kg" in tidy.columns:
        tidy["quantity_tonnes"] = tidy["quantity_100kg"] / 10.0

    tidy.to_csv(r"../../data/processed/wheat_imports.csv", index=False)
    print(f"\nSaved {len(tidy):,} rows to intra_eu_wheat_imports.csv")
    return tidy


if __name__ == "__main__":
    out = main()
    print(out.head(20).to_string(index=False))

