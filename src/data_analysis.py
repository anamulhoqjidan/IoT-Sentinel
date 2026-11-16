from pathlib import Path
import pandas as pd
import numpy as np

from preprocessing import load_iot23

# Load original dataset
df = load_iot23("data/raw/conn.log.labeled")

print("\n========== DATASET OVERVIEW ==========")

print("Total records:", len(df))
print("Total columns:", len(df.columns))

# Check missing values, including Zeek's '-' marker
df = df.replace("-", np.nan)

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

# Select numerical columns
numeric_columns = [
    "id.orig_p",
    "id.resp_p",
    "duration",
    "orig_bytes",
    "resp_bytes",
    "orig_pkts",
    "resp_pkts"
]

# Convert numerical columns
for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

print("\n========== NUMERICAL FEATURES ==========")
print(df[numeric_columns].describe())

print("\n========== PROTOCOL DISTRIBUTION ==========")
print(df["proto"].value_counts())

print("\n========== CONNECTION STATES ==========")
print(df["conn_state"].value_counts())

print("\n========== LABEL DISTRIBUTION ==========")
print(df["label"].value_counts(dropna=False))

# Add source scenario identifier
df["scenario_id"] = "CTU-Honeypot-Capture-4-1"

# Create output directory
output_dir = Path("data/processed")
output_dir.mkdir(parents=True, exist_ok=True)

# Save cleaned dataset
output_file = output_dir / "benign_cleaned.csv"

df.to_csv(output_file, index=False)

print("\nCleaned dataset saved successfully!")
print("Location:", output_file)