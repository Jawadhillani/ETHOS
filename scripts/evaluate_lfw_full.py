"""
Week 3 deliverable: Full LFW evaluation — EER, AUC, ROC, DET, score distributions.

Outputs (saved to outputs/plots/):
  lfw_roc.png
  lfw_det.png
  lfw_score_distributions.png

Console report:
  EER %, EER threshold, AUC
  FAR/FRR comparison: default 0.55 vs EER-optimal threshold
"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.matching.engine import MatchingEngine
from src.matching.threshold_optimizer import ThresholdOptimizer
from src.visualization.curves import (
    plot_roc,
    plot_det,
    plot_score_distributions,
)


def main():
    project_root = Path(__file__).parent.parent
    lfw_cache = project_root / "data/embeddings_cache/lfw_embeddings.npz"
    plots_dir = project_root / "outputs/plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    # ── Load cached embeddings ────────────────────────────────────────────────
    print(f"Loading LFW embeddings from {lfw_cache.relative_to(project_root)}")
    data = np.load(str(lfw_cache), allow_pickle=True)
    embeddings = data["embeddings"]   # (12000, 512) float32
    issame = data["issame"].astype(bool)  # (6000,) bool
    print(f"   {len(embeddings):,} embeddings, {len(issame):,} pairs "
          f"({issame.sum():,} genuine, {(~issame).sum():,} impostor)")

    # ── Compute pairwise similarities ─────────────────────────────────────────
    engine = MatchingEngine(threshold=0.55)
    embs_a = embeddings[0::2]   # (6000, 512)
    embs_b = embeddings[1::2]   # (6000, 512)
    similarities = engine.cosine_similarity_batch(embs_a, embs_b)

    genuine_scores = similarities[issame]
    impostor_scores = similarities[~issame]

    print(f"\nScore distributions:")
    print(f"   Genuine:  n={len(genuine_scores):,}  "
          f"mean={genuine_scores.mean():.4f}  std={genuine_scores.std():.4f}  "
          f"min={genuine_scores.min():.4f}  max={genuine_scores.max():.4f}")
    print(f"   Impostor: n={len(impostor_scores):,}  "
          f"mean={impostor_scores.mean():.4f}  std={impostor_scores.std():.4f}  "
          f"min={impostor_scores.min():.4f}  max={impostor_scores.max():.4f}")
    print(f"   Gap (genuine mean - impostor mean): "
          f"{genuine_scores.mean() - impostor_scores.mean():.4f}")

    # ── Threshold sweep ───────────────────────────────────────────────────────
    print(f"\nRunning threshold sweep (200 points)...")
    optimizer = ThresholdOptimizer()
    result = optimizer.sweep(genuine_scores, impostor_scores, n_thresholds=200)

    print(f"\nHeadline metrics:")
    print(f"   EER:               {result.eer * 100:.2f}%")
    print(f"   EER threshold:     {result.eer_threshold:.4f}")
    print(f"   AUC:               {result.auc:.4f}")

    # ── Threshold comparison ──────────────────────────────────────────────────
    def rates_at(threshold):
        far = float(np.sum(impostor_scores >= threshold) / len(impostor_scores))
        frr = float(np.sum(genuine_scores < threshold) / len(genuine_scores))
        acc = float(np.sum(
            (similarities >= threshold) == issame
        ) / len(issame))
        return far, frr, acc

    far_def, frr_def, acc_def = rates_at(0.55)
    far_eer, frr_eer, acc_eer = rates_at(result.eer_threshold)

    print(f"\nThreshold comparison:")
    print(f"   {'Threshold':>12}  {'FAR':>8}  {'FRR':>8}  {'Accuracy':>10}")
    print(f"   {'0.5500':>12}  {far_def*100:>7.2f}%  {frr_def*100:>7.2f}%  {acc_def*100:>9.2f}%")
    print(f"   {result.eer_threshold:>12.4f}  {far_eer*100:>7.2f}%  {frr_eer*100:>7.2f}%  {acc_eer*100:>9.2f}%")

    # ── Generate plots ────────────────────────────────────────────────────────
    print(f"\nGenerating plots...")

    roc_path = plots_dir / "lfw_roc.png"
    plot_roc(
        result.far, result.frr, result.auc,
        save_path=str(roc_path),
        title=f"LFW ROC Curve — ETHOS (AUC = {result.auc:.4f})",
    )
    print(f"   Saved {roc_path.relative_to(project_root)}")

    det_path = plots_dir / "lfw_det.png"
    plot_det(
        result.far, result.frr, result.eer,
        save_path=str(det_path),
        title=f"LFW DET Curve — ETHOS (EER = {result.eer*100:.2f}%)",
    )
    print(f"   Saved {det_path.relative_to(project_root)}")

    dist_path = plots_dir / "lfw_score_distributions.png"
    plot_score_distributions(
        genuine_scores, impostor_scores, result.eer_threshold,
        save_path=str(dist_path),
        title="LFW Score Distributions — Genuine vs Impostor",
    )
    print(f"   Saved {dist_path.relative_to(project_root)}")

    print(f"\nWeek 3 LFW evaluation complete.")
    print(f"   EER={result.eer*100:.2f}%  |  AUC={result.auc:.4f}  |  "
          f"EER threshold={result.eer_threshold:.4f}")


if __name__ == "__main__":
    main()
