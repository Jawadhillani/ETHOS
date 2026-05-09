"""
Week 4 deliverable: full fairness audit — LFW genuine + FairFace stratified impostor.

Audits:
  1. Fairness by race  (7 groups)
  2. Fairness by gender (2 groups)
  3. Fairness by age    (9 groups)

Outputs:
  outputs/reports/fairness_audit.json  ← Claude API payload for Week 5
  outputs/plots/fairness_far_by_race.png
  outputs/plots/fairness_score_dist_by_race.png
  outputs/plots/fairness_ratios_race.png
  outputs/plots/fairness_far_by_gender.png
  outputs/plots/fairness_ratios_gender.png
  outputs/plots/fairness_far_by_age.png
"""

import sys
import json
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fairness.pair_builder import PairBuilder
from src.fairness.metrics import FairnessMetrics
from src.visualization.fairness_plots import (
    plot_far_by_group,
    plot_per_group_score_distributions,
    plot_fairness_ratios,
)

# EER-optimal threshold found in Week 3
THRESHOLD = 0.1810


def load_npz(path):
    return np.load(str(path), allow_pickle=True)


def run_audit(label, embeddings, group_labels, genuine_scores, threshold,
              metrics_engine, builder, plots_dir, n_pairs=50_000):
    print(f"\n{'='*60}")
    print(f"AUDIT: Fairness by {label.upper()}")
    print(f"{'='*60}")
    print(f"Building impostor pairs stratified by {label}...")
    scores_by_group = builder.build_impostor_pairs_per_group(
        embeddings, group_labels, n_pairs_per_group=n_pairs
    )

    # Privileged group = largest (most-represented) group
    privileged = max(scores_by_group, key=lambda g: len(scores_by_group[g]))

    report = metrics_engine.generate_report(
        scores_by_group, genuine_scores, threshold, privileged
    )

    print(f"\nFairness summary — by {label}:")
    print(f"  Overall FAR:        {report.overall_far*100:.4f}%")
    print(f"  Overall FRR:        {report.overall_frr*100:.4f}%   (from LFW, not per-group)")
    print(f"  Disparate Impact:   {report.disparate_impact:.4f}  "
          f"(threshold ≥ {metrics_engine.di_threshold})  "
          f"→ {'PASS' if report.di_compliant else 'FAIL'}")
    print(f"  FMRD:               {report.fmrd:.4f}  "
          f"(threshold ≤ {metrics_engine.fmrd_threshold})  "
          f"→ {'PASS' if report.fmrd_compliant else 'FAIL'}")
    print(f"  Best  group (lowest FAR):  {report.best_far_group}")
    print(f"  Worst group (highest FAR): {report.worst_far_group}")
    print(f"\n  Per-{label} FAR (sorted):")
    for g, m in sorted(report.per_group.items(), key=lambda kv: kv[1].far_at_threshold):
        flag = "  <-- best" if g == report.best_far_group else (
               "  <-- worst" if g == report.worst_far_group else "")
        print(f"    {g:25s}  FAR={m.far_at_threshold*100:.4f}%  "
              f"mean_sim={m.score_mean:.4f}  n={m.n_pairs:,}{flag}")

    # Plots
    slug = label.lower()
    plot_far_by_group(
        {g: m.far_at_threshold for g, m in report.per_group.items()},
        threshold,
        save_path=str(plots_dir / f"fairness_far_by_{slug}.png"),
        title=f"False Acceptance Rate by {label.title()}",
    )
    if label == "race":
        plot_per_group_score_distributions(
            scores_by_group, threshold,
            save_path=str(plots_dir / f"fairness_score_dist_by_{slug}.png"),
            title=f"Impostor Score Distributions by {label.title()}",
        )
    plot_fairness_ratios(
        report.disparate_impact, report.fmrd,
        metrics_engine.di_threshold, metrics_engine.fmrd_threshold,
        save_path=str(plots_dir / f"fairness_ratios_{slug}.png"),
        title=f"{label.title()} Fairness Ratios vs Compliance Thresholds",
    )

    return report, scores_by_group


def main():
    project_root = Path(__file__).parent.parent
    plots_dir = project_root / "outputs/plots"
    reports_dir = project_root / "outputs/reports"
    plots_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    # ── Load embeddings ───────────────────────────────────────────────────────
    print("Loading embeddings...")
    lfw = load_npz(project_root / "data/embeddings_cache/lfw_embeddings.npz")
    ff = load_npz(project_root / "data/embeddings_cache/fairface_train_embeddings.npz")

    print(f"  LFW:       {lfw['embeddings'].shape[0]:,} embeddings, "
          f"{lfw['issame'].shape[0]:,} pairs")
    print(f"  FairFace:  {ff['embeddings'].shape[0]:,} embeddings  "
          f"(race×{len(np.unique(ff['race']))}  "
          f"gender×{len(np.unique(ff['gender']))}  "
          f"age×{len(np.unique(ff['age']))})")

    # ── Genuine scores from LFW ───────────────────────────────────────────────
    print(f"\nBuilding genuine pair scores from LFW...")
    builder = PairBuilder(random_seed=42)
    genuine_scores = builder.get_lfw_genuine_scores(
        lfw["embeddings"], lfw["issame"].astype(bool)
    )
    print(f"  Genuine pairs: {len(genuine_scores):,}  "
          f"mean={genuine_scores.mean():.4f}  std={genuine_scores.std():.4f}")

    print(f"\nUsing EER-optimal threshold: {THRESHOLD}")

    metrics_engine = FairnessMetrics()
    ff_embs = ff["embeddings"]

    # ── Audits ────────────────────────────────────────────────────────────────
    race_report, race_scores = run_audit(
        "race", ff_embs, ff["race"], genuine_scores, THRESHOLD,
        metrics_engine, builder, plots_dir, n_pairs=50_000,
    )

    gender_report, gender_scores = run_audit(
        "gender", ff_embs, ff["gender"], genuine_scores, THRESHOLD,
        metrics_engine, builder, plots_dir, n_pairs=50_000,
    )

    age_report, age_scores = run_audit(
        "age", ff_embs, ff["age"], genuine_scores, THRESHOLD,
        metrics_engine, builder, plots_dir, n_pairs=50_000,
    )

    # ── Plots saved summary ───────────────────────────────────────────────────
    print(f"\nPlots saved to outputs/plots/:")
    for fname in sorted(plots_dir.glob("fairness_*.png")):
        print(f"  {fname.name}")

    # ── Master JSON report ────────────────────────────────────────────────────
    master = {
        "metadata": {
            "project": "ETHOS",
            "evaluation": "Week 4 fairness audit",
            "datasets": {
                "genuine_pairs": "LFW (3,000 genuine pairs)",
                "impostor_pairs": "FairFace train (86,486 images, stratified by demographic)",
            },
            "threshold": THRESHOLD,
            "threshold_source": "LFW EER-optimal (Week 3)",
            "limitation": (
                "Per-group FRR unavailable: LFW lacks demographic labels. "
                "FNMRD cannot be computed. Documented in paper."
            ),
        },
        "audits": {
            "race":   metrics_engine.report_to_dict(race_report),
            "gender": metrics_engine.report_to_dict(gender_report),
            "age":    metrics_engine.report_to_dict(age_report),
        },
    }

    report_path = reports_dir / "fairness_audit.json"
    with open(report_path, "w") as f:
        json.dump(master, f, indent=2, default=str)

    print(f"\nFairness audit JSON → {report_path.relative_to(project_root)}")
    print("  (Claude API payload for Week 5)")

    print(f"\nWeek 4 complete.")


if __name__ == "__main__":
    main()
