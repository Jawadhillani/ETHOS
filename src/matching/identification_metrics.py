"""
Closed-set 1:N identification metrics — Cumulative Match Characteristic (CMC).

IdentificationEvaluator computes Rank-K identification rates for a probe set
against a fixed-size gallery. Uses the chunked cosine-similarity matrix from
MatchingEngine to stay memory-safe for galleries up to ~10k images.
"""

from __future__ import annotations

import numpy as np

from src.matching.engine import MatchingEngine


class IdentificationEvaluator:
    """
    Evaluate 1:N face identification via CMC curves.

    Args:
        batch_size: Number of probe embeddings processed per chunk to avoid
                    OOM with large galleries.
    """

    def __init__(self, batch_size: int = 512) -> None:
        self._engine     = MatchingEngine()
        self._batch_size = batch_size

    # ──────────────────────────────────────────────────────────────────────────

    def evaluate(
        self,
        probe_embeddings:   np.ndarray,   # (N_probe, D)
        probe_identities:   np.ndarray,   # (N_probe,) — any hashable labels
        gallery_embeddings: np.ndarray,   # (N_gallery, D)
        gallery_identities: np.ndarray,   # (N_gallery,)
        max_rank: int = 20,
    ) -> dict:
        """
        Compute CMC Rank-K identification rates.

        For each probe, the gallery is sorted by descending similarity.  The
        rank of the correct identity is the position of the first gallery
        entry that shares the probe's identity.  Rank-1 = correct match is
        the top-1 result.

        Returns:
            {
                "rank_k":  np.ndarray of shape (max_rank,)  # Rank-1…Rank-K rates
                "rank_1":  float
                "rank_5":  float
                "rank_10": float
                "n_probes": int
                "n_gallery": int
            }
        """
        N_probe   = probe_embeddings.shape[0]
        N_gallery = gallery_embeddings.shape[0]
        max_rank  = min(max_rank, N_gallery)

        # For each probe, record at which rank the correct identity appears
        correct_ranks = np.full(N_probe, max_rank, dtype=np.int32)  # default: not found

        # Convert identities to arrays for fast comparison
        probe_ids   = np.asarray(probe_identities)
        gallery_ids = np.asarray(gallery_identities)

        # Chunked similarity to stay memory-safe
        for start in range(0, N_probe, self._batch_size):
            end   = min(start + self._batch_size, N_probe)
            chunk = probe_embeddings[start:end]                 # (B, D)
            sims  = self._engine.cosine_similarity_matrix(chunk, gallery_embeddings)
            # sims: (B, N_gallery)

            # Descending sort — argsort is cheaper than full sort for top-K
            sorted_idx = np.argsort(-sims, axis=1)             # (B, N_gallery)

            for bi, gi in enumerate(range(start, end)):
                pid = probe_ids[gi]
                # Walk the sorted gallery until we find a matching identity
                for rank_pos, gal_j in enumerate(sorted_idx[bi]):
                    if gallery_ids[gal_j] == pid:
                        correct_ranks[gi] = rank_pos   # 0-indexed
                        break

        # ── CMC curve ─────────────────────────────────────────────────────────
        # rank_k[k] = fraction of probes where correct ID was in top-(k+1)
        rank_k = np.array([
            (correct_ranks <= k).mean()
            for k in range(max_rank)
        ])

        return {
            "rank_k":    rank_k,
            "rank_1":    float(rank_k[0]),
            "rank_5":    float(rank_k[4]) if max_rank >= 5  else float("nan"),
            "rank_10":   float(rank_k[9]) if max_rank >= 10 else float("nan"),
            "n_probes":  N_probe,
            "n_gallery": N_gallery,
        }
