"""
Day 12 — Build LFW Enrollment / Probe Split.

Strategy
--------
The available LFW data uses the InsightFace binary format (lfw.bin), which
packs 12,000 images as ordered pairs without identity folder structure.
Each pair i has:
  - pair_{i:04d}_a.jpg  (side A)
  - pair_{i:04d}_b.jpg  (side B)
  - issame[i] — True iff A and B are the same person

We treat every **genuine** pair (issame=True) as one gallery identity:
  - enrollment → the A-side image
  - probe       → the B-side image

This gives 3,000 identities × 2 images each — exactly the minimum needed for
1:N identification evaluation. The ArcFace embeddings for both sides are
already in lfw_embeddings.npz (no re-extraction required).

Outputs
-------
  data/processed/lfw_enrollment_probe.csv
  data/processed/Face_Database/subject_NNNN/enrollment.jpg  (symlinks)
  data/processed/Face_Database/subject_NNNN/probe.jpg       (symlinks)

Usage
-----
  python scripts/build_enrollment_probe_split.py
"""

import csv
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

LFW_EMB_PATH = ROOT / "data/embeddings_cache/lfw_embeddings.npz"
LFW_EXTRACTED = ROOT / "data/raw/lfw/lfw_extracted"
PROCESSED_DIR  = ROOT / "data/processed"
CSV_OUT        = PROCESSED_DIR / "lfw_enrollment_probe.csv"
DB_ROOT        = PROCESSED_DIR / "Face_Database"

SEED = 42


def main():
    rng = np.random.default_rng(SEED)

    # ── Load issame labels ────────────────────────────────────────────────────
    print("Loading LFW embeddings cache …")
    data   = np.load(str(LFW_EMB_PATH), allow_pickle=True)
    issame = data["issame"].astype(bool)           # (6000,)
    print(f"  Total pairs:   {len(issame)}")
    print(f"  Genuine pairs: {issame.sum()}")
    print(f"  Impostor pairs:{(~issame).sum()}")

    # ── Select genuine pairs → identity set ──────────────────────────────────
    genuine_pair_indices = np.where(issame)[0]     # pair-level indices (0-5999)
    n_identities = len(genuine_pair_indices)

    # Shuffle for reproducibility (seed=42), then assign subject IDs in order
    shuffled = rng.permutation(n_identities)
    genuine_pair_indices = genuine_pair_indices[shuffled]

    # ── Build CSV manifest ────────────────────────────────────────────────────
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DB_ROOT.mkdir(parents=True, exist_ok=True)

    rows = []
    n_enroll = 0
    n_probe  = 0

    for subject_id, pair_idx in enumerate(genuine_pair_indices):
        pair_str   = f"{pair_idx:04d}"
        subject_str = f"{subject_id:04d}"

        img_enroll = LFW_EXTRACTED / f"pair_{pair_str}_a.jpg"
        img_probe  = LFW_EXTRACTED / f"pair_{pair_str}_b.jpg"

        rows.append({
            "identity":   f"subject_{subject_str}",
            "image_path": str(img_enroll),
            "role":       "enrollment",
            "pair_idx":   pair_idx,
            "subject_id": subject_id,
        })
        rows.append({
            "identity":   f"subject_{subject_str}",
            "image_path": str(img_probe),
            "role":       "probe",
            "pair_idx":   pair_idx,
            "subject_id": subject_id,
        })
        n_enroll += 1
        n_probe  += 1

        # Face_Database symlinks per Dr's spec
        subj_dir = DB_ROOT / f"subject_{subject_str}"
        subj_dir.mkdir(exist_ok=True)

        for dst_name, src in [("enrollment.jpg", img_enroll),
                               ("probe.jpg",      img_probe)]:
            link = subj_dir / dst_name
            if link.exists() or link.is_symlink():
                link.unlink()
            os.symlink(src.resolve(), link)

    # Write CSV
    fieldnames = ["identity", "image_path", "role", "pair_idx", "subject_id"]
    with open(CSV_OUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # ── Stats ─────────────────────────────────────────────────────────────────
    print(f"\n✓ Split saved to {CSV_OUT}")
    print(f"\n{'='*50}")
    print(f"  Identities with gallery:   {n_identities:>6,}")
    print(f"  Total enrollment images:   {n_enroll:>6,}")
    print(f"  Total probe images:        {n_probe:>6,}")
    print(f"  Face_Database root:        {DB_ROOT}")
    print(f"{'='*50}\n")

    # Sanity-check: first 5 subjects
    print("Sample subjects:")
    for row in rows[:4]:
        print(f"  {row['identity']}  [{row['role']}]  → {Path(row['image_path']).name}")


if __name__ == "__main__":
    main()
