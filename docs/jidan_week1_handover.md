# IoT Sentinel — Week 1 Handover

**Student:** Jidan  
**Role:** Dataset Preparation and Machine Learning  
**Project:** IoT Sentinel — AI-Based Botnet Detection and Network Security Agent

## 1. Work Completed

During Week 1, I successfully prepared the IoT-23 network traffic dataset for our AIoT security project.

The completed tasks include:

- Setting up the Python development environment.
- Downloading four IoT-23 traffic capture scenarios.
- Loading labeled Zeek network connection logs.
- Cleaning and combining benign and malicious traffic records.
- Converting traffic labels into binary classification targets.
- Selecting network-flow features for machine learning.
- Generating four dataset visualization graphs.

## 2. Dataset Information

**Source:** IoT-23 Dataset, Stratosphere Laboratory, Czech Technical University.

**Official website:** https://www.stratosphereips.org/datasets-iot23

Four capture scenarios were selected:

| Capture scenario | Benign | Malicious |
|---|---:|---:|
| CTU-Honeypot-Capture-4-1 | 452 | 0 |
| CTU-Honeypot-Capture-5-1 | 1,374 | 0 |
| CTU-IoT-Malware-Capture-34-1 | 1,923 | 21,222 |
| CTU-IoT-Malware-Capture-3-1 | 4,536 | 151,567 |
| **Total** | **8,285** | **172,789** |

The combined dataset contains **181,074 network-flow records**.

## 3. Selected Network Features

The following ten network-flow features were selected:

1. Source port (`id.orig_p`)
2. Destination port (`id.resp_p`)
3. Protocol (`proto`)
4. Service (`service`)
5. Connection duration (`duration`)
6. Originator bytes (`orig_bytes`)
7. Responder bytes (`resp_bytes`)
8. Connection state (`conn_state`)
9. Originator packets (`orig_pkts`)
10. Responder packets (`resp_pkts`)

Two additional columns are included:

- `scenario_id`: Identifies the original network capture.
- `target`: Binary classification label.

The target labels are:

- `0` = Benign traffic
- `1` = Malicious traffic

The `scenario_id` and `target` fields must not be used as machine learning input features.

## 4. Dataset Preprocessing

The preprocessing workflow performs the following operations:

1. Loads labeled Zeek network logs.
2. Combines records from the four capture scenarios.
3. Replaces missing-value markers (`-`) with missing values.
4. Normalizes benign and malicious labels.
5. Converts the target labels into numerical values.
6. Converts numerical network features into appropriate data types.
7. Preserves the original capture identifier.
8. Saves the processed dataset as a CSV file.

**Processed dataset location:**

`data/processed/iot23_combined.csv`

The original dataset files remain unchanged.

## 5. Data Analysis Results

**Total network flows:** 181,074

**Benign traffic:** 8,285

**Malicious traffic:** 172,789

**Protocol distribution:**

- TCP: 176,113
- UDP: 3,668
- ICMP: 1,293

The dataset is highly imbalanced, with approximately 95.4% malicious traffic.

## 6. Missing Values

The processed dataset contains:

| Feature | Missing values |
|---|---:|
| `service` | 172,152 |
| `duration` | 92,067 |
| `orig_bytes` | 92,067 |
| `resp_bytes` | 92,067 |

These missing values have been preserved for the machine learning preprocessing stage.

## 7. Generated Visualizations

Four graphs were generated and saved inside `results/figures/`:

- `class_distribution.png`
- `protocol_distribution.png`
- `connection_states.png`
- `duration_distribution.png`

These graphs demonstrate the distribution of traffic classes, protocols, connection states, and durations.

## 8. Python Files

| File | Purpose |
|---|---|
| `preprocessing.py` | Loads the original IoT-23 Zeek logs |
| `data_analysis.py` | Analyzes and cleans network traffic |
| `combine_datasets.py` | Combines all four capture scenarios |
| `visualize_data.py` | Generates dataset visualizations |

## 9. How to Run

From the project root directory, activate the Python virtual environment.

Run:

```powershell
python src/combine_datasets.py
```

This generates the combined dataset.

Then run:

```powershell
python src/visualize_data.py
```

This generates the dataset visualization graphs.

## 10. Known Limitations

The dataset contains significantly more malicious traffic than benign traffic.

Only four capture scenarios are currently included, limiting evaluation across different IoT devices and malware behaviors.

Some network-flow features have high missing-value rates.

To reduce data leakage, model development should use scenario-separated training and testing rather than a random split of all records.

## 11. Next Steps for Jidan

During Week 2:

1. Prepare scenario-separated training and testing datasets.
2. Apply random undersampling to training data only.
3. Handle missing values and encode categorical features.
4. Train a Random Forest classifier.
5. Evaluate model performance using precision, recall, F1-score, confusion matrix, and false-positive rate.
6. Save the trained model for system integration.

## 12. Next Steps for Tanim

Tanim will use the processed dataset to develop a Python network traffic replay simulator.

The simulator will:

1. Read network-flow records from the processed dataset.
2. Convert records into structured JSON messages.
3. Publish the messages through MQTT.
4. Simulate network traffic from IoT devices.
5. Send network events to the machine learning inference service.

The `target` and `scenario_id` columns must not be sent to the prediction model as input features.

Ground-truth labels should be retained separately for evaluation.

## 13. Integration Agreement

Both students will use the same ten network-flow features.

The trained machine learning model will classify each network event as benign or malicious.

The AI security agent will use the prediction and additional context to determine whether to:

- Continue monitoring.
- Log suspicious activity.
- Generate a security alert.
- Create a security incident.
- Request simulated device isolation with administrator approval.

All security actions will be software simulations and will not modify real network firewall rules.