"""
MatchingEngine: cosine similarity + threshold-based matching.

Core abstraction for both verification (1:1) and identification (1:N).
Designed to be agnostic to the source dataset.
"""

import numpy as np


class MatchingEngine:
    """
    Computes similarity scores and match decisions between face embeddings.

    Embeddings are expected to be L2-normalized (unit norm), which is the case
    for ArcFace's `normed_embedding` output.
    """

    def __init__(self, threshold: float = 0.55):
        self.threshold = threshold

    def cosine_similarity(self, emb_a: np.ndarray, emb_b: np.ndarray) -> float:
        """
        Cosine similarity between two L2-normalized embeddings.
        For unit vectors, this is just the dot product.
        """
        return float(np.dot(emb_a, emb_b))

    def cosine_similarity_batch(self, embs_a: np.ndarray, embs_b: np.ndarray) -> np.ndarray:
        """
        Pairwise cosine similarity. embs_a and embs_b must align row-by-row.
        Returns: 1D array of similarity scores, one per pair.
        """
        return np.sum(embs_a * embs_b, axis=1)

    def cosine_similarity_matrix(self, query_embs: np.ndarray, gallery_embs: np.ndarray) -> np.ndarray:
        """
        Cosine similarity matrix for 1:N identification.
        Returns: (N_query, N_gallery) similarity matrix.
        Memory-safe: callers should chunk their queries if gallery is huge.
        """
        return query_embs @ gallery_embs.T

    def is_match(self, similarity: float) -> bool:
        """Threshold-based match decision."""
        return similarity >= self.threshold

    def decide_batch(self, similarities: np.ndarray) -> np.ndarray:
        """Vectorized match decision for a batch of similarities."""
        return similarities >= self.threshold

    def update_threshold(self, new_threshold: float):
        """Adjust the threshold (used by EER analysis in Week 3)."""
        self.threshold = new_threshold
