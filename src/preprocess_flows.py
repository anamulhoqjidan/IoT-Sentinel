"""
IoT Sentinel - Week 2, Step 1
Split the IoT-23 data into train / validation / test sets.

Rules:
- Split by CAPTURE (scenario), not by random rows, so the model is tested
  on traffic from captures it has never seen.
- Remove exact duplicate rows inside each capture.
- Balance ONLY the training set (same number of benign and malicious rows).
- Validation and test sets keep their real class ratio.

The original file data/processed/iot23_combined.csv is NOT changed.
"""

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


# ==========================================
# 1. SETTINGS
# ==========================================

INPUT_FILE = Path("data/processed/iot23_combined.csv")
OUTPUT_DIR = Path("data/splits")

RANDOM_SEED = 42

# Captures used for training (and validation)
TRAIN_SCENARIOS = [
    "CTU-IoT-Malware-Capture-3-1",
    "CTU-Honeypot-Capture-5-1",
]

# Captures kept completely separate for the final test
TEST_SCENARIOS = [
    "CTU-IoT-Malware-Capture-34-1",
    "CTU-Honeypot-Capture-4-1",
]

# Share of the training captures held back for validation
VALIDATION_SIZE = 0.2


def show_counts(name, df):
    benign = (df["target"] == 0).sum()
    malicious = (df["target"] == 1).sum()
    print(f"{name:<12} total={len(df):>7}  benign={benign:>6}  malicious={malicious:>7}")


def main():

    # ==========================================
    # 2. LOAD DATA
    # ==========================================

    df = pd.read_csv(INPUT_FILE)
    print("Loaded rows:", len(df))

    # ==========================================
    # 3. REMOVE DUPLICATES (inside each capture)
    # ==========================================
    # scenario_id is part of the row, so identical flows from
    # different captures are kept; only copies within one capture go.

    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    print("Removed duplicates:", before - len(df))

    # ==========================================
    # 4. SPLIT BY CAPTURE
    # ==========================================

    train_pool = df[df["scenario_id"].isin(TRAIN_SCENARIOS)]
    test_df = df[df["scenario_id"].isin(TEST_SCENARIOS)]

    # Safety check: no capture may appear in both sets
    overlap = set(train_pool["scenario_id"]) & set(test_df["scenario_id"])
    if overlap:
        raise ValueError(f"Capture used in both train and test: {overlap}")

    # ==========================================
    # 5. HOLD OUT VALIDATION DATA
    # ==========================================
    # Done BEFORE balancing, so validation keeps the real class ratio.
    # Used later to choose the decision threshold.

    train_df, val_df = train_test_split(
        train_pool,
        test_size=VALIDATION_SIZE,
        stratify=train_pool["target"],
        random_state=RANDOM_SEED,
    )

    # ==========================================
    # 6. BALANCE THE TRAINING SET ONLY
    # ==========================================
    # Keep all benign rows, randomly pick the same number of malicious rows.

    benign_rows = train_df[train_df["target"] == 0]
    malicious_rows = train_df[train_df["target"] == 1]

    malicious_sample = malicious_rows.sample(
        n=len(benign_rows),
        random_state=RANDOM_SEED,
    )

    train_balanced = (
        pd.concat([benign_rows, malicious_sample])
        .sample(frac=1, random_state=RANDOM_SEED)   # shuffle
        .reset_index(drop=True)
    )

    # ==========================================
    # 7. SAVE
    # ==========================================

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    train_balanced.to_csv(OUTPUT_DIR / "train.csv", index=False)
    val_df.to_csv(OUTPUT_DIR / "validation.csv", index=False)
    test_df.to_csv(OUTPUT_DIR / "test.csv", index=False)

    # ==========================================
    # 8. SUMMARY
    # ==========================================

    print("\n========== SPLIT SUMMARY ==========")
    print("Train captures:", TRAIN_SCENARIOS)
    print("Test captures: ", TEST_SCENARIOS)
    print()
    show_counts("Train", train_balanced)
    show_counts("Validation", val_df)
    show_counts("Test", test_df)
    print("\nTest rows per capture:")
    print(test_df.groupby(["scenario_id", "target"]).size())
    print("\nSaved to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
