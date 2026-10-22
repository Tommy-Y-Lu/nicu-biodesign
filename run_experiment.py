from nicu_biodesign import DeteriorationPlatform, VitalDBClient

def main():
    client = VitalDBClient(
        base_url="https://api.vitaldb.net"
    )

    # Test actual VitalDB ingestion first.
    records = client.fetch_dataset("cases", limit=5)
    print(f"Retrieved {len(records)} clinical records")
    print("Available columns:", list(records[0].keys()))
    print("First record:", records[0])

    # Then try the existing platform.
    platform = DeteriorationPlatform(client)

    result = platform.run_experiment(
        dataset_id="cases",
        data_type="vitals",
        architecture="logistic",
        indication="sepsis",
        limit=100,
    )

    print("Mean risk:", result.mean_risk)
    print("High-risk fraction:", result.high_risk_fraction)

if __name__ == "__main__":
    main()