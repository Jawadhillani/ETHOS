"""
Verifier: 1:1 face verification built on top of MatchingEngine.

Given two embeddings, decides whether they belong to the same person.
"""

from dataclasses import dataclass
import numpy as np
from .engine import MatchingEngine


@dataclass
class VerifyResult:
    is_match: bool
    similarity: float
    threshold: float


class Verifier:
    """
    1:1 verification wrapper around MatchingEngine.

    Usage:
        verifier = Verifier()
        result = verifier.verify(emb_a, emb_b)
        print(result.is_match, result.similarity)
    """

    def __init__(self, engine: MatchingEngine = None):
        self.engine = engine or MatchingEngine()

    def verify(self, emb_a: np.ndarray, emb_b: np.ndarray) -> VerifyResult:
        """
        Verify whether two embeddings belong to the same person.

        Args:
            emb_a: L2-normalized embedding, shape (512,)
            emb_b: L2-normalized embedding, shape (512,)

        Returns:
            VerifyResult with is_match, similarity, and threshold used.
        """
        sim = self.engine.cosine_similarity(emb_a, emb_b)
        return VerifyResult(
            is_match=self.engine.is_match(sim),
            similarity=sim,
            threshold=self.engine.threshold,
        )

    def verify_batch(
        self, embs_a: np.ndarray, embs_b: np.ndarray
    ) -> list[VerifyResult]:
        """
        Verify N pairs in one shot. embs_a and embs_b must align row-by-row.

        Args:
            embs_a: shape (N, 512)
            embs_b: shape (N, 512)

        Returns:
            List of N VerifyResult objects.
        """
        sims = self.engine.cosine_similarity_batch(embs_a, embs_b)
        decisions = self.engine.decide_batch(sims)
        return [
            VerifyResult(is_match=bool(d), similarity=float(s), threshold=self.engine.threshold)
            for d, s in zip(decisions, sims)
        ]
