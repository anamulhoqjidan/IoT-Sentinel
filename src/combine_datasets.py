from pathlib import Path
import pandas as pd
import numpy as np

from preprocessing import load_iot23


# ==========================================
# 1. DEFINE DATASET LOCATIONS
# ==========================================

datasets = {
    "CTU-Honeypot-Capture-4-1":
        "data/raw/conn.log.labeled",

    "CTU-Honeypot-Capture-5-1":
        "data/raw/CTU-Honeypot-Capture-5-1/conn.log.labeled",

    "CTU-IoT-Malware-Capture-34-1":
        "data/raw/CTU-IoT-Malware-Capture-34-1/conn.log.labeled",

    "CTU-IoT-Malware-Capture-3-1":
        "data/raw/CTU-IoT-Malware-Capture-3-1/conn.log.labeled"
}


# ==========================================
# 2. LOAD ALL FOUR DATASETS
# ==========================================

all_data = []

print("\n========== LOADING DATASETS ==========")

for scenario_name, filepath in datasets.items():

    print(f"\nLoading: {scenario_name}")

    df = load_iot23(filepath)

    print("Records:", len(df))
    print("Columns:", len(df.columns))

    # Preserve original capture identity
    df["scenario_id"] = scenario_name

    all_data.append(df)


# ==========================================
# 3. COMBINE DATASETS
# ==========================================

combined_df = pd.concat(
    all_data,
    ignore_index=True
)

print("\nAll datasets combined successfully!")

print("Total records:", len(combined_df))


# ==========================================
# 4. HANDLE MISSING VALUES
# ==========================================

# Zeek uses '-' for unavailable values
combined_df = combined_df.replace("-", np.nan)


# ==========================================
# 5. NORMALIZE TRAFFIC LABELS
# ==========================================

combined_df["label"] = (
    combined_df["label"]
    .astype(str)
    .str.strip()
    .str.lower()
)

label_mapping = {
    "benign": 0,
    "malicious": 1
}

combined_df["target"] = (
    combined_df["label"].map(label_mapping)
)

# Check for unexpected labels
if combined_df["target"].isna().any():

    print("\nUnexpected labels detected:")

    print(
        combined_df.loc[
            combined_df["target"].isna(),
            "label"
        ].value_counts()
    )

    raise ValueError(
        "Unknown labels found. Check dataset."
    )


combined_df["target"] = (
    combined_df["target"].astype(int)
)


# ==========================================
# 6. CONVERT NUMERICAL FEATURES
# ==========================================

numeric_columns = [
    "id.orig_p",
    "id.resp_p",
    "duration",
    "orig_bytes",
    "resp_bytes",
    "orig_pkts",
    "resp_pkts"
]

for col in numeric_columns:

    combined_df[col] = pd.to_numeric(
        combined_df[col],
        errors="coerce"
    )


# ==========================================
# 7. SELECT MACHINE LEARNING FEATURES
# ==========================================

selected_columns = [
    "scenario_id",
    "id.orig_p",
    "id.resp_p",
    "proto",
    "service",
    "duration",
    "orig_bytes",
    "resp_bytes",
    "conn_state",
    "orig_pkts",
    "resp_pkts",
    "target"
]

processed_df = combined_df[
    selected_columns
].copy()


# ==========================================
# 8. SAVE FINAL DATASET
# ==========================================

output_dir = Path("data/processed")

output_dir.mkdir(
    parents=True,
    exist_ok=True
)

output_file = output_dir / "iot23_combined.csv"

processed_df.to_csv(
    output_file,
    index=False
)


# ==========================================
# 9. VERIFY THE COMBINED DATASET
# ==========================================

print("\n========== FINAL DATASET SUMMARY ==========")

print("\nTotal records:")
print(len(processed_df))

print("\nTotal columns:")
print(len(processed_df.columns))

print("\nClass distribution:")
print(
    processed_df["target"].value_counts()
)

print("\nScenario distribution:")
print(
    processed_df.groupby(
        ["scenario_id", "target"]
    ).size()
)

print("\nMissing target labels:")
print(
    processed_df["target"].isna().sum()
)

print("\nMissing feature values:")
print(
    processed_df.isna().sum()
)

print("\nDataset saved successfully!")
print("Location:", output_file)