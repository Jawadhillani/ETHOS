"""
Extract embeddings for FairFace TRAIN set (~86,744 images).

This is the project's primary asset. Once done, all fairness math,
ROC curves, identification experiments, and LLM analysis run on it.

Estimated time: 60-90 minutes on M4 Air with CoreML.
"""

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings.extractor import EmbeddingExtractor
from src.utils.label_mapping import normalize_fairface_labels

BATCH_SIZE = 256


def main():
    project_root = Path(__file__).parent.parent
    fairface_dir  = project_root / "data/raw/fairface"
    labels_csv    = fairface_dir / "fairface_label_train.csv"
    output_path   = project_root / "data/embeddings_cache/fairface_train_embeddings.npz"
    log_path      = project_root / "outputs/logs/fairface_train_extraction.log"

    # ------------------------------------------------------------------
    # Guard: skip if already done
    # ------------------------------------------------------------------
    if output_path.exists():
        data = np.load(str(output_path), allow_pickle=True)
        print(f"✅ Already exists: {output_path}  shape={data['embeddings'].shape}  Skipping.")
        return

    # ------------------------------------------------------------------
    # Load + normalise labels
    # ------------------------------------------------------------------
    print(f"📋 Loading labels from {labels_csv}")
    df = pd.read_csv(labels_csv)
    print(f"   {len(df)} entries")

    # Normalise raw FairFace strings → unified taxonomy
    normalized = df.apply(
        lambda r: normalize_fairface_labels(r["race"], r["gender"], r["age"]),
        axis=1, result_type="expand",
    )
    df["race"]   = normalized["race"]
    df["gender"] = normalized["gender"]
    df["age"]    = normalized["age"]

    image_paths = [str(fairface_dir / f) for f in df["file"]]

    # Sanity check
    if not Path(image_paths[0]).exists():
        print(f"❌ Sample path missing: {image_paths[0]}")
        sys.exit(1)
    print(f"   ✓ Sample image found")

    # ------------------------------------------------------------------
    # Distribution preview
    # ------------------------------------------------------------------
    print(f"\n📊 Distribution preview:")
    print(f"   Race:   {df['race'].value_counts().to_dict()}")
    print(f"   Gender: {df['gender'].value_counts().to_dict()}")

    # ------------------------------------------------------------------
    # Extract
    # ------------------------------------------------------------------
    print(f"\n🚀 Loading ArcFace model (CoreML)...")
    extractor = EmbeddingExtractor()

    print(f"\n🔍 Extracting {len(image_paths)} images in batches of {BATCH_SIZE}...")
    print(f"   ETA: ~60-90 minutes. Progress bar updates live.\n")

    all_embeddings  = []
    all_valid_paths = []
    all_indices     = []   # original df row index for label alignment

    t0 = time.time()

    for start in range(0, len(image_paths), BATCH_SIZE):
        batch_paths   = image_paths[start: start + BATCH_SIZE]
        batch_indices = list(range(start, min(start + BATCH_SIZE, len(image_paths))))
        total         = len(image_paths)

        embs, valid_paths = extractor.extract_batch(
            batch_paths,
            error_log=str(log_path),
            desc=f"FairFace train [{start+1}-{min(start+BATCH_SIZE, total)}/{total}]",
        )

        path_to_idx = {p: i for i, p in zip(batch_indices, batch_paths)}
        for path, emb in zip(valid_paths, embs):
            all_embeddings.append(emb)
            all_valid_paths.append(path)
            all_indices.append(path_to_idx[path])

    elapsed_min = (time.time() - t0) / 60
    n_ok   = len(all_embeddings)
    n_fail = len(image_paths) - n_ok

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------
    print(f"\n📊 Results:")
    print(f"   ✓ Successful: {n_ok}")
    print(f"   ✗ Failed:     {n_fail}")
    print(f"   Success rate: {n_ok / len(image_paths) * 100:.2f}%")
    print(f"   Wall time:    {elapsed_min:.1f} min")
    print(f"   Throughput:   {n_ok / (elapsed_min * 60):.1f} img/sec")

    # ------------------------------------------------------------------
    # Build aligned label arrays
    # ------------------------------------------------------------------
    df_aligned = df.iloc[all_indices].reset_index(drop=True)

    emb_array = np.stack(all_embeddings, axis=0)  # (N, 512)

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        str(output_path),
        embeddings = emb_array,
        filenames  = np.array(all_valid_paths, dtype=object),
        race       = np.array(df_aligned["race"].values,   dtype=object),
        gender     = np.array(df_aligned["gender"].values, dtype=object),
        age        = np.array(df_aligned["age"].values,    dtype=object),
    )
    size_mb = output_path.stat().st_size / 1024 / 1024
    print(f"\n💾 Saved → {output_path}  ({size_mb:.1f} MB)")

    # ------------------------------------------------------------------
    # Verify
    # ------------------------------------------------------------------
    saved = np.load(str(output_path), allow_pickle=True)
    norms = np.linalg.norm(saved["embeddings"], axis=1)

    print(f"\n✅ Verification:")
    print(f"   Shape:       {saved['embeddings'].shape}")
    print(f"   Norm range:  [{norms.min():.4f}, {norms.max():.4f}]")
    print(f"   File size:   {size_mb:.1f} MB")

    print(f"\n📈 Per-race counts after extraction:")
    races, counts = np.unique(saved["race"], return_counts=True)
    for r, c in sorted(zip(races, counts), key=lambda x: -x[1]):
        print(f"   {r:<20s}: {c}")

    print(f"\n📈 Per-gender counts:")
    genders, gcounts = np.unique(saved["gender"], return_counts=True)
    for g, c in zip(genders, gcounts):
        print(f"   {g}: {c}")

    print(f"\n🎉 FairFace train extraction complete. Core asset ready for Week 4 fairness math.")


if __name__ == "__main__":
    main()
