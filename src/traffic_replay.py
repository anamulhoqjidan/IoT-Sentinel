
import argparse
import json
import time
from pathlib import Path
from threading import Event

import pandas as pd
import paho.mqtt.client as mqtt


# ==========================================
# 1. MQTT CONFIGURATION
# ==========================================

BROKER = "localhost"
PORT = 1883
TOPIC = "iot/device01/traffic"

DATASET_PATH = "data/processed/iot23_combined.csv"

DEVICE_ID = "device01"


# ==========================================
# 2. NETWORK FLOW FEATURES
# ==========================================

FEATURE_COLUMNS = [
    "id.orig_p",
    "id.resp_p",
    "proto",
    "service",
    "duration",
    "orig_bytes",
    "resp_bytes",
    "conn_state",
    "orig_pkts",
    "resp_pkts"
]

# Connection event
connected = Event()


# ==========================================
# 3. MQTT CALLBACK
# ==========================================

def on_connect(client, userdata, flags, reason_code, properties):

    if reason_code.is_failure:
        print(f"MQTT connection failed: {reason_code}")
        return

    print("Connected to MQTT Broker!")
    connected.set()


# ==========================================
# 4. HANDLE MISSING VALUES
# ==========================================

def clean_value(value):

    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


# ==========================================
# 5. LOAD IOT-23 DATASET
# ==========================================

def load_dataset(limit):

    print("\nLoading IoT-23 dataset...")

    if not Path(DATASET_PATH).exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    required_columns = FEATURE_COLUMNS + [
        "scenario_id",
        "target"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing dataset columns: {missing_columns}"
        )

    print(f"Total records available: {len(df)}")

    df = df.head(limit).copy()

    print(f"Records selected for replay: {len(df)}")

    return df


# ==========================================
# 6. CREATE NETWORK EVENT
# ==========================================

def create_event(row, event_number):

    features = {
        column: clean_value(row[column])
        for column in FEATURE_COLUMNS
    }

    event = {
        "event_id": f"evt-{event_number:06d}",
        "device_id": DEVICE_ID,
        "scenario_id": row["scenario_id"],
        "timestamp": time.time(),
        "features": features
    }

    return event


# ==========================================
# 7. TRAFFIC REPLAY
# ==========================================

def replay_traffic(client, df, interval):

    ground_truth = []

    print(f"\nStarting traffic replay...")
    print(f"MQTT Topic: {TOPIC}")
    print("-" * 50)

    for index, (_, row) in enumerate(df.iterrows(), start=1):

        # Create JSON event
        event = create_event(row, index)

        message = json.dumps(event)

        # Publish MQTT message
        info = client.publish(
            TOPIC,
            message,
            qos=1
        )

        info.wait_for_publish(timeout=10)

        if not info.is_published():
            raise RuntimeError(
                f"Failed to publish event {event['event_id']}"
            )

        # Store ground truth separately
        ground_truth.append({
            "event_id": event["event_id"],
            "scenario_id": row["scenario_id"],
            "target": int(row["target"])
        })

        print(
            f"Published {event['event_id']} | "
            f"Protocol: {event['features']['proto']} | "
            f"Scenario: {row['scenario_id']}"
        )

        if index < len(df):
            time.sleep(interval)

    return ground_truth


# ==========================================
# 8. MAIN FUNCTION
# ==========================================

def main():

    parser = argparse.ArgumentParser(
        description="NetShieldX IoT Traffic Replay Simulator"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of network records to replay"
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Delay between events in seconds"
    )

    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be at least 1")

    if args.interval < 0:
        parser.error("--interval cannot be negative")

    # Load dataset
    df = load_dataset(args.limit)

    # Create MQTT publisher
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="netshieldx_publisher"
    )

    client.on_connect = on_connect

    try:

        print("\nConnecting to MQTT Broker...")

        client.connect(BROKER, PORT, 60)
        client.loop_start()

        if not connected.wait(timeout=10):
            raise TimeoutError(
                "Could not connect to MQTT Broker"
            )

        # Replay actual IoT-23 records
        ground_truth = replay_traffic(
            client,
            df,
            args.interval
        )

        # Save evaluation labels separately
        output_path = Path("results/replay_ground_truth.csv")
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        pd.DataFrame(ground_truth).to_csv(
            output_path,
            index=False
        )

        print("-" * 50)
        print(f"Replay completed successfully!")
        print(f"Total events published: {len(df)}")
        print(f"Ground truth saved: {output_path}")

    finally:

        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    main()
