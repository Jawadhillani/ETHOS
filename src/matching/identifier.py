"""
Identifier: 1:N face identification built on top of MatchingEngine.

Given a query embedding and a gallery of N embeddings, returns the top-k
most similar gallery entries and whether they cross the match threshold.
"""

from dataclasses import dataclass, field
import numpy as np
from .engine import MatchingEngine


@dataclass
class IdentifyResult:
    top_k_indices: list[int]          # gallery indices, best first
    top_k_similarities: list[float]   # corresponding similarity scores
    top_k_ids: list | None            # gallery IDs / labels if provided
    best_is_match: bool               # whether the top-1 hit crosses threshold
    threshold: float


class Identifier:
    """
    1:N identification wrapper around MatchingEngine.

    Chunked similarity computation keeps memory flat regardless of gallery size.

    Usage:
        identifier = Identifier()
        result = identifier.identify(query_emb, gallery_embs, gallery_ids=labels)
        print(result.top_k_ids, result.top_k_similarities)
    """

    def __init__(self, engine: MatchingEngine = None, batch_size: int = 5000):
        self.engine = engine or MatchingEngine()
        self.batch_size = batch_size

    def identify(
        self,
        query_emb: np.ndarray,
        gallery_embs: np.ndarray,
        gallery_ids=None,
        top_k: int = 5,
    ) -> IdentifyResult:
        """
        Find the top-k most similar gallery entries for a single query.

        Args:
            query_emb:    L2-normalized embedding, shape (512,)
            gallery_embs: L2-normalized gallery, shape (N, 512)
            gallery_ids:  Optional list/array of length N (labels, filenames, etc.)
            top_k:        How many results to return (capped at gallery size)

        Returns:
            IdentifyResult with ranked indices, similarities, IDs, and match flag.
        """
        top_k = min(top_k, len(gallery_embs))
        similarities = self._chunked_similarity(query_emb[np.newaxis, :], gallery_embs)[0]

        # Partial sort — only sort the top_k, not the full gallery
        top_k_indices = np.argpartition(similarities, -top_k)[-top_k:]
        top_k_indices = top_k_indices[np.argsort(similarities[top_k_indices])[::-1]]
        top_k_sims = similarities[top_k_indices].tolist()

        return IdentifyResult(
            top_k_indices=top_k_indices.tolist(),
            top_k_similarities=top_k_sims,
            top_k_ids=[gallery_ids[i] for i in top_k_indices] if gallery_ids is not None else None,
            best_is_match=self.engine.is_match(top_k_sims[0]),
            threshold=self.engine.threshold,
        )

    def identify_batch(
        self,
        query_embs: np.ndarray,
        gallery_embs: np.ndarray,
        gallery_ids=None,
        top_k: int = 5,
    ) -> list[IdentifyResult]:
        """
        Identify a batch of queries against the same gallery.

        Args:
            query_embs:   shape (Q, 512)
            gallery_embs: shape (N, 512)
            gallery_ids:  Optional list/array of length N
            top_k:        How many results per query

        Returns:
            List of Q IdentifyResult objects.
        """
        top_k = min(top_k, len(gallery_embs))
        sim_matrix = self._chunked_similarity(query_embs, gallery_embs)  # (Q, N)

        results = []
        for sims in sim_matrix:
            indices = np.argpartition(sims, -top_k)[-top_k:]
            indices = indices[np.argsort(sims[indices])[::-1]]
            sims_k = sims[indices].tolist()
            results.append(IdentifyResult(
                top_k_indices=indices.tolist(),
                top_k_similarities=sims_k,
                top_k_ids=[gallery_ids[i] for i in indices] if gallery_ids is not None else None,
                best_is_match=self.engine.is_match(sims_k[0]),
                threshold=self.engine.threshold,
            ))
        return results

    def _chunked_similarity(
        self, query_embs: np.ndarray, gallery_embs: np.ndarray
    ) -> np.ndarray:
        """
        Compute query×gallery similarity matrix in chunks to cap memory usage.

        With batch_size=5000 and 512-dim float32 embeddings, each chunk is
        ~10 MB — safe even if the gallery has hundreds of thousands of entries.

        Returns: (Q, N) similarity matrix as float32.
        """
        n_gallery = len(gallery_embs)
        n_query = len(query_embs)
        sim_matrix = np.empty((n_query, n_gallery), dtype=np.float32)

        for start in range(0, n_gallery, self.batch_size):
            end = min(start + self.batch_size, n_gallery)
            sim_matrix[:, start:end] = self.engine.cosine_similarity_matrix(
                query_embs, gallery_embs[start:end]
            )

        return sim_matrix
