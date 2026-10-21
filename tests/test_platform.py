import json
import unittest

from nicu_biodesign.platform import DeteriorationPlatform
from nicu_biodesign.vitaldb_api import VitalDBClient


class PlatformTests(unittest.TestCase):
    def test_vitaldb_client_fetches_records_from_api_contract(self) -> None:
        captured_urls: list[str] = []

        def fake_fetcher(url: str) -> bytes:
            captured_urls.append(url)
            return json.dumps({"records": [{"heart_rate": 118, "spo2": 91, "map": 62}]}).encode("utf-8")

        client = VitalDBClient(base_url="https://vitaldb.example/api", api_key="token", fetcher=fake_fetcher)
        records = client.fetch_dataset("nicu-icu", limit=25)

        self.assertEqual(len(records), 1)
        self.assertIn("/records?", captured_urls[0])
        self.assertIn("dataset=nicu-icu", captured_urls[0])
        self.assertIn("limit=25", captured_urls[0])
        self.assertIn("api_key=token", captured_urls[0])

    def test_platform_supports_multiple_data_types_and_architectures(self) -> None:
        payload = {
            "records": [
                {
                    "heart_rate": 124,
                    "spo2": 89,
                    "map": 58,
                    "hrv": 70,
                    "respiratory_rate": 38,
                    "perfusion_index": 1.1,
                    "lactate": 3.5,
                    "wbc": 20.0,
                    "creatinine": 1.7,
                },
                {
                    "heart_rate": 92,
                    "spo2": 96,
                    "map": 74,
                    "hrv": 42,
                    "respiratory_rate": 24,
                    "perfusion_index": 2.4,
                    "lactate": 1.2,
                    "wbc": 11.0,
                    "creatinine": 0.8,
                },
            ]
        }

        client = VitalDBClient(
            base_url="https://vitaldb.example/api",
            fetcher=lambda _: json.dumps(payload).encode("utf-8"),
        )
        platform = DeteriorationPlatform(client)

        experiments = [
            ("vitals", "logistic", "sepsis"),
            ("waveform", "rule_tree", "respiratory_failure"),
            ("labs", "logistic", "hemodynamic_instability"),
        ]
        for data_type, architecture, indication in experiments:
            with self.subTest(data_type=data_type, architecture=architecture, indication=indication):
                result = platform.run_experiment(
                    dataset_id="nicu-icu",
                    data_type=data_type,
                    architecture=architecture,
                    indication=indication,
                )
                self.assertEqual(result.data_type, data_type)
                self.assertEqual(result.architecture, architecture)
                self.assertEqual(result.indication, indication)
                self.assertEqual(result.sample_count, 2)
                self.assertGreaterEqual(result.mean_risk, 0.0)
                self.assertLessEqual(result.mean_risk, 1.0)
                self.assertEqual(len(result.risks), 2)

    def test_platform_rejects_unsupported_configuration(self) -> None:
        client = VitalDBClient(
            base_url="https://vitaldb.example/api",
            fetcher=lambda _: json.dumps({"records": [{"heart_rate": 110}]}).encode("utf-8"),
        )
        platform = DeteriorationPlatform(client)

        with self.assertRaises(ValueError):
            platform.run_experiment(
                dataset_id="nicu-icu",
                data_type="imaging",
                architecture="logistic",
                indication="sepsis",
            )


if __name__ == "__main__":
    unittest.main()
