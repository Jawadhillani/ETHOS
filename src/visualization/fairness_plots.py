"""
Fairness visualization: per-demographic FAR bars, score distributions, ratio summary.
All plots are publication-quality, saved as PNG.
"""

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import Dict


_COLORS = [
    "#2b6cb0", "#c05621", "#2f855a", "#805ad5",
    "#d69e2e", "#319795", "#e53e3e", "#718096",
    "#744210",
]


def plot_far_by_group(
    per_group_far: Dict[str, float],
    threshold: float,
    save_path: str,
    title: str = "FAR by Demographic Group",
) -> None:
    """Horizontal bar chart of FAR per group, sorted ascending."""
    groups = list(per_group_far.keys())
    fars_pct = [per_group_far[g] * 100 for g in groups]

    order = np.argsort(fars_pct)
    groups_s = [groups[i] for i in order]
    fars_s = [fars_pct[i] for i in order]
    colors = [_COLORS[i % len(_COLORS)] for i in range(len(groups_s))]

    fig, ax = plt.subplots(figsize=(9, max(4, len(groups_s) * 0.7 + 1.5)), dpi=120)
    bars = ax.barh(groups_s, fars_s, color=colors, edgecolor="black", linewidth=0.5)
    x_max = max(fars_s) if max(fars_s) > 0 else 1.0
    for bar, val in zip(bars, fars_s):
        ax.text(val + x_max * 0.015, bar.get_y() + bar.get_height() / 2,
                f"{val:.4f}%", va="center", fontsize=10)

    ax.set_xlabel("False Acceptance Rate (%)", fontsize=12)
    ax.set_title(f"{title}  (threshold={threshold:.4f})", fontsize=13, fontweight="bold")
    ax.set_xlim([0, x_max * 1.18])
    ax.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_per_group_score_distributions(
    impostor_scores_by_group: Dict[str, np.ndarray],
    threshold: float,
    save_path: str,
    title: str = "Impostor Score Distributions by Demographic",
) -> None:
    """Overlaid density histograms, one per demographic group."""
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=120)
    for i, (group, scores) in enumerate(impostor_scores_by_group.items()):
        ax.hist(scores, bins=60, alpha=0.40,
                color=_COLORS[i % len(_COLORS)],
                label=f"{group}  (n={len(scores):,})", density=True)
    ax.axvline(threshold, color="black", linestyle="--", linewidth=1.8,
               label=f"Threshold = {threshold:.4f}")
    ax.set_xlabel("Cosine similarity  (impostor pairs)", fontsize=12)
    ax.set_ylabel("Density", fontsize=12)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_fairness_ratios(
    di: float,
    fmrd: float,
    di_threshold: float,
    fmrd_threshold: float,
    save_path: str,
    title: str = "Fairness Ratios vs Compliance Thresholds",
) -> None:
    """Bar chart comparing DI and FMRD against their compliance lines."""
    labels = ["Disparate Impact\n(≥ threshold = pass)", "FMRD\n(≤ threshold = pass)"]
    values = [di if di is not None else 0.0, fmrd]
    thresholds = [di_threshold, fmrd_threshold]
    colors = ["#2b6cb0", "#c05621"]

    fig, ax = plt.subplots(figsize=(7, 5), dpi=120)
    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=colors, edgecolor="black", linewidth=0.5, width=0.5)
    for i, (xpos, t) in enumerate(zip(x, thresholds)):
        ax.hlines(t, xpos - 0.28, xpos + 0.28,
                  colors="red", linestyles="--", linewidth=2.0,
                  label="Compliance threshold" if i == 0 else "")

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + max(values) * 0.02,
                f"{val:.4f}", ha="center", fontsize=11, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Ratio", fontsize=12)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
