"""
IoT Sentinel - Week 2, Step 3
predict_flow(event): classify ONE network-flow event.

Input:  an event in the agreed MQTT format (same as traffic_replay.py):
    {
        "event_id": "evt-000001",
        "device_id": "device01",
        "scenario_id": "...",
        "timestamp": 1795356362.26,
        "features": {"id.orig_p": 58687, "id.resp_p": 123, "proto": "udp", ...}
    }

Output:
    {
        "event_id": "evt-000001",
        "device_id": "device01",
        "predicted_label": "benign" or "malicious",
        "malicious_probability": 0.03
    }

Run src/train_model.py first to create models/iot_botnet_model.joblib.
"""

import json
from pathlib import Path

import joblib
import pandas as pd


MODEL_FILE = Path("models/iot_botnet_model.joblib")

# The model is loaded once and then reused for every event
_model_bundle = None


def load_model():
    global _model_bundle

    if _model_bundle is None:
        if not MODEL_FILE.exists():
            raise FileNotFoundError(
                f"Model not found: {MODEL_FILE}. "
                "Run: python src/train_model.py"
            )
        _model_bundle = joblib.load(MODEL_FILE)

    return _model_bundle


def predict_flow(event):

    bundle = load_model()
    pipeline = bundle["pipeline"]
    threshold = bundle["threshold"]
    features = bundle["features"]

    if "features" not in event or not isinstance(event["features"], dict):
        raise ValueError("Event has no 'features' dictionary")

    # Build a one-row table with the 10 features in the right order.
    # A feature that is absent becomes missing (None); the model's
    # preprocessing handles missing values the same way as in training.
    row = {name: event["features"].get(name) for name in features}
    X = pd.DataFrame([row], columns=features)

    probability = float(pipeline.predict_proba(X)[0, 1])

    if probability >= threshold:
        label = "malicious"
    else:
        label = "benign"

    return {
        "event_id": event.get("event_id"),
        "device_id": event.get("device_id"),
        "predicted_label": label,
        "malicious_probability": round(probability, 4),
    }


# ==========================================
# DEMO: run this file directly to test it
# ==========================================

if __name__ == "__main__":

    # Both examples are real rows from the TEST captures
    # (not used for training).
    benign_event = {
        "event_id": "evt-demo-001",
        "device_id": "device01",
        "scenario_id": "CTU-Honeypot-Capture-4-1",
        "timestamp": 0,
        "features": {
            "id.orig_p": 58687,
            "id.resp_p": 123,
            "proto": "udp",
            "service": None,
            "duration": 0.114184,
            "orig_bytes": 48.0,
            "resp_bytes": 48.0,
            "conn_state": "SF",
            "orig_pkts": 1,
            "resp_pkts": 1,
        },
    }

    malicious_event = {
        "event_id": "evt-demo-002",
        "device_id": "device01",
        "scenario_id": "CTU-IoT-Malware-Capture-34-1",
        "timestamp": 0,
        "features": {
            "id.orig_p": 48986,
            "id.resp_p": 6667,
            "proto": "tcp",
            "service": None,
            "duration": 3.107733,
            "orig_bytes": 0.0,
            "resp_bytes": 0.0,
            "conn_state": "S0",
            "orig_pkts": 3,
            "resp_pkts": 0,
        },
    }

    print("Threshold used:", load_model()["threshold"])

    for event in [benign_event, malicious_event]:
        print("\nInput: ", event["event_id"], event["features"])
        print("Output:", json.dumps(predict_flow(event)))
