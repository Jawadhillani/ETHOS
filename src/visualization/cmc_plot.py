"""
CMC curve plotting — publication-quality, matches ETHOS palette.
"""

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_cmc(
    rank_accuracies: np.ndarray,
    save_path: str,
    title: str = "CMC Curve — LFW 1:N Identification",
) -> None:
    """
    Plot Cumulative Match Characteristic curve.

    Args:
        rank_accuracies: array of shape (max_rank,) where index k = Rank-(k+1) rate.
        save_path:       output PNG path (parent dirs created automatically).
        title:           chart title.
    """
    ranks     = np.arange(1, len(rank_accuracies) + 1)
    rank1_pct = float(rank_accuracies[0]) * 100

    fig, ax = plt.subplots(figsize=(7, 6), dpi=120)
    ax.plot(ranks, rank_accuracies * 100,
            color="#2f855a", linewidth=2.2, marker="o", markersize=4,
            label="ETHOS (ArcFace buffalo_l)")

    # Annotate Rank-1
    ax.annotate(
        f"Rank-1: {rank1_pct:.2f}%",
        xy=(1, rank1_pct),
        xytext=(max(len(ranks) * 0.30, 2), rank1_pct - 5),
        fontsize=11,
        arrowprops=dict(arrowstyle="->", color="#2f855a", alpha=0.7),
    )

    # Mark Rank-5 and Rank-10 if available
    for k, color in [(5, "#2b6cb0"), (10, "#c05621")]:
        if len(rank_accuracies) >= k:
            val = float(rank_accuracies[k - 1]) * 100
            ax.axvline(x=k, color=color, linestyle="--", linewidth=1.0, alpha=0.5)
            ax.text(k + 0.2, val - 1.5, f"R-{k}: {val:.2f}%",
                    fontsize=9, color=color, va="top")

    ax.set_xlabel("Rank", fontsize=12)
    ax.set_ylabel("Identification Rate (%)", fontsize=12)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend(loc="lower right", fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0.5, len(ranks) + 0.5])
    ax.set_ylim([max(rank_accuracies.min() * 100 - 2, 0), 102])

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"CMC curve saved → {save_path}")
