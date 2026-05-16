"""
Day 12 — LFW 1:N Identification Evaluation.

Uses the enrollment/probe split built by build_enrollment_probe_split.py.
Loads pre-computed embeddings (no re-extraction needed).
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.matching.identification_metrics import IdentificationEvaluator
from src.visualization.cmc_plot import plot_cmc

LFW_EMB   = ROOT / "data/embeddings_cache/lfw_embeddings.npz"
SPLIT_CSV = ROOT / "data/processed/lfw_enrollment_probe.csv"
CMC_OUT   = ROOT / "outputs/plots/lfw_cmc.png"
METRICS_OUT = ROOT / "outputs/reports/lfw_identification_metrics.json"


def main():
    # ── Load split manifest ───────────────────────────────────────────────────
    if not SPLIT_CSV.exists():
        print("Split CSV not found. Run build_enrollment_probe_split.py first.")
        sys.exit(1)

    df = pd.read_csv(SPLIT_CSV)
    enroll_df = df[df["role"] == "enrollment"].reset_index(drop=True)
    probe_df  = df[df["role"] == "probe"].reset_index(drop=True)
    print(f"Split loaded: {len(enroll_df)} enrollment, {len(probe_df)} probe")

    # ── Load LFW embeddings ───────────────────────────────────────────────────
    print("Loading LFW embeddings …")
    data       = np.load(str(LFW_EMB), allow_pickle=True)
    embeddings = data["embeddings"]   # (12000, 512)
    issame     = data["issame"].astype(bool)

    # Reconstruct embedding index from pair_idx
    # embeddings[pair_idx * 2]     → A-side (enrollment)
    # embeddings[pair_idx * 2 + 1] → B-side (probe)
    enroll_embs = embeddings[enroll_df["pair_idx"].values * 2]
    probe_embs  = embeddings[probe_df["pair_idx"].values  * 2 + 1]

    enroll_ids  = enroll_df["subject_id"].values
    probe_ids   = probe_df["subject_id"].values

    print(f"Gallery: {enroll_embs.shape}  Probe: {probe_embs.shape}")

    # ── Run evaluation ────────────────────────────────────────────────────────
    print("Running IdentificationEvaluator (max_rank=20) …")
    evaluator = IdentificationEvaluator(batch_size=512)
    results   = evaluator.evaluate(
        probe_embeddings   = probe_embs,
        probe_identities   = probe_ids,
        gallery_embeddings = enroll_embs,
        gallery_identities = enroll_ids,
        max_rank           = 20,
    )

    # ── Print summary ─────────────────────────────────────────────────────────
    print("\n" + "="*50)
    print(f"  LFW 1:N Identification Results")
    print(f"  Gallery size:  {results['n_gallery']:,}")
    print(f"  Probe size:    {results['n_probes']:,}")
    print(f"  Rank-1:        {results['rank_1']*100:.2f}%")
    print(f"  Rank-5:        {results['rank_5']*100:.2f}%")
    print(f"  Rank-10:       {results['rank_10']*100:.2f}%")
    print("="*50 + "\n")

    # ── CMC curve ─────────────────────────────────────────────────────────────
    plot_cmc(results["rank_k"], str(CMC_OUT),
             title="CMC Curve — LFW 1:N Identification (3,000-subject Gallery)")
    print(f"CMC plot saved → {CMC_OUT}")

    # ── Save metrics JSON ─────────────────────────────────────────────────────
    import json
    METRICS_OUT.parent.mkdir(parents=True, exist_ok=True)
    metrics_dict = {
        "task":      "lfw_1_n_identification",
        "n_gallery": results["n_gallery"],
        "n_probes":  results["n_probes"],
        "rank_1":    round(results["rank_1"], 6),
        "rank_5":    round(results["rank_5"], 6),
        "rank_10":   round(results["rank_10"], 6),
        "rank_k":    [round(float(v), 6) for v in results["rank_k"]],
    }
    with open(METRICS_OUT, "w") as f:
        json.dump(metrics_dict, f, indent=2)
    print(f"Metrics saved → {METRICS_OUT}")


if __name__ == "__main__":
    main()
