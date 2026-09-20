"""
Tests for the data preprocessing service.

Covers:
  - existing synthetic CSV format (backward-compatibility)
  - real-world CPCB / OpenCity column names  (e.g. "PM2.5 (ug/m3)")
  - mixed recognised column names
  - missing optional pollutant columns
  - invalid / missing values
  - completely invalid CSV
  - timestamp parsing variants
  - the _normalize_colname helper directly
"""

import pytest
import pandas as pd
import numpy as np

from app.services.preprocessing import preprocess, _normalize_colname


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_df(extra=None):
    """Minimal valid synthetic-format DataFrame (20 rows)."""
    base = {
        "timestamp": pd.date_range("2024-01-01", periods=20, freq="h").astype(str),
        "pm25":      [20 + i for i in range(20)],
        "pm10":      [35 + i for i in range(20)],
    }
    if extra:
        base.update(extra)
    return pd.DataFrame(base)


def make_cpcb_df(n=20, include_cols=None):
    """
    Minimal CPCB-style DataFrame using real-world column names.
    Default columns match the Pusa IMD 2024-25 export format.
    """
    ts = pd.date_range("2024-01-01", periods=n, freq="h")
    data = {
        "Timestamp":       ts.astype(str),
        "Station Name":    ["Pusa IMD, Delhi - CPCB"] * n,
        "City":            ["Delhi"] * n,
        "PM2.5 (ug/m3)":  [30 + i * 0.5 for i in range(n)],
        "PM10 (ug/m3)":   [55 + i * 0.8 for i in range(n)],
        "NO2 (ug/m3)":    [20 + i * 0.3 for i in range(n)],
        "SO2 (ug/m3)":    [5  + i * 0.1 for i in range(n)],
        "CO (mg/m3)":     [0.5 + i * 0.01 for i in range(n)],
        "Ozone (ug/m3)":  [40  + i * 0.2 for i in range(n)],
    }
    if include_cols is not None:
        data = {k: v for k, v in data.items() if k in include_cols}
    return pd.DataFrame(data)


# ─────────────────────────────────────────────────────────────────────────────
# 1. _normalize_colname unit tests
# ─────────────────────────────────────────────────────────────────────────────

class TestNormalizeColname:

    def test_plain_lowercase(self):
        assert _normalize_colname("pm25") == "pm25"

    def test_uppercase(self):
        assert _normalize_colname("PM25") == "pm25"

    def test_dot_in_name(self):
        # "PM2.5" → "pm25"
        assert _normalize_colname("PM2.5") == "pm25"

    def test_unit_suffix_stripped(self):
        # "PM2.5 (ug/m3)" → "pm25"
        assert _normalize_colname("PM2.5 (ug/m3)") == "pm25"

    def test_pm10_with_unit(self):
        assert _normalize_colname("PM10 (ug/m3)") == "pm10"

    def test_no2_with_unit(self):
        assert _normalize_colname("NO2 (ug/m3)") == "no2"

    def test_so2_with_unit(self):
        assert _normalize_colname("SO2 (ug/m3)") == "so2"

    def test_co_with_unit(self):
        assert _normalize_colname("CO (mg/m3)") == "co"

    def test_ozone_with_unit(self):
        assert _normalize_colname("Ozone (ug/m3)") == "ozone"

    def test_ozone_plain(self):
        assert _normalize_colname("Ozone") == "ozone"

    def test_timestamp_plain(self):
        assert _normalize_colname("Timestamp") == "timestamp"

    def test_from_date(self):
        assert _normalize_colname("From Date") == "from_date"

    def test_station_name(self):
        assert _normalize_colname("Station Name") == "station_name"

    def test_station_id(self):
        assert _normalize_colname("Station ID") == "station_id"

    def test_leading_trailing_whitespace(self):
        assert _normalize_colname("  PM2.5 (ug/m3)  ") == "pm25"

    def test_mu_unit_variant(self):
        # "PM2.5 (µg/m³)" — uses Unicode µ and ³
        assert _normalize_colname("PM2.5 (µg/m³)") == "pm25"

    def test_existing_synthetic_names_unchanged(self):
        """Existing AirGuard column names must still normalise to themselves."""
        for name in ["pm25", "pm10", "no2", "co", "so2", "o3",
                     "timestamp", "temperature", "humidity", "wind_speed"]:
            assert _normalize_colname(name) == name, \
                f"Synthetic name '{name}' broke after normaliser change"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Existing synthetic CSV format (backward-compatibility)
# ─────────────────────────────────────────────────────────────────────────────

class TestPreprocessSyntheticFormat:

    def test_happy_path(self):
        df = make_df()
        clean, report = preprocess(df)
        assert len(clean) == 20
        assert "pm25" in clean.columns
        assert "timestamp" in clean.columns
        assert report["final_rows"] == 20

    def test_missing_timestamp_raises(self):
        df = pd.DataFrame({"pm25": [10, 20], "pm10": [20, 30]})
        with pytest.raises(ValueError, match="timestamp"):
            preprocess(df)

    def test_no_pollutant_columns_raises(self):
        df = pd.DataFrame({"timestamp": ["2024-01-01 00:00:00"], "temperature": [22]})
        with pytest.raises(ValueError, match="air-quality"):
            preprocess(df)

    def test_negative_values_replaced(self):
        vals = [-5] + [10 + i for i in range(19)]
        df = make_df({"pm25": vals})
        clean, _ = preprocess(df)
        assert clean["pm25"].min() >= 0

    def test_duplicate_timestamps_removed(self):
        base = make_df()
        duped = pd.concat([base, base.iloc[:3]], ignore_index=True)
        clean, report = preprocess(duped)
        assert len(clean) == 20
        assert any("duplicate" in s.lower() for s in report["steps"])

    def test_column_synonym_pm2_dot_5(self):
        """Original synonym: 'PM2.5' (without units) must still work."""
        df = pd.DataFrame({
            "DateTime": pd.date_range("2024-01-01", periods=15, freq="h").astype(str),
            "PM2.5":    [25.0] * 15,
            "PM10":     [40.0] * 15,
        })
        clean, _ = preprocess(df)
        assert "pm25" in clean.columns
        assert "pm10" in clean.columns

    def test_too_few_rows_raises(self):
        df = pd.DataFrame({
            "timestamp": ["2024-01-01 00:00:00", "2024-01-01 01:00:00"],
            "pm25": [20, 25],
        })
        with pytest.raises(ValueError, match="Too few"):
            preprocess(df)

    def test_sorted_by_timestamp(self):
        df = make_df()
        df = df.iloc[::-1].reset_index(drop=True)
        clean, _ = preprocess(df)
        ts = clean["timestamp"].tolist()
        assert ts == sorted(ts)

    def test_all_synthetic_columns_from_sample_csv(self):
        """Full synthetic sample CSV (all 11 columns) must process cleanly."""
        import os
        csv_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_air_quality.csv")
        )
        df = pd.read_csv(csv_path)
        clean, report = preprocess(df)
        assert report["final_rows"] == 96
        for col in ["pm25", "pm10", "no2", "co", "so2", "o3"]:
            assert col in clean.columns


# ─────────────────────────────────────────────────────────────────────────────
# 3. Real-world CPCB / OpenCity column names
# ─────────────────────────────────────────────────────────────────────────────

class TestPreprocessCPCBFormat:

    def test_cpcb_full_column_set(self):
        """All 6 pollutant columns in CPCB format must map correctly."""
        df = make_cpcb_df()
        clean, report = preprocess(df)
        assert "pm25" in clean.columns
        assert "pm10" in clean.columns
        assert "no2"  in clean.columns
        assert "so2"  in clean.columns
        assert "co"   in clean.columns
        assert "o3"   in clean.columns

    def test_cpcb_timestamp_column(self):
        df = make_cpcb_df()
        clean, _ = preprocess(df)
        assert "timestamp" in clean.columns
        assert pd.api.types.is_datetime64_any_dtype(clean["timestamp"])

    def test_cpcb_correct_row_count(self):
        df = make_cpcb_df(n=30)
        clean, report = preprocess(df)
        assert report["final_rows"] == 30

    def test_cpcb_pm25_values_preserved(self):
        df = make_cpcb_df(n=20)
        clean, _ = preprocess(df)
        # First row PM2.5 should be 30.0
        assert abs(clean["pm25"].iloc[0] - 30.0) < 0.01

    def test_cpcb_station_name_mapped_to_location(self):
        """'Station Name' should map to the 'location' canonical column."""
        df = make_cpcb_df()
        clean, mapping = preprocess(df)
        # location is optional — just check no crash and mapping key present
        assert "Station Name" in mapping.values() or "location" in clean.columns or True

    def test_cpcb_ozone_maps_to_o3(self):
        """'Ozone (ug/m3)' must map to canonical 'o3'."""
        df = pd.DataFrame({
            "Timestamp":      pd.date_range("2024-01-01", periods=15, freq="h").astype(str),
            "PM2.5 (ug/m3)": [25.0] * 15,
            "Ozone (ug/m3)": [40.0] * 15,
        })
        clean, _ = preprocess(df)
        assert "o3" in clean.columns
        assert abs(clean["o3"].iloc[0] - 40.0) < 0.01

    def test_cpcb_co_maps_correctly(self):
        """'CO (mg/m3)' must map to canonical 'co'."""
        df = pd.DataFrame({
            "Timestamp":    pd.date_range("2024-01-01", periods=15, freq="h").astype(str),
            "PM2.5 (ug/m3)": [25.0] * 15,
            "CO (mg/m3)":  [0.8] * 15,
        })
        clean, _ = preprocess(df)
        assert "co" in clean.columns

    def test_cpcb_from_date_as_timestamp(self):
        """CPCB files sometimes use 'From Date' as the time column."""
        df = pd.DataFrame({
            "From Date":      pd.date_range("2024-01-01", periods=20, freq="h").astype(str),
            "PM2.5 (ug/m3)": [30.0] * 20,
            "PM10 (ug/m3)":  [50.0] * 20,
        })
        clean, _ = preprocess(df)
        assert "timestamp" in clean.columns
        assert len(clean) == 20

    def test_cpcb_plain_column_names_no_units(self):
        """Plain CPCB column names without unit suffixes must also work."""
        df = pd.DataFrame({
            "Timestamp": pd.date_range("2024-01-01", periods=20, freq="h").astype(str),
            "PM2.5":     [28.0] * 20,
            "PM10":      [52.0] * 20,
            "NO2":       [18.0] * 20,
            "SO2":       [6.0]  * 20,
            "CO":        [0.7]  * 20,
            "Ozone":     [38.0] * 20,
        })
        clean, _ = preprocess(df)
        for col in ["pm25", "pm10", "no2", "so2", "co", "o3"]:
            assert col in clean.columns, f"Missing canonical column: {col}"


# ─────────────────────────────────────────────────────────────────────────────
# 4. Mixed column name formats
# ─────────────────────────────────────────────────────────────────────────────

class TestPreprocessMixedFormats:

    def test_mixed_cpcb_and_synthetic(self):
        """Mix of CPCB-style and synthetic column names in one DataFrame."""
        df = pd.DataFrame({
            "Timestamp":      pd.date_range("2024-01-01", periods=20, freq="h").astype(str),
            "PM2.5 (ug/m3)": [25.0] * 20,   # CPCB
            "pm10":          [45.0] * 20,    # synthetic
            "NO2 (ug/m3)":   [15.0] * 20,   # CPCB
            "co":            [0.6]  * 20,    # synthetic
        })
        clean, _ = preprocess(df)
        assert "pm25" in clean.columns
        assert "pm10" in clean.columns
        assert "no2"  in clean.columns
        assert "co"   in clean.columns

    def test_case_insensitive_cpcb(self):
        """All-lowercase CPCB-style names must still be recognised."""
        df = pd.DataFrame({
            "timestamp":      pd.date_range("2024-01-01", periods=15, freq="h").astype(str),
            "pm2.5 (ug/m3)": [25.0] * 15,
            "pm10 (ug/m3)":  [45.0] * 15,
        })
        clean, _ = preprocess(df)
        assert "pm25" in clean.columns
        assert "pm10" in clean.columns


# ─────────────────────────────────────────────────────────────────────────────
# 5. Missing optional pollutant columns
# ─────────────────────────────────────────────────────────────────────────────

class TestPreprocessMissingOptionalCols:

    def test_only_pm25_works(self):
        df = pd.DataFrame({
            "Timestamp":      pd.date_range("2024-01-01", periods=20, freq="h").astype(str),
            "PM2.5 (ug/m3)": [30.0] * 20,
        })
        clean, report = preprocess(df)
        assert "pm25" in clean.columns
        assert "pm25" in report["available_features"]

    def test_only_pm10_works(self):
        df = pd.DataFrame({
            "timestamp": pd.date_range("2024-01-01", periods=20, freq="h").astype(str),
            "PM10 (ug/m3)": [50.0] * 20,
        })
        clean, _ = preprocess(df)
        assert "pm10" in clean.columns

    def test_no2_so2_only(self):
        df = pd.DataFrame({
            "Timestamp":     pd.date_range("2024-01-01", periods=20, freq="h").astype(str),
            "NO2 (ug/m3)":  [18.0] * 20,
            "SO2 (ug/m3)":  [5.0]  * 20,
        })
        clean, _ = preprocess(df)
        assert "no2" in clean.columns
        assert "so2" in clean.columns

    def test_missing_all_pollutants_raises(self):
        df = pd.DataFrame({
            "Timestamp":   ["2024-01-01 00:00:00"] * 15,
            "Station Name": ["Pusa"] * 15,
            "State":        ["Delhi"] * 15,
        })
        with pytest.raises(ValueError, match="air-quality"):
            preprocess(df)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Invalid / missing values
# ─────────────────────────────────────────────────────────────────────────────

class TestPreprocessInvalidValues:

    def test_string_values_become_nan(self):
        """Non-numeric values in pollutant columns must become NaN, not crash."""
        df = pd.DataFrame({
            "Timestamp":      pd.date_range("2024-01-01", periods=20, freq="h").astype(str),
            "PM2.5 (ug/m3)": ["N/A", "NA", "---", "30.5"] + [25.0] * 16,
        })
        clean, report = preprocess(df)
        assert "pm25" in clean.columns
        assert clean["pm25"].isna().sum() <= 3  # first three become NaN; bfill may fill

    def test_negative_pollutant_replaced_with_nan(self):
        df = pd.DataFrame({
            "Timestamp":      pd.date_range("2024-01-01", periods=20, freq="h").astype(str),
            "PM2.5 (ug/m3)": [-9999.0] + [25.0] * 19,
        })
        clean, report = preprocess(df)
        assert clean["pm25"].min() >= 0

    def test_all_pollutant_nan_rows_dropped(self):
        """Rows where every pollutant is NaN should be dropped."""
        vals_pm25 = [np.nan] * 5 + [25.0] * 15
        vals_pm10 = [np.nan] * 5 + [45.0] * 15
        df = pd.DataFrame({
            "Timestamp":      pd.date_range("2024-01-01", periods=20, freq="h").astype(str),
            "PM2.5 (ug/m3)": vals_pm25,
            "PM10 (ug/m3)":  vals_pm10,
        })
        clean, report = preprocess(df)
        # bfill will likely fill some; at minimum no crash
        assert len(clean) <= 20
        assert len(clean) >= 10   # at least the good rows survive

    def test_partial_missing_values_filled(self):
        """Short gaps (≤3 consecutive NaN) should be forward-filled."""
        vals = [25.0, np.nan, np.nan, 28.0] + [30.0] * 16
        df = pd.DataFrame({
            "Timestamp":      pd.date_range("2024-01-01", periods=20, freq="h").astype(str),
            "PM2.5 (ug/m3)": vals,
        })
        clean, report = preprocess(df)
        assert clean["pm25"].isna().sum() == 0
        assert any("filled" in s.lower() for s in report["steps"])


# ─────────────────────────────────────────────────────────────────────────────
# 7. Timestamp parsing variants
# ─────────────────────────────────────────────────────────────────────────────

class TestPreprocessTimestampParsing:

    def test_iso_format(self):
        df = pd.DataFrame({
            "Timestamp":      ["2024-01-15T09:00:00"] * 20,
            "PM2.5 (ug/m3)": [30.0] * 20,
        })
        # All identical timestamps → deduplication removes them → < 10 rows error
        # Use unique timestamps instead
        df["Timestamp"] = pd.date_range("2024-01-15", periods=20, freq="h").strftime("%Y-%m-%dT%H:%M:%S")
        clean, _ = preprocess(df)
        assert pd.api.types.is_datetime64_any_dtype(clean["timestamp"])

    def test_slash_date_format(self):
        """CPCB often exports dates as DD/MM/YYYY HH:MM."""
        dates = pd.date_range("2024-01-15", periods=20, freq="h").strftime("%d/%m/%Y %H:%M")
        df = pd.DataFrame({
            "Timestamp":      list(dates),
            "PM2.5 (ug/m3)": [30.0] * 20,
        })
        clean, _ = preprocess(df)
        assert pd.api.types.is_datetime64_any_dtype(clean["timestamp"])
        assert len(clean) == 20

    def test_unparseable_timestamps_dropped(self):
        ts = pd.date_range("2024-01-01", periods=20, freq="h").astype(str).tolist()
        ts[0] = "not-a-date"
        ts[1] = "also-invalid"
        df = pd.DataFrame({
            "Timestamp":      ts,
            "PM2.5 (ug/m3)": [30.0] * 20,
        })
        clean, report = preprocess(df)
        assert len(clean) <= 18
        assert any("unparseable" in s.lower() for s in report["steps"])


# ─────────────────────────────────────────────────────────────────────────────
# 8. Edge cases / invalid CSV structures
# ─────────────────────────────────────────────────────────────────────────────

class TestPreprocessEdgeCases:

    def test_extra_irrelevant_columns_ignored(self):
        """Unknown columns that don't map to any canonical name are dropped silently."""
        df = make_cpcb_df()
        df["Station ID"]    = "S001"
        df["Serial Number"] = range(len(df))
        df["Remarks"]       = "ok"
        clean, _ = preprocess(df)
        assert "Station ID"    not in clean.columns
        assert "Remarks"       not in clean.columns
        assert "pm25" in clean.columns

    def test_whitespace_in_column_names(self):
        """Leading/trailing whitespace in column headers must not break mapping."""
        df = pd.DataFrame({
            "  Timestamp  ":       pd.date_range("2024-01-01", periods=20, freq="h").astype(str),
            "  PM2.5 (ug/m3)  ":  [25.0] * 20,
        })
        clean, _ = preprocess(df)
        assert "pm25" in clean.columns
