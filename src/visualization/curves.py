"""
ROC, DET, CMC, and score-distribution curve plotting.

All plots are publication-quality (IEEE-ready), saved as PNG.
No scipy dependency — probit transform implemented via Acklam's rational
approximation (accurate to ~1e-9).
"""

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")   # headless-safe, must be before pyplot import
import matplotlib.pyplot as plt


# ── Probit helper (replaces scipy.stats.norm.ppf) ────────────────────────────

def _probit(p: np.ndarray) -> np.ndarray:
    """
    Inverse normal CDF (probit function) via Acklam's rational approximation.
    Accurate to ~1.15e-9. No scipy required.

    Reference: Peter J. Acklam, https://web.archive.org/web/20151030215612/
               http://home.online.no/~pjacklam/notes/invnorm/
    """
    a = [-3.969683028665376e+01,  2.209460984245205e+02,
         -2.759285104469687e+02,  1.383577518672690e+02,
         -3.066479806614716e+01,  2.506628277459239e+00]
    b = [-5.447609879822406e+01,  1.615858368580409e+02,
         -1.556989798598866e+02,  6.680131188771972e+01,
         -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
          4.374664141464968e+00,  2.938163982698783e+00]
    d = [ 7.784695709041462e-03,  3.224671290700398e-01,
          2.445134137142996e+00,  3.754408661907416e+00]

    p_low, p_high = 0.02425, 1 - 0.02425
    q = np.empty_like(p, dtype=np.float64)

    # Lower tail
    lo = p < p_low
    if lo.any():
        s = np.sqrt(-2.0 * np.log(p[lo]))
        q[lo] = (((((c[0]*s+c[1])*s+c[2])*s+c[3])*s+c[4])*s+c[5]) / \
                ((((d[0]*s+d[1])*s+d[2])*s+d[3])*s+1.0)

    # Central region
    mid = (p_low <= p) & (p <= p_high)
    if mid.any():
        t = p[mid] - 0.5
        u = t * t
        q[mid] = (((((a[0]*u+a[1])*u+a[2])*u+a[3])*u+a[4])*u+a[5])*t / \
                 (((((b[0]*u+b[1])*u+b[2])*u+b[3])*u+b[4])*u+1.0)

    # Upper tail (symmetry)
    hi = p > p_high
    if hi.any():
        s = np.sqrt(-2.0 * np.log(1.0 - p[hi]))
        q[hi] = -(((((c[0]*s+c[1])*s+c[2])*s+c[3])*s+c[4])*s+c[5]) / \
                  ((((d[0]*s+d[1])*s+d[2])*s+d[3])*s+1.0)

    return q


# ── Public plotting functions ─────────────────────────────────────────────────

def plot_roc(
    far: np.ndarray,
    frr: np.ndarray,
    auc: float,
    save_path: str,
    title: str = "ROC Curve",
) -> None:
    """Receiver Operating Characteristic: TPR vs FPR."""
    tpr = 1.0 - frr
    order = np.argsort(far)

    fig, ax = plt.subplots(figsize=(7, 6), dpi=120)
    ax.plot(far[order], tpr[order], color="#2b6cb0", linewidth=2.2,
            label=f"ETHOS (AUC = {auc:.4f})")
    ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.5, label="Random")
    ax.set_xlabel("False Positive Rate (FAR)", fontsize=12)
    ax.set_ylabel("True Positive Rate (1 − FRR)", fontsize=12)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend(loc="lower right", fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1.02])
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_det(
    far: np.ndarray,
    frr: np.ndarray,
    eer: float,
    save_path: str,
    title: str = "DET Curve",
) -> None:
    """
    Detection Error Tradeoff curve. FAR vs FRR on probit-scaled axes.
    Standard biometric reporting format (NIST FRVT style).
    """
    eps = 1e-6
    far_p = _probit(np.clip(far, eps, 1 - eps))
    frr_p = _probit(np.clip(frr, eps, 1 - eps))

    fig, ax = plt.subplots(figsize=(7, 6), dpi=120)
    ax.plot(far_p, frr_p, color="#c05621", linewidth=2.2,
            label=f"ETHOS (EER = {eer*100:.2f}%)")

    ticks_pct = [0.1, 1, 5, 10, 20, 40]
    tick_locs = _probit(np.array(ticks_pct) / 100.0)
    ax.set_xticks(tick_locs)
    ax.set_xticklabels([f"{t}%" for t in ticks_pct])
    ax.set_yticks(tick_locs)
    ax.set_yticklabels([f"{t}%" for t in ticks_pct])

    ax.set_xlabel("False Acceptance Rate (FAR)", fontsize=12)
    ax.set_ylabel("False Rejection Rate (FRR)", fontsize=12)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_cmc(
    rank_accuracies: np.ndarray,
    save_path: str,
    title: str = "CMC Curve",
) -> None:
    """
    Cumulative Match Characteristic curve.
    rank_accuracies[i] = fraction of queries where correct ID is in top-(i+1).
    """
    ranks = np.arange(1, len(rank_accuracies) + 1)
    rank1_pct = float(rank_accuracies[0]) * 100

    fig, ax = plt.subplots(figsize=(7, 6), dpi=120)
    ax.plot(ranks, rank_accuracies * 100, color="#2f855a", linewidth=2.2,
            marker="o", markersize=4)
    ax.annotate(
        f"Rank-1: {rank1_pct:.2f}%",
        xy=(1, rank1_pct),
        xytext=(max(len(ranks) * 0.35, 2), rank1_pct - 5),
        fontsize=11,
        arrowprops=dict(arrowstyle="->", color="#2f855a", alpha=0.7),
    )
    ax.set_xlabel("Rank", fontsize=12)
    ax.set_ylabel("Identification Rate (%)", fontsize=12)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.set_ylim([max(rank_accuracies.min() * 100 - 2, 0), 102])
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_score_distributions(
    genuine_scores: np.ndarray,
    impostor_scores: np.ndarray,
    eer_threshold: float,
    save_path: str,
    title: str = "Score Distributions",
) -> None:
    """Histogram of genuine vs impostor scores with EER threshold line."""
    fig, ax = plt.subplots(figsize=(8, 5), dpi=120)
    ax.hist(impostor_scores, bins=80, alpha=0.6, color="#c05621", density=True,
            label=f"Impostor  (n={len(impostor_scores):,})")
    ax.hist(genuine_scores, bins=80, alpha=0.6, color="#2b6cb0", density=True,
            label=f"Genuine   (n={len(genuine_scores):,})")
    ax.axvline(eer_threshold, color="black", linestyle="--", linewidth=1.5,
               label=f"EER threshold = {eer_threshold:.4f}")
    ax.set_xlabel("Cosine similarity", fontsize=12)
    ax.set_ylabel("Density", fontsize=12)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
