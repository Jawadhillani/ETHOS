"""
FairnessMetrics: computes biometric fairness measurements per demographic group.

Metrics:
  - Per-group FAR (False Acceptance Rate) from FairFace impostor pairs
  - Overall FRR (False Rejection Rate) from LFW genuine pairs
  - Disparate Impact (DI): legal compliance metric (EU AI Act / US 4/5ths rule)
  - FMRD (False Match Rate Disparity): max(FAR) / min(FAR) — security metric
  - FNMRD: not computed here (requires per-group genuine pairs; noted as limitation)

Output is serialisable to JSON for direct consumption by the Claude API (Week 5).
"""

import numpy as np
from dataclasses import dataclass, asdict
from typing import Dict, Optional


@dataclass
class GroupMetrics:
    group: str
    n_pairs: int
    far_at_threshold: float
    frr_at_threshold: Optional[float]   # None — LFW lacks demographic labels
    score_mean: float
    score_std: float


@dataclass
class FairnessReport:
    threshold: float
    overall_far: float
    overall_frr: float
    per_group: Dict[str, GroupMetrics]
    disparate_impact: Optional[float]
    fmrd: float
    fnmrd: Optional[float]              # None — see FNMRD limitation above
    di_compliant: Optional[bool]
    fmrd_compliant: bool
    fnmrd_compliant: Optional[bool]
    worst_far_group: str
    best_far_group: str
    privileged_group: str
    n_groups: int


class FairnessMetrics:
    """Compute and serialise fairness metrics from per-group similarity scores."""

    def __init__(
        self,
        di_threshold: float = 0.80,
        fmrd_threshold: float = 1.50,
        fnmrd_threshold: float = 1.50,
    ):
        self.di_threshold = di_threshold
        self.fmrd_threshold = fmrd_threshold
        self.fnmrd_threshold = fnmrd_threshold

    def compute_per_group_far(
        self,
        impostor_scores_by_group: Dict[str, np.ndarray],
        threshold: float,
    ) -> Dict[str, GroupMetrics]:
        per_group: Dict[str, GroupMetrics] = {}
        for group, scores in impostor_scores_by_group.items():
            per_group[group] = GroupMetrics(
                group=group,
                n_pairs=len(scores),
                far_at_threshold=float(np.mean(scores >= threshold)),
                frr_at_threshold=None,
                score_mean=float(scores.mean()),
                score_std=float(scores.std()),
            )
        return per_group

    def compute_disparate_impact(
        self,
        per_group: Dict[str, GroupMetrics],
        privileged_group: str,
    ) -> Optional[float]:
        """
        Biometric DI definition: ratio of *impostor rejection rates*.
        A lower FAR = stricter security for that group.

        DI = (1 - FAR_unprivileged) / (1 - FAR_privileged)

        Returns the worst (minimum) DI across all unprivileged groups.
        Values below di_threshold indicate a compliance violation.
        """
        if privileged_group not in per_group:
            return None
        priv_acceptance = 1.0 - per_group[privileged_group].far_at_threshold
        if priv_acceptance == 0.0:
            return None

        worst_di = 1.0
        for group, m in per_group.items():
            if group == privileged_group:
                continue
            di = (1.0 - m.far_at_threshold) / priv_acceptance
            if di < worst_di:
                worst_di = di
        return float(worst_di)

    def compute_fmrd(self, per_group: Dict[str, GroupMetrics]) -> float:
        """FMRD = max(FAR) / min(FAR). Uses ε floor to avoid divide-by-zero."""
        fars = [m.far_at_threshold for m in per_group.values()]
        return float(max(fars) / max(min(fars), 1e-6))

    def generate_report(
        self,
        impostor_scores_by_group: Dict[str, np.ndarray],
        genuine_scores: np.ndarray,
        threshold: float,
        privileged_group: str,
    ) -> FairnessReport:
        per_group = self.compute_per_group_far(impostor_scores_by_group, threshold)
        overall_frr = float(np.mean(genuine_scores < threshold))
        all_impostor = np.concatenate(list(impostor_scores_by_group.values()))
        overall_far = float(np.mean(all_impostor >= threshold))

        di = self.compute_disparate_impact(per_group, privileged_group)
        fmrd = self.compute_fmrd(per_group)

        sorted_groups = sorted(per_group.items(), key=lambda kv: kv[1].far_at_threshold)
        best_far_group = sorted_groups[0][0]
        worst_far_group = sorted_groups[-1][0]

        return FairnessReport(
            threshold=threshold,
            overall_far=overall_far,
            overall_frr=overall_frr,
            per_group=per_group,
            disparate_impact=di,
            fmrd=fmrd,
            fnmrd=None,
            di_compliant=(di >= self.di_threshold) if di is not None else None,
            fmrd_compliant=(fmrd <= self.fmrd_threshold),
            fnmrd_compliant=None,
            worst_far_group=worst_far_group,
            best_far_group=best_far_group,
            privileged_group=privileged_group,
            n_groups=len(per_group),
        )

    def report_to_dict(self, report: FairnessReport) -> dict:
        """Serialise to a JSON-safe dict for the Claude API payload (Week 5)."""
        return {
            "threshold": report.threshold,
            "overall_far": report.overall_far,
            "overall_frr": report.overall_frr,
            "per_group": {g: asdict(m) for g, m in report.per_group.items()},
            "fairness_ratios": {
                "disparate_impact": report.disparate_impact,
                "fmrd": report.fmrd,
                "fnmrd": report.fnmrd,
            },
            "compliance": {
                "di_compliant": report.di_compliant,
                "di_threshold": self.di_threshold,
                "fmrd_compliant": report.fmrd_compliant,
                "fmrd_threshold": self.fmrd_threshold,
                "fnmrd_compliant": report.fnmrd_compliant,
                "fnmrd_threshold": self.fnmrd_threshold,
            },
            "summary": {
                "best_far_group": report.best_far_group,
                "worst_far_group": report.worst_far_group,
                "privileged_group": report.privileged_group,
                "n_groups": report.n_groups,
            },
        }
