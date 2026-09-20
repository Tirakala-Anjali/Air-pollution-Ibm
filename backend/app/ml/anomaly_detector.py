"""
Anomaly detection using Isolation Forest.

Why Isolation Forest?
─────────────────────
Isolation Forest is well-suited for this problem because:

1. Unsupervised – Air-quality datasets typically lack labelled anomalies,
   so we cannot use supervised classifiers.
2. Efficient at high dimensions – Multiple pollutant features (PM2.5, PM10,
   NO2, CO, …) can all be fed in together without performance collapse.
3. Anomaly-score output – It produces a continuous score, not just a binary
   flag, which lets us calibrate severity thresholds.
4. Robust to outliers in training data – The algorithm isolates anomalies
   by randomly splitting the feature space; anomalies require fewer splits
   and therefore get a lower (more negative) score.
5. No distributional assumption – Air-quality data does not follow a neat
   Gaussian distribution, making density-based methods (like Gaussian
   Mixture Models) less appropriate.

The contamination parameter is set conservatively (5 %) since most real
air-quality recordings are normal.  Users can adjust this via the API.
"""

import logging
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

# Feature priority order – the pipeline uses whichever of these exist
FEATURE_PRIORITY = ["pm25", "pm10", "no2", "co", "so2", "o3",
                    "temperature", "humidity", "wind_speed"]

# Isolation Forest contamination rate (expected fraction of anomalies)
DEFAULT_CONTAMINATION = 0.05


def _select_features(df: pd.DataFrame) -> list[str]:
    """Return only the feature columns that exist in the DataFrame."""
    return [f for f in FEATURE_PRIORITY if f in df.columns and df[f].notna().sum() > 0]


def detect_anomalies(
    df: pd.DataFrame,
    contamination: float = DEFAULT_CONTAMINATION,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, dict]:
    """
    Run Isolation Forest on the preprocessed DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Output of the preprocessing pipeline (canonical column names).
    contamination : float
        Expected fraction of anomalous observations (0.01 – 0.20).
    random_state : int
        Reproducibility seed.

    Returns
    -------
    result_df : pd.DataFrame
        Original DataFrame with two new columns:
          - ``anomaly_score``  : float, lower = more anomalous
          - ``is_anomaly``     : bool
    model_info : dict
        Metadata about the trained model.
    """
    features = _select_features(df)
    if not features:
        raise ValueError("No usable numeric features found for anomaly detection.")

    logger.info("Running Isolation Forest on features: %s", features)

    X = df[features].copy()

    # Impute any remaining NaNs with column medians before scaling
    for col in features:
        median = X[col].median()
        X[col] = X[col].fillna(median)

    # Standardise – Isolation Forest works better when features are on similar scales
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ── Train Isolation Forest ────────────────────────────────────────────────
    clf = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        max_samples="auto",
        random_state=random_state,
        n_jobs=-1,
    )
    clf.fit(X_scaled)

    # Predictions: +1 = normal, -1 = anomaly
    predictions = clf.predict(X_scaled)
    # Raw decision function: more negative = more anomalous
    raw_scores = clf.decision_function(X_scaled)

    # Normalise scores to [0, 1] where 1 = most anomalous for interpretability
    min_score = raw_scores.min()
    max_score = raw_scores.max()
    if max_score != min_score:
        normalised_scores = (raw_scores - min_score) / (max_score - min_score)
        # Invert: 1 = anomalous, 0 = normal
        normalised_scores = 1.0 - normalised_scores
    else:
        normalised_scores = np.zeros(len(raw_scores))

    result_df = df.copy()
    result_df["anomaly_score"] = np.round(normalised_scores, 4)
    result_df["is_anomaly"]    = predictions == -1

    anomaly_count  = int(result_df["is_anomaly"].sum())
    total          = len(result_df)

    model_info = {
        "algorithm":         "Isolation Forest",
        "n_estimators":      200,
        "contamination":     contamination,
        "features_used":     features,
        "total_records":     total,
        "anomalies_detected": anomaly_count,
        "anomaly_rate_pct":  round(anomaly_count / total * 100, 2),
        "note": (
            "Anomaly scores are normalised to [0, 1] for display purposes. "
            "1 = most anomalous. These are relative scores, not official AQI values."
        ),
    }

    logger.info(
        "Detection complete: %d/%d records flagged as anomalies (%.1f %%)",
        anomaly_count, total, model_info["anomaly_rate_pct"],
    )
    return result_df, model_info
