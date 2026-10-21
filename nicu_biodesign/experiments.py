from __future__ import annotations

from dataclasses import dataclass
from math import exp


FEATURES_BY_DATA_TYPE = {
    "vitals": ("heart_rate", "spo2", "map"),
    "waveform": ("hrv", "respiratory_rate", "perfusion_index"),
    "labs": ("lactate", "wbc", "creatinine"),
}

SUPPORTED_INDICATIONS = {"sepsis", "respiratory_failure", "hemodynamic_instability"}


def _normalize(value: float, baseline: float, scale: float) -> float:
    return (value - baseline) / scale


def extract_features(records: list[dict[str, float]], data_type: str) -> list[list[float]]:
    feature_names = FEATURES_BY_DATA_TYPE.get(data_type)
    if feature_names is None:
        raise ValueError(f"Unsupported data_type: {data_type}")

    rows: list[list[float]] = []
    for record in records:
        rows.append([float(record.get(feature_name, 0.0) or 0.0) for feature_name in feature_names])
    return rows


def _profile(indication: str) -> tuple[list[float], list[float]]:
    if indication not in SUPPORTED_INDICATIONS:
        raise ValueError(f"Unsupported indication: {indication}")

    if indication == "sepsis":
        return [0.9, -0.8, -0.2], [100.0, 95.0, 65.0]
    if indication == "respiratory_failure":
        return [0.5, -1.0, -0.1], [95.0, 94.0, 70.0]
    return [0.4, -0.5, -0.9], [95.0, 95.0, 75.0]


def _logistic(activations: list[float], intercept: float = 0.0) -> float:
    return 1.0 / (1.0 + exp(-(sum(activations) + intercept)))


def predict_with_logistic(features: list[list[float]], indication: str) -> list[float]:
    weights, baselines = _profile(indication)
    risks: list[float] = []
    for row in features:
        activations = [
            weight * _normalize(value, baseline, 20.0)
            for weight, value, baseline in zip(weights, row, baselines)
        ]
        risks.append(_logistic(activations))
    return risks


def predict_with_rules(features: list[list[float]], indication: str) -> list[float]:
    weights, baselines = _profile(indication)
    risks: list[float] = []
    for row in features:
        risk_score = 0.0
        for weight, value, baseline in zip(weights, row, baselines):
            if weight >= 0 and value > baseline:
                risk_score += abs(weight)
            elif weight < 0 and value < baseline:
                risk_score += abs(weight)
        risks.append(min(risk_score / 3.0, 1.0))
    return risks


def predict(features: list[list[float]], architecture: str, indication: str) -> list[float]:
    if architecture == "logistic":
        return predict_with_logistic(features, indication)
    if architecture == "rule_tree":
        return predict_with_rules(features, indication)
    raise ValueError(f"Unsupported architecture: {architecture}")


@dataclass(frozen=True)
class ExperimentResult:
    data_type: str
    architecture: str
    indication: str
    sample_count: int
    mean_risk: float
    high_risk_fraction: float
    risks: list[float]
