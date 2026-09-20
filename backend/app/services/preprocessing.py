"""
Data preprocessing service.

Responsibilities:
  1. Accept a raw pandas DataFrame from the upload service.
  2. Detect and map relevant column names (case-insensitive).
  3. Parse timestamps.
  4. Drop exact duplicates.
  5. Handle missing values (forward-fill then drop).
  6. Remove physically impossible negative values.
  7. Report preprocessing statistics back to the caller.
  8. Return a clean DataFrame ready for ML ingestion.

Column normalisation strategy
──────────────────────────────
Real-world CPCB / OpenCity CSVs use names like:
  "PM2.5 (ug/m3)", "PM10 (ug/m3)", "Ozone (ug/m3)", "CO (mg/m3)" …

The normaliser:
  1. Lowercases the raw name.
  2. Strips parenthetical unit suffixes:  (ug/m3), (mg/m3), (µg/m³) etc.
  3. Strips all non-alphanumeric characters.
This turns "PM2.5 (ug/m3)" → "pm25" and "Ozone (ug/m3)" → "ozone",
which then matches the synonym lists below.
"""

import re
import logging
from typing import Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# ── Column name synonyms ──────────────────────────────────────────────────────
# Each key is the canonical internal name.
# Each value is a list of *normalised* synonyms (after _normalize_colname()).
# Add new synonyms here — nowhere else — to support additional data sources.
COLUMN_SYNONYMS: dict[str, list[str]] = {
    # ── Timestamp ──────────────────────────────────────────────────────────
    "timestamp": [
        "timestamp", "datetime", "date_time", "date", "time",
        "recorded_at", "measured_at",
        # CPCB / OpenCity
        "from_date", "fromdate", "to_date", "todate",
        "samplingdate", "sampling_date", "obs_date",
    ],
    # ── Location ───────────────────────────────────────────────────────────
    "location": [
        "location", "station", "site", "city", "area",
        # CPCB / OpenCity
        "station_name", "stationname", "station_id", "stationid",
        "state", "site_name", "sitename",
    ],
    # ── PM2.5 ──────────────────────────────────────────────────────────────
    "pm25": [
        "pm25", "pm2_5", "fine_particles",
        # e.g. "PM2.5" → normalised "pm25" (dots stripped)
        # e.g. "PM2.5 (ug/m3)" → normalised "pm25" (units stripped)
        # e.g. "pm2.5_conc", "pm25_conc"
        "pm25_conc", "pm2_5_conc",
        "fineparticles", "fine_particulate_matter",
    ],
    # ── PM10 ───────────────────────────────────────────────────────────────
    "pm10": [
        "pm10", "pm_10", "coarse_particles",
        "pm10_conc",
        "coarseparticles", "coarse_particulate_matter",
    ],
    # ── NO2 ────────────────────────────────────────────────────────────────
    "no2": [
        "no2", "nitrogen_dioxide", "nitrogendioxide",
        "no2_conc",
    ],
    # ── CO ─────────────────────────────────────────────────────────────────
    "co": [
        "co", "carbon_monoxide", "carbonmonoxide",
        "co_conc",
    ],
    # ── SO2 ────────────────────────────────────────────────────────────────
    "so2": [
        "so2", "sulphur_dioxide", "sulfur_dioxide",
        "sulphurdioxide", "sulfurdioxide",
        "so2_conc",
    ],
    # ── O3 / Ozone ─────────────────────────────────────────────────────────
    "o3": [
        "o3", "ozone",
        "o3_conc", "ozone_conc",
    ],
    # ── Meteorological (optional) ──────────────────────────────────────────
    "temperature": [
        "temperature", "temp", "temp_c", "temperature_c",
        "at", "air_temp", "airtemp",
    ],
    "humidity": [
        "humidity", "relative_humidity", "rh", "humidity_pct",
        "rh_pct",
    ],
    "wind_speed": [
        "wind_speed", "windspeed", "wind", "ws",
        "wind_speed_ms", "ws_ms",
    ],
}

# Columns that must have at least one present for the pipeline to work
REQUIRED_POLLUTANT_COLS = {"pm25", "pm10", "no2", "co", "so2", "o3"}

# Regex that matches parenthetical unit suffixes:
#   (ug/m3)  (µg/m3)  (mg/m3)  (ug/m³)  (ppb)  (ppm)  etc.
_UNIT_SUFFIX_RE = re.compile(r"\s*\([^)]*\)\s*$")


def _normalize_colname(name: str) -> str:
    """
    Normalise a raw CSV column name for synonym matching.

    Steps:
      1. Strip leading/trailing whitespace.
      2. Lowercase.
      3. Remove parenthetical unit suffix, e.g. "(ug/m3)", "(mg/m3)".
      4. Remove all characters that are not alphanumeric or underscore.
         This collapses "PM2.5" → "pm25", "NO2" → "no2", "Ozone" → "ozone".

    Examples
    --------
    "PM2.5 (ug/m3)"  → "pm25"
    "PM10 (ug/m3)"   → "pm10"
    "NO2 (ug/m3)"    → "no2"
    "SO2 (ug/m3)"    → "so2"
    "CO (mg/m3)"     → "co"
    "Ozone (ug/m3)"  → "ozone"
    "Timestamp"      → "timestamp"
    "Station Name"   → "station_name"   (kept as-is after stripping)
    "From Date"      → "from_date"
    "PM2.5"          → "pm25"
    "date_time"      → "date_time"
    """
    s = name.strip().lower()
    # Remove trailing unit suffix like (ug/m3)
    s = _UNIT_SUFFIX_RE.sub("", s)
    # Replace spaces and hyphens with underscore for readability before
    # stripping all punctuation (keeps multi-word names like "from_date")
    s = s.replace(" ", "_").replace("-", "_")
    # Remove everything that is not a letter, digit, or underscore
    s = re.sub(r"[^a-z0-9_]", "", s)
    # Collapse multiple consecutive underscores
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def _map_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict[str, str]]:
    """
    Build a canonical → actual-column mapping and rename the DataFrame.

    The function normalises every raw column name with _normalize_colname()
    then checks it against each canonical key's synonym list.  The first
    synonym that matches wins.

    Returns the renamed DataFrame and the mapping dict (canonical → original).
    """
    # Build: normalised_name → original_name
    normalized = {_normalize_colname(c): c for c in df.columns}
    mapping: dict[str, str] = {}

    for canonical, synonyms in COLUMN_SYNONYMS.items():
        for syn in synonyms:
            if syn in normalized:
                mapping[canonical] = normalized[syn]
                break

    if "timestamp" not in mapping:
        raise ValueError(
            "No timestamp column found. "
            "Expected a column named one of: "
            + ", ".join(COLUMN_SYNONYMS["timestamp"])
            + ". Detected columns (normalised): "
            + ", ".join(sorted(normalized.keys()))
        )

    found_pollutants = REQUIRED_POLLUTANT_COLS & set(mapping.keys())
    if not found_pollutants:
        raise ValueError(
            "No recognised air-quality columns found. "
            "Expected at least one of: pm25, pm10, no2, co, so2, o3. "
            "Accepted real-world names include: "
            "'PM2.5 (ug/m3)', 'PM10 (ug/m3)', 'NO2 (ug/m3)', "
            "'SO2 (ug/m3)', 'CO (mg/m3)', 'Ozone (ug/m3)'. "
            "Detected columns (normalised): "
            + ", ".join(sorted(normalized.keys()))
        )

    # Rename to canonical names
    reverse_mapping = {v: k for k, v in mapping.items()}
    df = df.rename(columns=reverse_mapping)
    # Keep only canonical columns that were found
    keep_cols = [c for c in mapping if c in df.columns]
    df = df[keep_cols].copy()

    return df, mapping


def preprocess(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    Full preprocessing pipeline.

    Parameters
    ----------
    raw_df : pd.DataFrame
        DataFrame parsed directly from the uploaded CSV.

    Returns
    -------
    clean_df : pd.DataFrame
        Cleaned, typed DataFrame with canonical column names.
    report : dict
        Human-readable summary of preprocessing decisions.
    """
    report: dict = {
        "original_rows": len(raw_df),
        "original_cols": list(raw_df.columns),
        "steps": [],
    }

    # ── 1. Map columns ────────────────────────────────────────────────────────
    df, col_mapping = _map_columns(raw_df)
    report["column_mapping"] = col_mapping
    report["steps"].append(
        f"Mapped {len(col_mapping)} columns: {list(col_mapping.keys())}"
    )

    # ── 2. Parse timestamps ───────────────────────────────────────────────────
    try:
        # errors="coerce" turns unparseable values into NaT instead of raising.
        # dayfirst=False is the safe default; pandas will still handle both
        # DD/MM/YYYY and MM/DD/YYYY via heuristic when format is ambiguous.
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    except Exception as exc:
        raise ValueError(f"Failed to parse timestamps: {exc}") from exc

    invalid_ts = df["timestamp"].isna().sum()
    if invalid_ts:
        df = df.dropna(subset=["timestamp"])
        report["steps"].append(f"Dropped {invalid_ts} rows with unparseable timestamps.")

    df = df.sort_values("timestamp").reset_index(drop=True)
    report["steps"].append("Sorted by timestamp.")

    # ── 3. Remove exact duplicates ────────────────────────────────────────────
    before = len(df)
    df = df.drop_duplicates(subset=["timestamp"])
    dup_removed = before - len(df)
    if dup_removed:
        report["steps"].append(f"Removed {dup_removed} duplicate timestamp rows.")

    # ── 4. Cast numeric columns ───────────────────────────────────────────────
    numeric_cols = [c for c in df.columns if c not in ("timestamp", "location")]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── 5. Remove physically impossible negative values ───────────────────────
    for col in numeric_cols:
        if col == "temperature":
            continue  # temperature can legitimately be negative
        neg_count = (df[col] < 0).sum()
        if neg_count:
            df.loc[df[col] < 0, col] = np.nan
            report["steps"].append(
                f"Replaced {neg_count} negative values in '{col}' with NaN."
            )

    # ── 6. Handle missing values ──────────────────────────────────────────────
    missing_before = df[numeric_cols].isna().sum().sum()
    # Forward-fill then backward-fill short gaps (up to 3 consecutive)
    df[numeric_cols] = (
        df[numeric_cols]
        .ffill(limit=3)
        .bfill(limit=3)
    )
    missing_after = df[numeric_cols].isna().sum().sum()
    filled = missing_before - missing_after
    if filled:
        report["steps"].append(
            f"Forward/backward filled {filled} missing values (limit 3 consecutive)."
        )

    # Drop rows where ALL pollutant columns are still NaN
    pollutant_cols_present = [
        c for c in ["pm25", "pm10", "no2", "co", "so2", "o3"] if c in df.columns
    ]
    before_drop = len(df)
    df = df.dropna(subset=pollutant_cols_present, how="all")
    dropped_all_nan = before_drop - len(df)
    if dropped_all_nan:
        report["steps"].append(
            f"Dropped {dropped_all_nan} rows where all pollutant values were missing."
        )

    # ── 7. Final statistics ───────────────────────────────────────────────────
    report["final_rows"] = len(df)
    report["available_features"] = pollutant_cols_present
    report["date_range"] = {
        "start": str(df["timestamp"].min()),
        "end":   str(df["timestamp"].max()),
    }

    if len(df) < 10:
        raise ValueError(
            f"Too few usable rows ({len(df)}) after preprocessing. "
            "Please provide a dataset with at least 10 valid measurements."
        )

    logger.info(
        "Preprocessing complete: %d → %d rows, features: %s",
        report["original_rows"], report["final_rows"], pollutant_cols_present,
    )
    return df, report
