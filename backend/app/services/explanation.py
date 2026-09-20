"""
Rule-based AI explanation generator for pollution events.

This module generates human-readable explanations for detected
pollution events without requiring an external LLM API.

Design principles
─────────────────
- Explanations describe WHAT was detected, not WHY (we cannot infer cause
  from concentration data alone).
- Possible contributing factors are listed as examples, not definitive causes.
- All explanations carry a responsible-AI disclaimer.
"""

from __future__ import annotations
import math
from typing import Optional


# ── Responsible-AI disclaimer ─────────────────────────────────────────────────
DISCLAIMER = (
    "⚠️ Responsible AI Note: This explanation is generated automatically "
    "by an AI model. It describes statistical patterns in the data and does "
    "NOT identify the definitive cause of elevated pollution. "
    "Do not use this information as a substitute for official air-quality "
    "advisories or professional environmental assessment."
)


def _duration_text(minutes: float) -> str:
    if minutes < 60:
        return f"approximately {int(minutes)} minutes"
    hours = minutes / 60
    if hours < 24:
        return f"approximately {hours:.1f} hours"
    days = hours / 24
    return f"approximately {days:.1f} days"


def _pollutant_description(max_pm25: Optional[float], max_pm10: Optional[float],
                            max_no2: Optional[float], max_co: Optional[float]) -> str:
    parts = []
    if max_pm25 is not None and not math.isnan(max_pm25):
        parts.append(f"PM2.5 peaked at {max_pm25:.1f} µg/m³")
    if max_pm10 is not None and not math.isnan(max_pm10):
        parts.append(f"PM10 peaked at {max_pm10:.1f} µg/m³")
    if max_no2 is not None and not math.isnan(max_no2):
        parts.append(f"NO₂ peaked at {max_no2:.1f} µg/m³")
    if max_co is not None and not math.isnan(max_co):
        parts.append(f"CO peaked at {max_co:.1f} mg/m³")

    if not parts:
        return "Elevated pollutant levels were detected."
    if len(parts) == 1:
        return parts[0] + " during the event."
    return ", ".join(parts[:-1]) + ", and " + parts[-1] + " during the event."


def _severity_context(severity: str) -> str:
    context = {
        "MODERATE": (
            "The pollution level was moderately above the recent baseline. "
            "This may be a short-term fluctuation."
        ),
        "HIGH": (
            "The pollution level was significantly above the recent baseline, "
            "which may be of concern for sensitive groups."
        ),
        "SEVERE": (
            "The pollution level was substantially above the recent baseline. "
            "This warrants attention and possible follow-up."
        ),
        "NORMAL": (
            "Although flagged by the anomaly model, the absolute pollutant "
            "levels remain within a relatively moderate range."
        ),
    }
    return context.get(severity, "")


def _contributing_factors(max_pm25: Optional[float], max_pm10: Optional[float],
                           duration_minutes: float) -> str:
    """
    List possible – NOT confirmed – contributing factors.
    We deliberately say 'may include' and 'available data is insufficient
    to determine the exact source.'
    """
    factors = [
        "vehicular traffic emissions",
        "industrial or construction activity",
        "biomass or waste burning",
        "stagnant meteorological conditions that trap pollutants near the surface",
        "dust re-suspension",
    ]
    if max_pm10 is not None and max_pm25 is not None and not math.isnan(max_pm10):
        if max_pm10 > max_pm25 * 1.8:
            factors.insert(0, "coarse particle sources such as road dust or construction")

    if duration_minutes > 180:
        factors.append("prolonged stagnant weather patterns")

    return (
        "Possible contributing factors (not confirmed) may include: "
        + "; ".join(factors[:4])
        + ". "
        "However, the available sensor data is insufficient to determine "
        "the exact pollution source."
    )


def generate_explanation(event: dict) -> str:
    """
    Generate a human-readable explanation for a pollution event dict.

    Parameters
    ----------
    event : dict
        A pollution event as returned by ``detect_events`` or stored in DB.

    Returns
    -------
    str
        Multi-paragraph explanation with disclaimer.
    """
    severity       = event.get("severity", "MODERATE")
    duration_min   = event.get("duration_minutes", 0)
    anomaly_count  = event.get("anomaly_count", 0)
    anomaly_score  = event.get("anomaly_score", 0.0)
    max_pm25       = event.get("max_pm25")
    max_pm10       = event.get("max_pm10")
    max_no2        = event.get("max_no2")
    max_co         = event.get("max_co")

    # Paragraph 1 – what was detected
    p1 = (
        f"The AI anomaly detection system identified an unusual pattern in "
        f"air-quality measurements spanning {_duration_text(duration_min)} "
        f"({anomaly_count} anomalous observation{'s' if anomaly_count != 1 else ''}). "
        f"The normalised anomaly score was {anomaly_score:.2f} (scale 0–1, "
        f"where higher values indicate greater deviation from the recent baseline)."
    )

    # Paragraph 2 – pollutant details
    p2 = _pollutant_description(max_pm25, max_pm10, max_no2, max_co)

    # Paragraph 3 – severity context
    p3 = _severity_context(severity)

    # Paragraph 4 – contributing factors
    p4 = _contributing_factors(max_pm25, max_pm10, duration_min)

    # Paragraph 5 – disclaimer
    p5 = DISCLAIMER

    return "\n\n".join([p1, p2, p3, p4, p5])


# ── Rule-based chatbot responses ──────────────────────────────────────────────
CHATBOT_RESPONSES: dict[str, str] = {
    "pm2.5": (
        "PM2.5 refers to fine particulate matter with a diameter of 2.5 micrometres "
        "or less. These tiny particles can penetrate deep into the lungs and "
        "enter the bloodstream. Long-term exposure is associated with respiratory "
        "and cardiovascular health risks. (Source: WHO)"
    ),
    "pm10": (
        "PM10 refers to coarse particles with diameters of 10 micrometres or less. "
        "They are produced by dust, pollen, mould, and combustion. PM10 can irritate "
        "the respiratory tract. (Source: WHO)"
    ),
    "anomaly": (
        "Anomaly detection is an AI technique that learns the 'normal' pattern in "
        "data and flags observations that deviate significantly from that pattern. "
        "In AirGuard, we use Isolation Forest to identify unusual pollution readings."
    ),
    "isolation forest": (
        "Isolation Forest is an unsupervised machine-learning algorithm. It isolates "
        "anomalies by randomly partitioning the feature space. Anomalies are rare "
        "and different, so they are isolated quickly (fewer splits). Normal points "
        "require many more splits to isolate."
    ),
    "sdg 11": (
        "SDG 11 – Sustainable Cities and Communities – aims to make cities inclusive, "
        "safe, resilient, and sustainable. Air-quality monitoring contributes to SDG 11 "
        "by helping communities understand and reduce urban pollution."
    ),
    "sdg 3": (
        "SDG 3 – Good Health and Well-being – includes targets on reducing deaths from "
        "air pollution. AirGuard supports this goal by raising awareness about "
        "pollution events."
    ),
    "sdg 13": (
        "SDG 13 – Climate Action – addresses the urgent need to combat climate change. "
        "Many air pollutants (like black carbon) are also short-lived climate forcers, "
        "so reducing air pollution supports climate goals too."
    ),
    "air quality": (
        "Air quality refers to the condition of the air in our environment. It is "
        "measured by the concentration of pollutants such as PM2.5, PM10, NO2, CO, "
        "SO2, and ozone. Poor air quality can affect human health, ecosystems, and "
        "climate."
    ),
    "reduce": (
        "Communities can reduce air pollution by: using public transport or cycling, "
        "avoiding waste burning, planting trees, supporting clean energy policies, "
        "and reporting visible pollution sources to local authorities."
    ),
    "air pollution": (
        "Air pollution is the presence of harmful substances in the atmosphere. "
        "Sources include vehicles, industry, construction, and biomass burning. "
        "Long-term exposure is associated with respiratory disease, cardiovascular "
        "problems, and reduced life expectancy. The WHO estimates 99% of the world's "
        "population breathes air that exceeds guideline limits. (Source: WHO)"
    ),
    "pollution event": (
        "A pollution event, in AirGuard, is a period during which the AI model "
        "detects an abnormal elevation in one or more pollutants. Consecutive "
        "anomalous readings are grouped into a single event rather than being "
        "treated as separate incidents."
    ),
    "airguard": (
        "AirGuard is an AI-based air pollution event detection and early warning system. "
        "It uses the Isolation Forest unsupervised machine learning algorithm to detect "
        "unusual pollution patterns in time-series sensor data, groups them into pollution "
        "events, classifies their severity, and presents the results through a web dashboard. "
        "It is a student project built for the 1M1B AI for Sustainability Internship, "
        "aligned with SDG 11, SDG 3, and SDG 13."
    ),
    "reduce": (
        "Communities can reduce air pollution by: using public transport or cycling, "
        "avoiding waste burning, planting trees, supporting clean energy policies, "
        "and reporting visible pollution sources to local authorities."
    ),
    "default": (
        "I can answer questions about PM2.5, PM10, anomaly detection, Isolation Forest, "
        "pollution events, SDG 11, SDG 3, SDG 13, and how to reduce air pollution. "
        "Please ask about one of these topics."
    ),
}


def chatbot_response(question: str) -> str:
    """
    Simple keyword-based chatbot.
    Returns the best matching pre-written answer.
    """
    q = question.lower()
    for keyword, response in CHATBOT_RESPONSES.items():
        if keyword == "default":
            continue
        if keyword in q:
            return response
    return CHATBOT_RESPONSES["default"]
