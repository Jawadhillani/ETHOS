"""
PairBuilder: constructs genuine and impostor pairs for fairness evaluation.

Strategy (Option 1 hybrid):
  - Genuine pairs: LFW (same person, different photos) → overall FRR only,
    since LFW has no demographic labels. Documented limitation.
  - Impostor pairs: FairFace, stratified by demographic group.
    Pairs are drawn WITHIN each group (different identities, same demographic)
    to measure per-group FAR — the key fairness signal.
"""

import numpy as np
from typing import Dict


class PairBuilder:
    """Builds genuine and impostor pairs for biometric fairness evaluation."""

    def __init__(self, random_seed: int = 42):
        self.rng = np.random.default_rng(random_seed)

    def get_lfw_genuine_scores(
        self,
        lfw_embeddings: np.ndarray,
        lfw_issame: np.ndarray,
    ) -> np.ndarray:
        """
        Extract genuine pair similarity scores from LFW.

        LFW format: 12,000 embeddings = 6,000 pairs (interleaved).
        issame[i] = True for genuine pair at rows 2i, 2i+1.

        Returns: 1-D array of cosine similarities for genuine pairs only.
        """
        embs_a = lfw_embeddings[0::2].astype(np.float32, copy=False)
        embs_b = lfw_embeddings[1::2].astype(np.float32, copy=False)
        sims = np.sum(embs_a * embs_b, axis=1)
        return sims[lfw_issame.astype(bool)]

    def build_impostor_pairs_per_group(
        self,
        embeddings: np.ndarray,
        group_labels: np.ndarray,
        n_pairs_per_group: int = 50_000,
    ) -> Dict[str, np.ndarray]:
        """
        Build impostor pair similarity scores stratified by demographic group.

        For each unique group value, randomly samples up to n_pairs_per_group
        distinct within-group pairs (i ≠ j), computes cosine similarity for each.

        Args:
            embeddings:        (N, 512) float32 face embeddings
            group_labels:      (N,) array of demographic labels
            n_pairs_per_group: max impostor pairs sampled per group

        Returns:
            {group_name: 1-D array of cosine similarities}
        """
        embeddings = embeddings.astype(np.float32, copy=False)
        groups = np.unique(group_labels)
        scores_by_group: Dict[str, np.ndarray] = {}

        for group in groups:
            group_indices = np.where(group_labels == group)[0]
            n = len(group_indices)

            if n < 2:
                print(f"  Skipping '{group}': only {n} sample(s)")
                continue

            n_possible = n * (n - 1) // 2
            n_to_sample = min(n_pairs_per_group, n_possible)

            # Over-sample then filter to get enough unique non-self pairs
            oversample = min(n_to_sample * 3, n_possible * 2)
            idx_a = self.rng.integers(0, n, size=oversample)
            idx_b = self.rng.integers(0, n, size=oversample)

            valid = idx_a != idx_b
            idx_a, idx_b = idx_a[valid], idx_b[valid]

            # Canonical form (min, max) so (a,b) and (b,a) count once
            lo = np.minimum(idx_a, idx_b)
            hi = np.maximum(idx_a, idx_b)
            pairs = np.unique(np.stack([lo, hi], axis=1), axis=0)[:n_to_sample]

            global_a = group_indices[pairs[:, 0]]
            global_b = group_indices[pairs[:, 1]]
            sims = np.sum(embeddings[global_a] * embeddings[global_b], axis=1)

            scores_by_group[str(group)] = sims
            print(f"  '{group}': {len(sims):,} impostor pairs  ({n:,} samples in group)")

        return scores_by_group
