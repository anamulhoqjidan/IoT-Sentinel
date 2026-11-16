from pathlib import Path
import pandas as pd


def load_iot23(filepath):
    filepath = Path(filepath)

    columns = None
    records = []

    with filepath.open(
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:

        for line in file:

            if line.startswith("#fields"):
                columns = line.split()[1:]
                continue

            if line.startswith("#"):
                continue

            if not line.strip():
                continue

            values = line.split()

            if len(values) != len(columns):
                raise ValueError(
                    f"Expected {len(columns)} columns, "
                    f"found {len(values)}"
                )

            records.append(values)

    return pd.DataFrame(records, columns=columns)


if __name__ == "__main__":

    df = load_iot23("data/raw/conn.log.labeled")

    print("\nDataset loaded successfully!")

    print("\nDataset shape:", df.shape)

    print("\nLast three columns:")
    print(df[
        ["tunnel_parents", "label", "detailed-label"]
    ].head())

    print("\nLabel distribution:")
    print(df["label"].value_counts(dropna=False))

    print("\nMissing labels:")
    print(df["label"].isna().sum())