# NetShieldX — Week 1 Technical Handover

**Project:** NetShieldX — AI-Based IoT Botnet Detection and Agentic Network Security Response  
**Repository:** IoT-Sentinel  
**Student:** AHAMMED TANIM  
**Role:** MQTT Infrastructure, Traffic Replay and System Integration  
**Week:** 1 — Dataset Foundation and MQTT Communication

---

## 1. Overview

During Week 1, my responsibility was to establish the MQTT communication infrastructure and develop a traffic replay mechanism using the prepared IoT-23 network-flow dataset.

The purpose of this implementation is to simulate IoT network traffic by publishing selected network-flow records as structured JSON messages through an MQTT broker.

These messages will later be consumed by the machine learning inference service and the NetShieldX security agent.

The implementation uses a local Mosquitto MQTT broker and Python's Paho-MQTT library.

## 2. Development Environment

| Component | Configuration |
|---|---|
| Programming language | Python |
| MQTT Broker | Eclipse Mosquitto |
| MQTT Client Library | Paho-MQTT 2.2.0 |
| Dataset | IoT-23 |
| Data Processing | Pandas |
| Communication Protocol | MQTT |
| MQTT QoS | 1 |
| Broker Host | localhost |
| Broker Port | 1883 |
| MQTT Topic | `iot/device01/traffic` |

## 3. Implemented Components

### 3.1 MQTT Traffic Publisher

**File:** `src/traffic_replay.py`

This component reads network-flow records from the processed IoT-23 dataset and publishes them as MQTT messages.

Main responsibilities:

- Load the processed dataset.
- Validate the required dataset columns.
- Select a specified number of network-flow records.
- Convert each record into a structured JSON event.
- Generate a unique event ID.
- Include device ID, scenario ID and timestamp.
- Publish messages to the MQTT broker.
- Save ground-truth labels separately for evaluation.

The publisher supports configurable replay options through command-line arguments:

```bash
python src/traffic_replay.py --limit 10 --interval 1
```

**Parameters:**

- `--limit`: Number of network-flow records to replay.
- `--interval`: Delay between consecutive messages in seconds.

### 3.2 MQTT Subscriber

**File:** `src/mqtt_test.py`

The subscriber connects to the local MQTT broker and listens for incoming network traffic events.

Its responsibilities include:

- Establish an MQTT connection.
- Subscribe to `iot/device01/traffic`.
- Receive published JSON messages.
- Display the MQTT topic and received message.

This component verifies that the publisher and broker communicate successfully.

### 3.3 MQTT Broker

Mosquitto was installed and tested locally.

The broker was successfully started using:

```powershell
& "C:\Program Files\Mosquitto\mosquitto.exe" -v
```

The broker listens on port 1883 in local-only mode.

The Windows service configuration was not required for development because running Mosquitto manually worked successfully.

## 4. MQTT Event Structure

The publisher currently produces the following JSON structure:

```json
{
  "event_id": "evt-000001",
  "device_id": "device01",
  "scenario_id": "CTU-Honeypot-Capture-4-1",
  "timestamp": 1795356362.259459,
  "features": {
    "id.orig_p": 58687,
    "id.resp_p": 123,
    "proto": "udp",
    "service": null,
    "duration": 0.114184,
    "orig_bytes": 48.0,
    "resp_bytes": 48.0,
    "conn_state": "SF",
    "orig_pkts": 1,
    "resp_pkts": 1
  }
}
```

### Network-flow features

The following ten features are included:

1. `id.orig_p` — Originator port
2. `id.resp_p` — Responder port
3. `proto` — Network protocol
4. `service` — Application service
5. `duration` — Connection duration
6. `orig_bytes` — Originator bytes
7. `resp_bytes` — Responder bytes
8. `conn_state` — Connection state
9. `orig_pkts` — Originator packets
10. `resp_pkts` — Responder packets

**Important data separation:**

The `target` field is not included in MQTT messages.

- `target = 0`: Benign traffic
- `target = 1`: Malicious traffic

Ground-truth labels are retained separately for later evaluation. The `scenario_id` is included as event metadata and is not one of the ten model input features.

The JSON structure is the current implementation format and requires joint approval from both teammates before being treated as the final integration contract.

## 5. Ground-Truth Storage

After replaying traffic, the publisher saves evaluation labels to:

```text
results/replay_ground_truth.csv
```

The file contains:

| Field | Description |
|---|---|
| `event_id` | Unique event identifier |
| `scenario_id` | Original dataset scenario |
| `target` | Actual classification label |

This allows future comparison between the classifier's predictions and the actual dataset labels without exposing the ground truth to the prediction service.

The generated CSV is excluded from Git using `.gitignore`.

## 6. Testing and Validation

The local MQTT pipeline was successfully tested using the following three processes:

| Terminal | Process |
|---|---|
| Terminal 1 | Mosquitto MQTT broker |
| Terminal 2 | MQTT subscriber |
| Terminal 3 | Dataset traffic publisher |

### Test execution

Publisher:

```bash
python src/traffic_replay.py --limit 10 --interval 1
```

Subscriber:

```bash
python src/mqtt_test.py
```

### Test results

| Validation | Result |
|---|---|
| Mosquitto broker startup | Successful |
| Publisher connection | Successful |
| Subscriber connection | Successful |
| MQTT subscription | Successful |
| Messages published | 10 |
| Messages received | 10 |
| MQTT topic | Correct |
| JSON event structure | Received successfully |
| Ground-truth CSV generation | Successful |
| Ground-truth separation | Verified |

### Initial dataset test observation

The first ten selected records all had `target = 0`.

Therefore, the initial test verified MQTT communication using benign traffic only.

A separate malicious traffic replay test remains necessary.

## 7. GitHub Contribution

The implementation was committed and pushed successfully.

**Repository:**

`https://github.com/anamulhoqjidan/IoT-Sentinel`

**Branch:**

`feature/tanim-mqtt-agent`

**Commit:**

`ef3d594`

**Commit message:**

`Add MQTT traffic replay and subscriber`

### Files included in the commit

- `.gitignore`
- `requirements.txt`
- `src/mqtt_test.py`
- `src/traffic_replay.py`

The branch was successfully pushed to GitHub and is one commit ahead of `main`. No changes were merged into the main branch.

## 8. Current Limitations and Pending Improvements

The following tasks remain before final Week 1 sign-off:

1. Make MQTT broker host, port, topic and device configuration environment-based.
2. Add publisher filtering for benign and malicious traffic.
3. Improve subscriber-side JSON parsing and message validation.
4. Test at least one benign and one malicious network-flow event.
5. Confirm the final MQTT JSON schema with Jidan.
6. Confirm whether the instructor requires a shared MQTT broker, credentials or a different topic structure.
7. Complete joint testing and documentation.

These are pending improvements and have not yet been claimed as completed.

## 9. Integration Responsibilities

### Tanim — Student B

- MQTT broker setup.
- MQTT traffic publisher.
- MQTT subscriber.
- Traffic replay mechanism.
- Security agent.
- Response tools.
- SQLite database.
- Streamlit dashboard.
- System integration and testing.

### Jidan — Student A

- IoT-23 dataset preparation.
- Feature and label documentation.
- Dataset preprocessing.
- Machine learning classifier.
- Prediction interface.
- Model evaluation.

Both students must agree on the final feature names and JSON event contract before integrating the publisher with the ML inference service.

## 10. Week 1 Handover Status

**Completed by Tanim:**

- Local Mosquitto broker setup and testing.
- MQTT publisher implementation.
- MQTT subscriber implementation.
- IoT-23 dataset replay.
- Initial JSON event structure.
- Ground-truth separation.
- Successful ten-event communication test.
- GitHub commit and push.

**Pending joint verification:**

- Shared broker requirements.
- Final MQTT event schema approval.
- Malicious traffic replay demonstration.
- Jidan's dataset documentation and scenario verification.
- Week 1 problem card and one-page system design.
- Progress meeting record and instructor feedback.

### Final Status

Tanim's initial MQTT implementation is completed, tested locally and pushed to the feature branch.

The overall Week 1 milestone remains pending joint verification and completion of the remaining documentation and testing requirements.

---

**Prepared by:** AHAMMED TANIM  
**Project:** NetShieldX  
**Development Branch:** `feature/tanim-mqtt-agent`