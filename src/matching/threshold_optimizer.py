"""
ThresholdOptimizer: sweep thresholds and find Equal Error Rate point.

Computes FAR and FRR across a range of thresholds, identifies the EER
(where FAR ≈ FRR), and provides full sweep arrays for ROC/DET plotting.
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class SweepResult:
    thresholds: np.ndarray    # all evaluated thresholds (ascending)
    far: np.ndarray           # False Acceptance Rate at each threshold
    frr: np.ndarray           # False Rejection Rate at each threshold
    eer: float                # Equal Error Rate
    eer_threshold: float      # threshold at which EER occurs
    auc: float                # Area Under the ROC Curve


class ThresholdOptimizer:
    """Threshold sweep + EER computation for biometric verification."""

    def sweep(
        self,
        genuine_scores: np.ndarray,
        impostor_scores: np.ndarray,
        n_thresholds: int = 200,
    ) -> SweepResult:
        """
        Sweep thresholds from just below the minimum to just above the maximum
        observed score, computing FAR and FRR at each point.

        Args:
            genuine_scores:  similarity scores for same-person pairs
            impostor_scores: similarity scores for different-person pairs
            n_thresholds:    number of threshold points to evaluate

        Returns:
            SweepResult with full arrays and headline EER/AUC numbers.
        """
        all_scores = np.concatenate([genuine_scores, impostor_scores])
        lo = float(all_scores.min()) - 0.01
        hi = float(all_scores.max()) + 0.01
        thresholds = np.linspace(lo, hi, n_thresholds)

        n_gen = len(genuine_scores)
        n_imp = len(impostor_scores)

        # Vectorized sweep: compare each score against all thresholds at once
        # genuine_scores[:, None] → (N_gen, 1)  vs  thresholds → (T,)
        frr = np.sum(genuine_scores[:, None] < thresholds[None, :], axis=0) / n_gen
        far = np.sum(impostor_scores[:, None] >= thresholds[None, :], axis=0) / n_imp

        # EER: threshold where |FAR - FRR| is minimised
        eer_idx = int(np.argmin(np.abs(far - frr)))
        eer = float((far[eer_idx] + frr[eer_idx]) / 2.0)
        eer_threshold = float(thresholds[eer_idx])

        # AUC: trapezoidal integration of TPR over FPR (sorted by FAR ascending)
        tpr = 1.0 - frr
        order = np.argsort(far)
        auc = float(np.trapz(tpr[order], far[order]))

        return SweepResult(
            thresholds=thresholds,
            far=far,
            frr=frr,
            eer=eer,
            eer_threshold=eer_threshold,
            auc=auc,
        )
