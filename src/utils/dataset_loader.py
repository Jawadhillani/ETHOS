"""
Dataset loader for ETHOS.

Supports:
- FairFace (train + val splits, 7-class race taxonomy)
  Images: data/raw/fairface/train/ and data/raw/fairface/val/
  Labels: data/raw/fairface/fairface_label_{train,val}.csv

- LFW (InsightFace binary eval format, extracted to pair images)
  Source: lfw.bin binary → extracted to data/raw/lfw/lfw_extracted/
  Pairs:  pair_XXXX_a.jpg / pair_XXXX_b.jpg + issame.npy (6000 pairs)

- RFW (4-class taxonomy, loaded only when available)

All returned records use the unified taxonomy from label_mapping.py.
"""

import csv
from pathlib import Path

import numpy as np
import pandas as pd

from src.utils.label_mapping import normalize_fairface_labels, to_rfw_race

# ---------------------------------------------------------------------------
# Paths (relative to project root — callers should chdir or pass root)
# ---------------------------------------------------------------------------

DATA_ROOT = Path("data/raw")
FAIRFACE_ROOT = DATA_ROOT / "fairface"
LFW_EXTRACTED = DATA_ROOT / "lfw" / "lfw_extracted"
RFW_ROOT = DATA_ROOT / "rfw"


# ---------------------------------------------------------------------------
# FairFace
# ---------------------------------------------------------------------------

def load_fairface(split: str = "train") -> pd.DataFrame:
    """
    Load FairFace labels for a given split.

    Args:
        split: 'train' or 'val'

    Returns:
        DataFrame with columns:
            file, img_path, race, gender, age, rfw_race
    """
    assert split in ("train", "val"), "split must be 'train' or 'val'"
    label_file = FAIRFACE_ROOT / f"fairface_label_{split}.csv"

    if not label_file.exists():
        raise FileNotFoundError(
            f"FairFace labels not found at {label_file}. "
            "Run scripts/download_fairface.py first."
        )

    df = pd.read_csv(label_file)

    # Normalise to unified taxonomy
    normalized = df.apply(
        lambda row: normalize_fairface_labels(row["race"], row["gender"], row["age"]),
        axis=1,
        result_type="expand",
    )
    df["race"] = normalized["race"]
    df["gender"] = normalized["gender"]
    df["age"] = normalized["age"]

    # Absolute image path
    df["img_path"] = df["file"].apply(lambda f: str(FAIRFACE_ROOT / f))

    # Pre-compute RFW-compatible race label for cross-dataset experiments
    df["rfw_race"] = df["race"].apply(to_rfw_race)

    return df[["file", "img_path", "race", "gender", "age", "rfw_race"]]


def fairface_distribution(split: str = "train") -> dict:
    """Return label distribution counts for a FairFace split."""
    df = load_fairface(split)
    return {
        "race": df["race"].value_counts().to_dict(),
        "gender": df["gender"].value_counts().to_dict(),
        "age": df["age"].value_counts().to_dict(),
        "total": len(df),
    }


# ---------------------------------------------------------------------------
# LFW  (InsightFace binary eval format — 6 000 pairs, 112×112 aligned)
# ---------------------------------------------------------------------------

def load_lfw_pairs() -> pd.DataFrame:
    """
    Load LFW evaluation pairs from the extracted InsightFace binary pack.

    Source binary: data/raw/lfw/lfw_align_112/lfw.bin
    Extracted by:  scripts/extract_lfw_bin.py  (run once)
    Output layout: data/raw/lfw/lfw_extracted/
                     pair_XXXX_a.jpg
                     pair_XXXX_b.jpg
                     issame.npy

    Returns:
        DataFrame with columns:
            pair_id, img1_path, img2_path, same_person (bool)
    """
    if not LFW_EXTRACTED.exists():
        raise FileNotFoundError(
            f"LFW extracted images not found at {LFW_EXTRACTED}. "
            "Run: python -c \"import pickle,numpy as np; ... \" (see dataset_loader.py)"
        )

    issame = np.load(str(LFW_EXTRACTED / "issame.npy"))
    records = []
    for i, same in enumerate(issame):
        pid = f"{i:04d}"
        records.append((
            pid,
            str(LFW_EXTRACTED / f"pair_{pid}_a.jpg"),
            str(LFW_EXTRACTED / f"pair_{pid}_b.jpg"),
            bool(same),
        ))

    return pd.DataFrame(records, columns=["pair_id", "img1_path", "img2_path", "same_person"])


def lfw_stats() -> dict:
    """Return basic statistics about the LFW eval set."""
    df = load_lfw_pairs()
    return {
        "total_pairs": len(df),
        "same_person": int(df["same_person"].sum()),
        "different_person": int((~df["same_person"]).sum()),
    }


# ---------------------------------------------------------------------------
# RFW (optional — only loaded if present)
# ---------------------------------------------------------------------------

def rfw_available() -> bool:
    """Return True if RFW data has been downloaded."""
    return RFW_ROOT.exists() and any(RFW_ROOT.iterdir())


def load_rfw(race: str) -> pd.DataFrame:
    """
    Load RFW pairs for a single race split.

    Args:
        race: one of 'Caucasian', 'African', 'Asian', 'Indian'

    Returns:
        DataFrame with columns:
            name1, img1_path, name2, img2_path, same_person, race
    """
    if not rfw_available():
        raise RuntimeError("RFW dataset not present. Set rfw.enabled=true in config.")

    pairs_file = RFW_ROOT / "txts" / race / f"{race}_pairs.txt"
    if not pairs_file.exists():
        raise FileNotFoundError(f"RFW pairs file not found: {pairs_file}")

    records = []
    with open(pairs_file) as f:
        next(f)  # skip header
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 3:
                name, idx1, idx2 = parts
                img1 = str(RFW_ROOT / "data" / race / name / f"{name}_{int(idx1):04d}.jpg")
                img2 = str(RFW_ROOT / "data" / race / name / f"{name}_{int(idx2):04d}.jpg")
                records.append((name, img1, name, img2, True, race))
            elif len(parts) == 4:
                n1, idx1, n2, idx2 = parts
                img1 = str(RFW_ROOT / "data" / race / n1 / f"{n1}_{int(idx1):04d}.jpg")
                img2 = str(RFW_ROOT / "data" / race / n2 / f"{n2}_{int(idx2):04d}.jpg")
                records.append((n1, img1, n2, img2, False, race))

    df = pd.DataFrame(
        records,
        columns=["name1", "img1_path", "name2", "img2_path", "same_person", "race"],
    )
    return df


# ---------------------------------------------------------------------------
# Integrity check
# ---------------------------------------------------------------------------

def verify_dataset(name: str, sample_n: int = 5) -> dict:
    """
    Quick integrity check: count files, verify a sample exist on disk.

    Args:
        name: 'fairface_train', 'fairface_val', or 'lfw'

    Returns:
        dict with 'total', 'missing', 'sample_ok'
    """
    if name in ("fairface_train", "fairface_val"):
        split = name.split("_")[1]
        df = load_fairface(split)
        sample = df["img_path"].sample(min(sample_n, len(df)), random_state=42)
        missing = [p for p in sample if not Path(p).exists()]
        return {"total": len(df), "missing_in_sample": len(missing), "sample_ok": len(missing) == 0}

    if name == "lfw":
        stats = lfw_stats()
        sample_img = LFW_EXTRACTED / "pair_0000_a.jpg"
        return {**stats, "sample_ok": sample_img.exists()}

    raise ValueError(f"Unknown dataset name: {name}")
