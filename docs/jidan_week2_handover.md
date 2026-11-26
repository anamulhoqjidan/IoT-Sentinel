# IoT Sentinel — Week 2 Handover

**Module / owner / week:** Botnet classifier and prediction interface / Jidan / Week 2
**Branch:** `jidan-week2`

## 1. What is finished

- Scenario-based train / validation / test split of the IoT-23 data.
- Balanced training set (equal benign and malicious rows) using random undersampling.
- Decision Tree baseline and Random Forest classifier.
- Decision threshold chosen on validation data.
- Saved model (preprocessing + Random Forest + threshold in one file).
- `predict_flow(event)` that classifies one MQTT event.
- Unit tests (normal and failure cases).

## 2. Files changed

| File | Purpose |
|---|---|
| `src/preprocess_flows.py` | Splits data by capture, removes duplicates, balances training set |
| `src/train_model.py` | Trains Decision Tree and Random Forest, chooses threshold, saves model |
| `src/predict.py` | `predict_flow(event)` for one MQTT event |
| `tests/test_model.py` | 9 unit tests for `predict_flow` |
| `results/validation_summary.json` | Validation scores and chosen thresholds |

## 3. Data split

The data is split **by capture**, so the test captures are never seen during training.

| Set | Captures | Benign | Malicious |
|---|---|---:|---:|
| Train (balanced) | CTU-IoT-Malware-Capture-3-1, CTU-Honeypot-Capture-5-1 | 3,774 | 3,774 |
| Validation (real ratio) | 20% of the training captures | 944 | 22,792 |
| Test (real ratio) | CTU-IoT-Malware-Capture-34-1, CTU-Honeypot-Capture-4-1 | 1,228 | 7,045 |

- 54,124 exact duplicate rows were removed inside each capture.
- Only the training set is balanced. Validation and test keep the real class ratio.
- The original file `data/processed/iot23_combined.csv` is not changed.

## 4. Model

- **Input features (10):** `id.orig_p`, `id.resp_p`, `proto`, `service`, `duration`, `orig_bytes`, `resp_bytes`, `conn_state`, `orig_pkts`, `resp_pkts`
- **Not used as features:** `scenario_id`, `target`, `event_id`, `device_id`, `timestamp`
- **Missing numbers:** replaced with -1, plus an extra "was missing" indicator column.
- **Text features:** missing → `"missing"`, then one-hot encoded. Unknown categories are ignored, not an error.
- **Chosen model:** Random Forest (100 trees, max depth 15).
- **Decision threshold:** 0.25 (chosen on validation data using macro F1).

## 5. Validation results

| Model | Threshold | Macro F1 | False positive rate |
|---|---:|---:|---:|
| Decision Tree | 0.05 | 0.9992 | 0.000 |
| Random Forest | 0.25 | 0.9997 | 0.000 |

**Important:** validation rows come from the same captures as the training rows, so these scores are too optimistic. The real measure is the held-out test captures, which will be fully reported in Week 4. A first check on the test captures gave about 78% accuracy, with about 25% of malicious flows missed, which shows the model does not transfer perfectly to a new capture.

## 6. How to run and test

From the project folder, with the virtual environment active:

```
python src/preprocess_flows.py
python src/train_model.py
python src/predict.py
python -m unittest tests/test_model.py -v
```

The model file `models/iot_botnet_model.joblib` is excluded from Git by `.gitignore`. Run the first two commands once to create it.

## 7. How Tanim uses it

Run code from the project folder, then:

```python
from src.predict import predict_flow

result = predict_flow(event)   # event = one MQTT message, already parsed from JSON
```

The model is loaded once on the first call and reused after that.

## 8. Input example → output example

**Input** (same format as `traffic_replay.py` publishes):

```json
{
  "event_id": "evt-demo-002",
  "device_id": "device01",
  "scenario_id": "CTU-IoT-Malware-Capture-34-1",
  "timestamp": 0,
  "features": {
    "id.orig_p": 48986, "id.resp_p": 6667, "proto": "tcp",
    "service": null, "duration": 3.107733,
    "orig_bytes": 0.0, "resp_bytes": 0.0,
    "conn_state": "S0", "orig_pkts": 3, "resp_pkts": 0
  }
}
```

**Output:**

```json
{"event_id": "evt-demo-002", "device_id": "device01",
 "predicted_label": "malicious", "malicious_probability": 0.79}
```

A benign test row (`evt-demo-001`, Honeypot-4-1, UDP port 123) gives `"predicted_label": "benign", "malicious_probability": 0.0`.

## 9. Normal test / failure test

- **Normal:** output has the 4 agreed fields; IDs pass through; probability is between 0 and 1; label matches the threshold; known benign and malicious examples are classified correctly.
- **Failure:** a missing feature does not crash; unknown protocol / connection state does not crash; an event without `features` raises `ValueError`.

Result: 9 tests, all pass.

## 10. Known issues and limitations

- Validation scores are near 100% but do not reflect performance on unseen captures (see section 5).
- Only 4 captures are used, so the model has seen few devices and malware types.
- The malicious probability is a model score, not a calibrated real-world risk.
- `scenario_id` is passed through in events but must never be used for prediction.
- The model file is not in Git; it must be created locally by running the training script.

## 11. Next integration step

- Tanim: build `decide_action(...)` using the output format in section 8. Suggested risk bands should be agreed together; the model threshold is 0.25.
- Both: run `predict_flow(sample)` → `decide_action(...)` without MQTT before Week 3.
- Jidan (Week 3): `inference_service.py` that subscribes to MQTT, calls `predict_flow`, and forwards the result to the agent.

## 12. Partner verification

- Verified by Tanim: ☐   Date: __________
