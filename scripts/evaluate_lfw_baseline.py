"""
Day 4 baseline: evaluate the matching engine on LFW's 6,000 standard pairs.

LFW provides 6,000 pre-defined pairs:
  - 3,000 same-person pairs (positive)
  - 3,000 different-person pairs (negative)

Embeddings are stored as interleaved pairs in lfw_embeddings.npz:
  pair_i → embeddings[i*2], embeddings[i*2+1]
  issame  → boolean array of length 6,000 (also inside the .npz)
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.matching.engine import MatchingEngine


def main():
    project_root = Path(__file__).parent.parent
    lfw_emb_path = project_root / "data/embeddings_cache/lfw_embeddings.npz"

    # ---------------------------------------------------------------
    # Load embeddings
    # ---------------------------------------------------------------
    print(f"📥 Loading LFW embeddings from {lfw_emb_path}")
    data = np.load(str(lfw_emb_path), allow_pickle=True)
    embeddings = data["embeddings"]   # (12000, 512)
    issame     = data["issame"]       # (6000,) bool — stored in same .npz

    print(f"   Loaded {embeddings.shape[0]} embeddings ({embeddings.shape[0] // 2} pairs)")
    print(f"   issame labels: {issame.shape[0]} entries "
          f"({int(issame.sum())} same, {int((~issame).sum())} different)")

    # ---------------------------------------------------------------
    # Split into pair components (interleaved layout)
    # ---------------------------------------------------------------
    embs_a = embeddings[0::2]   # (6000, 512)
    embs_b = embeddings[1::2]   # (6000, 512)

    # ---------------------------------------------------------------
    # Matching engine
    # ---------------------------------------------------------------
    engine = MatchingEngine(threshold=0.55)
    similarities = engine.cosine_similarity_batch(embs_a, embs_b)

    # ---------------------------------------------------------------
    # Score distribution
    # ---------------------------------------------------------------
    print(f"\n📊 Similarity score distribution:")
    print(f"   Same-person     — mean: {similarities[issame].mean():.4f}  "
          f"median: {np.median(similarities[issame]):.4f}  "
          f"std: {similarities[issame].std():.4f}")
    print(f"   Different-person — mean: {similarities[~issame].mean():.4f}  "
          f"median: {np.median(similarities[~issame]):.4f}  "
          f"std: {similarities[~issame].std():.4f}")
    gap = similarities[issame].mean() - similarities[~issame].mean()
    print(f"   Separation (mean gap): {gap:.4f}")

    # ---------------------------------------------------------------
    # Accuracy @ 0.55
    # ---------------------------------------------------------------
    predictions = engine.decide_batch(similarities)
    accuracy    = (predictions == issame).mean()

    tp = int((predictions &  issame).sum())   # correct same
    tn = int((~predictions & ~issame).sum())  # correct different
    fp = int((predictions  & ~issame).sum())  # false accept
    fn = int((~predictions &  issame).sum())  # false reject

    far = fp / int((~issame).sum()) * 100
    frr = fn / int(issame.sum())   * 100

    print(f"\n✅ Baseline results @ threshold=0.55:")
    print(f"   Total accuracy:           {accuracy*100:.2f}%")
    print(f"   Correct same-person:      {tp}/{int(issame.sum())}  ({tp/int(issame.sum())*100:.2f}%)")
    print(f"   Correct different-person: {tn}/{int((~issame).sum())}  ({tn/int((~issame).sum())*100:.2f}%)")

    print(f"\n📉 Error breakdown:")
    print(f"   False Accepts (impostors accepted): {fp}")
    print(f"   False Rejects (genuine pairs rejected): {fn}")
    print(f"   FAR = {far:.2f}%")
    print(f"   FRR = {frr:.2f}%")

    print(f"\n🎯 Day 4 baseline complete.")
    print(f"   In Week 3 we'll sweep thresholds to find EER and plot ROC/DET curves.")


if __name__ == "__main__":
    main()
