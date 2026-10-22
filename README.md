# Learning deterioration for the RPA NICU - Biodesign.Sydney 2026

Proof of concept machine-learning experimentation platform for NICU deterioration prediction.

**Status:** Early-stage prototype. Data ingestion and scoring workflows are under development; the current scores are illustrative and are not clinically validated predictions.

## Overview

This project aims to provide a modular framework for experimenting with different data sources, feature representations, prediction models, and clinical deterioration outcomes.

The intended workflow is:

1. **Data ingestion:** Retrieve clinical records and measurements from external data sources.
2. **Feature extraction:** Transform raw records into structured, analysis-ready features.
3. **Prediction:** Apply configurable models to estimate the risk of a specified outcome.
4. **Evaluation:** Assess model performance against observed outcomes using appropriate validation strategies.
5. **Experimentation:** Compare data modalities, model architectures, and prediction tasks within a consistent workflow.

The initial prototype explores three feature groups:

- **Vitals:** Heart rate, oxygen saturation (SpO₂), and mean arterial pressure (MAP).
- **Waveform-derived features:** Heart rate variability (HRV), respiratory rate, and perfusion index.
- **Laboratory measurements:** Lactate, white blood cell count (WBC), and creatinine.

The initial prediction tasks are sepsis, respiratory failure, and haemodynamic instability.

## Repository structure

```text
nicu-biodesign/
├── nicu_biodesign/
│   ├── __init__.py       # Public package interface
│   ├── vitaldb.py        # VitalDB API client and response parsing
│   ├── experiments.py    # Feature extraction and prototype scoring methods
│   └── platform.py       # Experiment orchestration and result summaries
├── tests/
│   └── test_platform.py  # Automated software tests
├── run_experiment.py     # Example experiment entry point
└── README.md
```

## Data sources

The initial ingestion client targets the public VitalDB API:

- `https://api.vitaldb.net/cases` — case-level clinical information
- `https://api.vitaldb.net/trks` — track metadata
- `https://api.vitaldb.net/labs` — laboratory results
- `https://api.vitaldb.net/{tid}` — time-series data for an individual track identifier

The current client parses CSV responses and supports a local row limit for the `cases`, `trks`, and `labs` endpoints.

**Important:** These endpoints provide different types of data. Case metadata does not automatically contain the vital-sign or waveform features defined by the prototype. Linking cases to tracks, retrieving measurements, handling timestamps, and constructing analysis-ready observations remain necessary steps in the data pipeline.

## Running the prototype

From the repository root, run:

```bash
python run_experiment.py
```

The example script attempts to retrieve a small sample from VitalDB, prints the available columns, and then invokes the experiment platform.

The prediction stage is currently illustrative and may not run meaningfully on the raw `cases` endpoint because the expected feature columns may be absent.

## Running tests

From the repository root:

```bash
python -m unittest discover -s tests -v
```

The tests are intended to verify data-client behaviour, supported configurations, feature extraction, and result summaries without relying on live API requests.