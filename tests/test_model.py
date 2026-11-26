"""
IoT Sentinel - Week 2, Step 4
Automatic checks for predict_flow().

Run from the project folder:
    python -m unittest tests/test_model.py -v

Needs the trained model: run python src/train_model.py first.
"""

import copy
import unittest

from src.predict import load_model, predict_flow


# Real rows from the TEST captures (not used for training)
BENIGN_EVENT = {
    "event_id": "evt-test-benign",
    "device_id": "device01",
    "scenario_id": "CTU-Honeypot-Capture-4-1",
    "timestamp": 0,
    "features": {
        "id.orig_p": 58687, "id.resp_p": 123, "proto": "udp",
        "service": None, "duration": 0.114184,
        "orig_bytes": 48.0, "resp_bytes": 48.0,
        "conn_state": "SF", "orig_pkts": 1, "resp_pkts": 1,
    },
}

MALICIOUS_EVENT = {
    "event_id": "evt-test-malicious",
    "device_id": "device01",
    "scenario_id": "CTU-IoT-Malware-Capture-34-1",
    "timestamp": 0,
    "features": {
        "id.orig_p": 48986, "id.resp_p": 6667, "proto": "tcp",
        "service": None, "duration": 3.107733,
        "orig_bytes": 0.0, "resp_bytes": 0.0,
        "conn_state": "S0", "orig_pkts": 3, "resp_pkts": 0,
    },
}


class TestPredictFlow(unittest.TestCase):

    # ---------- normal tests ----------

    def test_output_has_agreed_fields(self):
        result = predict_flow(BENIGN_EVENT)
        self.assertEqual(
            set(result.keys()),
            {"event_id", "device_id", "predicted_label", "malicious_probability"},
        )

    def test_ids_are_passed_through(self):
        result = predict_flow(BENIGN_EVENT)
        self.assertEqual(result["event_id"], "evt-test-benign")
        self.assertEqual(result["device_id"], "device01")

    def test_probability_is_between_0_and_1(self):
        for event in [BENIGN_EVENT, MALICIOUS_EVENT]:
            p = predict_flow(event)["malicious_probability"]
            self.assertGreaterEqual(p, 0.0)
            self.assertLessEqual(p, 1.0)

    def test_label_matches_threshold(self):
        threshold = load_model()["threshold"]
        for event in [BENIGN_EVENT, MALICIOUS_EVENT]:
            result = predict_flow(event)
            expected = (
                "malicious"
                if result["malicious_probability"] >= threshold
                else "benign"
            )
            self.assertEqual(result["predicted_label"], expected)

    def test_known_benign_example(self):
        self.assertEqual(predict_flow(BENIGN_EVENT)["predicted_label"], "benign")

    def test_known_malicious_example(self):
        self.assertEqual(predict_flow(MALICIOUS_EVENT)["predicted_label"], "malicious")

    # ---------- failure tests ----------

    def test_missing_feature_does_not_crash(self):
        event = copy.deepcopy(BENIGN_EVENT)
        del event["features"]["duration"]
        result = predict_flow(event)
        self.assertIn(result["predicted_label"], ["benign", "malicious"])

    def test_unknown_category_does_not_crash(self):
        event = copy.deepcopy(BENIGN_EVENT)
        event["features"]["proto"] = "some_new_protocol"
        event["features"]["conn_state"] = "NEW_STATE"
        result = predict_flow(event)
        self.assertIn(result["predicted_label"], ["benign", "malicious"])

    def test_event_without_features_is_rejected(self):
        with self.assertRaises(ValueError):
            predict_flow({"event_id": "evt-bad", "device_id": "device01"})


if __name__ == "__main__":
    unittest.main()
