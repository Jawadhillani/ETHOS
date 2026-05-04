"""
Extract ArcFace embeddings for FairFace (val) and LFW pairs.

Run from project root:
    conda run -n ethos python scripts/extract_embeddings.py

Outputs:
    data/embeddings_cache/fairface_val_embeddings.npz
    data/embeddings_cache/lfw_embeddings.npz
    outputs/logs/extraction_errors.log
"""

import logging
import sys
import time
from pathlib import Path

import numpy as np

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings.extractor import EmbeddingExtractor
from src.utils.dataset_loader import load_fairface, load_lfw_pairs

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_FILE = Path("outputs/logs/extraction_errors.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE),
    ],
)
log = logging.getLogger(__name__)

BATCH_SIZE = 256
CACHE_DIR = Path("data/embeddings_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def process_in_batches(extractor, image_paths, labels_df, output_path, desc):
    """
    Extract embeddings in BATCH_SIZE chunks, accumulate, then save once.
    Keeps peak memory low for large splits.
    """
    all_embeddings = []
    all_paths = []
    all_indices = []  # original df row index for label alignment

    total = len(image_paths)
    log.info(f"Starting {desc}: {total} images → {output_path}")
    t0 = time.time()

    for start in range(0, total, BATCH_SIZE):
        batch_paths = image_paths[start: start + BATCH_SIZE]
        batch_indices = list(range(start, min(start + BATCH_SIZE, total)))

        embs, valid_paths = extractor.extract_batch(
            batch_paths,
            error_log=str(LOG_FILE),
            desc=f"{desc} [{start+1}-{min(start+BATCH_SIZE, total)}/{total}]",
        )

        # Match valid paths back to their original indices
        path_to_idx = {str(p): i for i, p in zip(batch_indices, batch_paths)}
        for path, emb in zip(valid_paths, embs):
            all_embeddings.append(emb)
            all_paths.append(path)
            all_indices.append(path_to_idx[path])

    elapsed = time.time() - t0
    n = len(all_embeddings)
    log.info(f"Done: {n}/{total} embeddings extracted in {elapsed:.1f}s "
             f"({elapsed/max(n,1)*1000:.1f}ms/img)")

    # Build label arrays aligned to valid paths
    labels = {}
    if labels_df is not None:
        for col in ["race", "gender", "age"]:
            if col in labels_df.columns:
                labels[col] = np.array(
                    labels_df.iloc[all_indices][col].values, dtype=object
                )

    extractor.save_embeddings(all_embeddings, all_paths, output_path, labels=labels)
    return n


def verify_embeddings(npz_path, dataset_name):
    """Load saved embeddings and print a quick sanity report."""
    data = np.load(str(npz_path), allow_pickle=True)
    embs = data["embeddings"]
    fnames = data["filenames"]

    norms = np.linalg.norm(embs, axis=1)
    log.info(f"\n{'='*50}")
    log.info(f"Verification: {dataset_name}")
    log.info(f"  Shape:      {embs.shape}")
    log.info(f"  Norm range: {norms.min():.4f} – {norms.max():.4f} (expect ~1.0)")

    if "race" in data:
        unique, counts = np.unique(data["race"], return_counts=True)
        log.info(f"  Race distribution:")
        for race, count in sorted(zip(unique, counts), key=lambda x: -x[1]):
            log.info(f"    {race:<20s}: {count}")

    if "gender" in data:
        unique, counts = np.unique(data["gender"], return_counts=True)
        log.info(f"  Gender: { {k: int(v) for k, v in zip(unique, counts)} }")

    log.info(f"{'='*50}\n")


def spot_check_lfw(npz_path):
    """Verify same-person similarity > different-person on 5 random LFW pairs."""
    data = np.load(str(npz_path), allow_pickle=True)
    embs = data["embeddings"]
    filenames = data["filenames"]
    issame = data["issame"]

    # Build lookup: filename → embedding
    fname_to_emb = {str(f): embs[i] for i, f in enumerate(filenames)}

    from src.utils.dataset_loader import load_lfw_pairs
    df = load_lfw_pairs()

    rng = np.random.default_rng(42)
    same_pairs = df[df["same_person"]].sample(5, random_state=42)
    diff_pairs = df[~df["same_person"]].sample(5, random_state=42)

    log.info("LFW spot-check (cosine similarity):")
    log.info("  Same-person pairs (expect > 0.5):")
    for _, row in same_pairs.iterrows():
        a = fname_to_emb.get(row["img1_path"])
        b = fname_to_emb.get(row["img2_path"])
        if a is not None and b is not None:
            log.info(f"    pair {row['pair_id']}: {float(np.dot(a, b)):.4f}")

    log.info("  Different-person pairs (expect < 0.3):")
    for _, row in diff_pairs.iterrows():
        a = fname_to_emb.get(row["img1_path"])
        b = fname_to_emb.get(row["img2_path"])
        if a is not None and b is not None:
            log.info(f"    pair {row['pair_id']}: {float(np.dot(a, b)):.4f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log.info("Initialising EmbeddingExtractor (CoreML)...")
    extractor = EmbeddingExtractor()

    # ------------------------------------------------------------------
    # 1. FairFace val (10,954 images — full split, validates pipeline)
    # ------------------------------------------------------------------
    fairface_out = CACHE_DIR / "fairface_val_embeddings.npz"
    if fairface_out.exists():
        log.info(f"FairFace val embeddings already exist at {fairface_out}, skipping.")
    else:
        df_val = load_fairface("val")
        n = process_in_batches(
            extractor,
            image_paths=df_val["img_path"].tolist(),
            labels_df=df_val,
            output_path=fairface_out,
            desc="FairFace val",
        )
        log.info(f"FairFace val complete: {n} embeddings saved.")

    verify_embeddings(fairface_out, "FairFace val")

    # ------------------------------------------------------------------
    # 2. LFW pairs (12,000 images — 6,000 pairs, pre-cropped 112×112 chips)
    # ------------------------------------------------------------------
    lfw_out = CACHE_DIR / "lfw_embeddings.npz"
    if lfw_out.exists():
        log.info(f"LFW embeddings already exist at {lfw_out}, deleting stale file.")
        lfw_out.unlink()

    df_lfw = load_lfw_pairs()
    # Interleave a/b so pair_i → embs[i*2], embs[i*2+1]
    interleaved = []
    for _, row in df_lfw.iterrows():
        interleaved.extend([row["img1_path"], row["img2_path"]])

    # Use extract_chips_batch — bypasses RetinaFace for pre-cropped images
    all_embeddings, all_paths = extractor.extract_chips_batch(
        interleaved,
        error_log=str(LOG_FILE),
        desc="LFW chips",
    )

    issame_arr = np.array(df_lfw["same_person"].tolist())

    extractor.save_embeddings(
        all_embeddings,
        all_paths,
        lfw_out,
        labels={"issame": issame_arr},
    )
    log.info(f"LFW complete: {len(all_embeddings)} embeddings saved.")

    verify_embeddings(lfw_out, "LFW")
    spot_check_lfw(lfw_out)

    log.info("Day 3 extraction complete. All embeddings cached.")


if __name__ == "__main__":
    main()
