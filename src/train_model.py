"""
IoT Sentinel - Week 2, Step 2
Train a Decision Tree (baseline) and a Random Forest on the balanced
training set, compare them on the validation set, choose a decision
threshold, and save the best model.

Run src/preprocess_flows.py first to create data/splits/.

The TEST set is NOT used here. It is kept for the final evaluation.
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier


# ==========================================
# 1. SETTINGS
# ==========================================

SPLIT_DIR = Path("data/splits")
MODEL_DIR = Path("models")
RESULTS_DIR = Path("results")

RANDOM_SEED = 42

# The 10 agreed input features (same names as in Tanim's MQTT events)
NUMERIC_FEATURES = [
    "id.orig_p",
    "id.resp_p",
    "duration",
    "orig_bytes",
    "resp_bytes",
    "orig_pkts",
    "resp_pkts",
]

CATEGORICAL_FEATURES = [
    "proto",
    "service",
    "conn_state",
]

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "target"


# ==========================================
# 2. PREPROCESSING
# ==========================================
# Everything here is fitted on the TRAINING data only.
#
# Numbers:  missing values -> -1, plus an extra "was missing" column
#           (a missing duration usually means the connection never
#           completed, which is useful information).
# Text:     missing values -> "missing", then one-hot encoding.
#           Categories never seen in training are ignored, not an error.

def build_preprocessor():

    numeric_steps = SimpleImputer(
        strategy="constant",
        fill_value=-1,
        add_indicator=True,
    )

    categorical_steps = Pipeline([
        ("fill", SimpleImputer(strategy="constant", fill_value="missing")),
        ("encode", OneHotEncoder(handle_unknown="ignore")),
    ])

    return ColumnTransformer([
        ("num", numeric_steps, NUMERIC_FEATURES),
        ("cat", categorical_steps, CATEGORICAL_FEATURES),
    ])


def build_models():

    decision_tree = Pipeline([
        ("prep", build_preprocessor()),
        ("model", DecisionTreeClassifier(
            max_depth=10,
            random_state=RANDOM_SEED,
        )),
    ])

    random_forest = Pipeline([
        ("prep", build_preprocessor()),
        ("model", RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            random_state=RANDOM_SEED,
            n_jobs=-1,
        )),
    ])

    return {
        "Decision Tree": decision_tree,
        "Random Forest": random_forest,
    }


# ==========================================
# 3. HELPERS
# ==========================================

def load_split(name):
    df = pd.read_csv(SPLIT_DIR / f"{name}.csv")
    return df[FEATURES], df[TARGET]


def false_positive_rate(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return fp / (fp + tn) if (fp + tn) else 0.0


def choose_threshold(y_true, probabilities):
    # Try thresholds 0.05 ... 0.95 and keep the one with the best
    # macro F1 (average of benign F1 and malicious F1), so that
    # neither class is ignored.
    best_threshold, best_score = 0.5, -1.0

    for threshold in np.arange(0.05, 0.96, 0.05):
        predictions = (probabilities >= threshold).astype(int)
        score = f1_score(y_true, predictions, average="macro")
        if score > best_score:
            best_threshold, best_score = float(threshold), score

    return round(best_threshold, 2), best_score


def report(name, y_true, y_pred):
    print(f"\n----- {name} -----")
    print(classification_report(
        y_true, y_pred,
        labels=[0, 1],
        target_names=["benign", "malicious"],
        digits=3,
        zero_division=0,
    ))
    print("Confusion matrix (rows = actual, columns = predicted):")
    print("              benign  malicious")
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    print(f"benign      {cm[0, 0]:>8} {cm[0, 1]:>10}")
    print(f"malicious   {cm[1, 0]:>8} {cm[1, 1]:>10}")
    print(f"False positive rate: {false_positive_rate(y_true, y_pred):.3f}")


# ==========================================
# 4. MAIN
# ==========================================

def main():

    X_train, y_train = load_split("train")
    X_val, y_val = load_split("validation")

    print("Training rows:  ", len(X_train), dict(y_train.value_counts()))
    print("Validation rows:", len(X_val), dict(y_val.value_counts()))

    models = build_models()
    summary = {}

    for name, pipeline in models.items():

        print(f"\n========== {name.upper()} ==========")

        pipeline.fit(X_train, y_train)

        probabilities = pipeline.predict_proba(X_val)[:, 1]

        # Default threshold 0.5
        default_pred = (probabilities >= 0.5).astype(int)
        report(f"{name} on validation (threshold 0.50)", y_val, default_pred)

        # Threshold chosen on validation data
        threshold, macro_f1 = choose_threshold(y_val, probabilities)
        tuned_pred = (probabilities >= threshold).astype(int)
        report(f"{name} on validation (threshold {threshold:.2f})", y_val, tuned_pred)

        summary[name] = {
            "threshold": threshold,
            "validation_macro_f1": round(macro_f1, 4),
            "validation_false_positive_rate": float(round(
                false_positive_rate(y_val, tuned_pred), 4)
            ),
        }

    # ==========================================
    # 5. SAVE THE RANDOM FOREST
    # ==========================================
    # Preprocessing + model + threshold are saved together in ONE file,
    # so predict.py only needs to load this file.

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    model_file = MODEL_DIR / "iot_botnet_model.joblib"

    joblib.dump(
        {
            "pipeline": models["Random Forest"],
            "threshold": summary["Random Forest"]["threshold"],
            "features": FEATURES,
        },
        model_file,
    )

    with open(RESULTS_DIR / "validation_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n========== SUMMARY ==========")
    for name, values in summary.items():
        print(name, values)
    print("\nSaved model:", model_file)
    print("Saved summary:", RESULTS_DIR / "validation_summary.json")


if __name__ == "__main__":
    main()
