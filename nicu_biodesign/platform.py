from __future__ import annotations

from .experiments import ExperimentResult, extract_features, predict
from .vitaldb import VitalDBClient


class DeteriorationPlatform:
    def __init__(self, vitaldb_client: VitalDBClient):
        self.vitaldb_client = vitaldb_client

    def run_experiment(
        self,
        dataset_id: str,
        data_type: str,
        architecture: str,
        indication: str,
        limit: int = 100,
    ) -> ExperimentResult:
        records = self.vitaldb_client.fetch_dataset(dataset_id=dataset_id, limit=limit)
        features = extract_features(records, data_type=data_type)
        risks = predict(features, architecture=architecture, indication=indication)
        sample_count = len(risks)
        mean_risk = sum(risks) / sample_count if sample_count else 0.0
        high_risk_fraction = sum(1 for risk in risks if risk >= 0.5) / sample_count if sample_count else 0.0

        return ExperimentResult(
            data_type=data_type,
            architecture=architecture,
            indication=indication,
            sample_count=sample_count,
            mean_risk=mean_risk,
            high_risk_fraction=high_risk_fraction,
            risks=risks,
        )


__all__ = ["DeteriorationPlatform", "ExperimentResult"]
