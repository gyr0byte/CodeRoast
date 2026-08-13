"""
CodeRoast — Dataset Preprocessor
Cleans, normalizes, deduplicates, and splits scraped code samples
into a ready-to-train dataset.

Usage:
    python data/preprocess_dataset.py

Input:  data/raw/scraped_code.csv
Output: data/processed/code_samples.csv
"""

import os
import sys
import hashlib
import pandas as pd
from sklearn.model_selection import train_test_split

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config


def load_raw_data() -> pd.DataFrame:
    """Load the raw scraped dataset."""
    filepath = config.DATA_RAW_DIR / "scraped_code.csv"
    if not filepath.exists():
        print(f"[ERROR] Raw data not found at: {filepath}")
        print("Run the scraping script first: python data/scrape_github.py")
        sys.exit(1)

    df = pd.read_csv(filepath)
    print(f"[INFO] Loaded {len(df)} raw samples")
    return df


def clean_code(code: str) -> str:
    """Clean and normalize a code snippet."""
    if not isinstance(code, str):
        return ""

    # Remove trailing whitespace from each line
    lines = [line.rstrip() for line in code.splitlines()]

    # Remove leading/trailing blank lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    return "\n".join(lines)


def compute_hash(code: str) -> str:
    """Compute a hash for deduplication."""
    # Normalize whitespace for comparison
    normalized = " ".join(code.split())
    return hashlib.md5(normalized.encode()).hexdigest()


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full preprocessing pipeline:
    1. Clean code
    2. Remove empty/too-short samples
    3. Remove duplicates
    4. Balance class distribution
    """
    print("\n[Step 1] Cleaning code...")
    df["code"] = df["code"].apply(clean_code)

    # Remove empty or too-short samples
    df = df[df["code"].str.len() > 50].copy()
    print(f"  After removing short samples: {len(df)}")

    # Remove samples that are too long (>100 lines)
    df = df[df["code"].apply(lambda x: len(x.splitlines()) <= 100)].copy()
    print(f"  After removing long samples: {len(df)}")

    print("\n[Step 2] Removing duplicates...")
    df["_hash"] = df["code"].apply(compute_hash)
    before = len(df)
    df = df.drop_duplicates(subset=["_hash"]).copy()
    df = df.drop(columns=["_hash"])
    print(f"  Removed {before - len(df)} duplicates. Remaining: {len(df)}")

    print("\n[Step 3] Balancing class distribution...")
    # Find the minimum class size and undersample larger classes
    class_counts = df["quality_label"].value_counts()
    print(f"  Before balancing: {class_counts.to_dict()}")

    min_count = class_counts.min()
    balanced_dfs = []
    for label in sorted(df["quality_label"].unique()):
        class_df = df[df["quality_label"] == label]
        if len(class_df) > min_count:
            class_df = class_df.sample(n=min_count, random_state=42)
        balanced_dfs.append(class_df)

    df = pd.concat(balanced_dfs, ignore_index=True)
    print(f"  After balancing: {df['quality_label'].value_counts().to_dict()}")

    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    return df


def save_dataset(df: pd.DataFrame) -> None:
    """Save the processed dataset."""
    os.makedirs(config.DATA_PROCESSED_DIR, exist_ok=True)
    output_path = config.DATA_PROCESSED_DIR / "code_samples.csv"
    df.to_csv(output_path, index=False)
    print(f"\n[SAVED] Processed dataset: {output_path}")
    print(f"        Total samples: {len(df)}")
    print(f"        Languages: {df['language'].value_counts().to_dict()}")
    print(f"        Quality labels: {df['quality_label'].value_counts().to_dict()}")


def main():
    print("CodeRoast — Dataset Preprocessor")
    print("=" * 60)

    df = load_raw_data()
    df = preprocess(df)
    save_dataset(df)

    print(f"\n{'='*60}")
    print("✅ Dataset ready for training!")
    print("Next step: python -m src.ml.train")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
