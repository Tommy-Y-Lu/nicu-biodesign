# nicu-biodesign

Machine-learning experimentation platform for NICU deterioration prediction.

## What this repository now provides

- VitalDB API ingestion through `VitalDBClient`
- Experiment runner (`DeteriorationPlatform`) to:
  - pull a dataset from an API endpoint
  - experiment with different data types (`vitals`, `waveform`, `labs`)
  - switch between architectures (`logistic`, `rule_tree`)
  - predict different deterioration indications:
    - `sepsis`
    - `respiratory_failure`
    - `hemodynamic_instability`

## Example

```python
from nicu_biodesign import DeteriorationPlatform, VitalDBClient

client = VitalDBClient(base_url="https://your-vitaldb-api.example")
platform = DeteriorationPlatform(client)

result = platform.run_experiment(
    dataset_id="nicu-icu",
    data_type="vitals",
    architecture="logistic",
    indication="sepsis",
    limit=100,
)

print(result.mean_risk, result.high_risk_fraction)
```

## Run tests

```bash
python -m unittest discover -s tests
```
