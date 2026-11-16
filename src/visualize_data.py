from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Load processed dataset
df = pd.read_csv("data/processed/iot23_combined.csv")

# Create output folder
output_dir = Path("results/figures")
output_dir.mkdir(parents=True, exist_ok=True)


print("Dataset loaded successfully!")
print("Total records:", len(df))


# =====================================
# 1. BENIGN VS MALICIOUS DISTRIBUTION
# =====================================

label_counts = df["target"].value_counts().reindex(
    [0, 1], fill_value=0
)

plt.figure(figsize=(7, 5))

plt.bar(
    ["Benign", "Malicious"],
    label_counts.values
)

plt.title("IoT-23 Traffic Class Distribution")
plt.xlabel("Traffic Class")
plt.ylabel("Number of Network Flows")

plt.tight_layout()

plt.savefig(
    output_dir / "class_distribution.png",
    dpi=300
)

plt.close()

print("Saved: class_distribution.png")


# =====================================
# 2. NETWORK PROTOCOL DISTRIBUTION
# =====================================

protocol_counts = df["proto"].value_counts()

plt.figure(figsize=(7, 5))

plt.bar(
    protocol_counts.index.astype(str),
    protocol_counts.values
)

plt.title("Network Protocol Distribution")
plt.xlabel("Protocol")
plt.ylabel("Number of Network Flows")

plt.tight_layout()

plt.savefig(
    output_dir / "protocol_distribution.png",
    dpi=300
)

plt.close()

print("Saved: protocol_distribution.png")


# =====================================
# 3. CONNECTION STATE DISTRIBUTION
# =====================================

state_counts = df["conn_state"].value_counts().head(10)

plt.figure(figsize=(9, 5))

plt.bar(
    state_counts.index.astype(str),
    state_counts.values
)

plt.title("Top 10 Network Connection States")
plt.xlabel("Connection State")
plt.ylabel("Number of Flows")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    output_dir / "connection_states.png",
    dpi=300
)

plt.close()

print("Saved: connection_states.png")


# =====================================
# 4. CONNECTION DURATION DISTRIBUTION
# =====================================

duration = pd.to_numeric(
    df["duration"],
    errors="coerce"
)

duration = duration[
    duration.notna() & (duration >= 0)
]

plt.figure(figsize=(8, 5))

plt.hist(
    np.log1p(duration),
    bins=40
)

plt.title("Network Connection Duration")
plt.xlabel("log(1 + Duration in Seconds)")
plt.ylabel("Number of Network Flows")

plt.tight_layout()

plt.savefig(
    output_dir / "duration_distribution.png",
    dpi=300
)

plt.close()

print("Saved: duration_distribution.png")


# =====================================
# 5. DATASET SUMMARY
# =====================================

print("\n========== DATASET SUMMARY ==========")

print("\nTraffic classes:")
print(df["target"].value_counts())

print("\nProtocols:")
print(df["proto"].value_counts())

print("\nCapture scenarios:")
print(df["scenario_id"].value_counts())

print("\nAll graphs saved successfully!")