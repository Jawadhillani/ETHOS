"""
Day 13 — Robustness Evaluation.

Tests how each image perturbation affects ArcFace pair similarity and
match accuracy on 1,000 LFW genuine pairs at the EER threshold (0.1810).

For each perturbation type, sweeps a severity range, re-extracts embeddings
from the perturbed B-side images, and measures the drop in match rate.

Output:
  outputs/plots/robustness_degradation.png
  outputs/reports/robustness_results.json
"""

import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.robustness.perturbations import (
    gaussian_blur, brightness, rotation, downsample, gaussian_noise,
)

LFW_EMB       = ROOT / "data/embeddings_cache/lfw_embeddings.npz"
LFW_EXTRACTED = ROOT / "data/raw/lfw/lfw_extracted"
ARCFACE_ONNX  = Path.home() / ".insightface/models/buffalo_l/w600k_r50.onnx"
PLOT_OUT      = ROOT / "outputs/plots/robustness_degradation.png"
JSON_OUT      = ROOT / "outputs/reports/robustness_results.json"

THRESHOLD = 0.1810
N_PAIRS   = 1000
SEED      = 42

# Perturbation sweep configs: (name, fn, severities, x_label)
PERTURBATIONS = [
    ("Gaussian Blur",   gaussian_blur,   [0, 1, 2, 4, 8],               "σ (px)"),
    ("Brightness",      brightness,      [1.0, 0.6, 0.3, 0.1, 2.0, 3.0], "factor"),
    ("Rotation",        rotation,        [0, 5, 10, 20, 45, 90],          "angle (°)"),
    ("Downsample",      downsample,      [1.0, 0.5, 0.25, 0.125, 0.0625], "scale"),
    ("Gaussian Noise",  gaussian_noise,  [0, 10, 25, 50, 100],            "σ (px value)"),
]


def load_arcface():
    """
    Load ArcFace recognition model directly (no RetinaFace detection stage).

    LFW extracted images are 112×112 pre-aligned face crops — RetinaFace
    cannot detect faces in these tiny crops.  We run ArcFace directly with
    the same normalisation the model was trained with: (pixel − 127.5) / 127.5.
    """
    import onnxruntime as ort
    sess = ort.InferenceSession(
        str(ARCFACE_ONNX),
        providers=["CoreMLExecutionProvider", "CPUExecutionProvider"],
    )
    inp_name = sess.get_inputs()[0].name
    return sess, inp_name


def extract_embedding(sess, inp_name: str, img_bgr: np.ndarray) -> np.ndarray | None:
    """
    Extract ArcFace embedding from a 112×112 BGR image.
    Returns L2-normalised 512-dim float32 vector, or None if image is bad.
    """
    if img_bgr is None or img_bgr.shape[:2] != (112, 112):
        # Resize to 112×112 if not already (e.g. after downsample+upsample)
        if img_bgr is None:
            return None
        img_bgr = cv2.resize(img_bgr, (112, 112), interpolation=cv2.INTER_LINEAR)
    norm = (img_bgr.astype(np.float32) - 127.5) / 127.5
    inp  = norm.transpose(2, 0, 1)[np.newaxis]          # (1, 3, 112, 112)
    out  = sess.run(None, {inp_name: inp})[0][0]        # (512,)
    nrm  = np.linalg.norm(out)
    if nrm < 1e-6:
        return None
    return (out / nrm).astype(np.float32)


def evaluate_perturbation(sess, inp_name, pair_indices, fn, severity,
                           cached_embs) -> dict:
    """
    Apply fn(img, severity) to the B-side of each pair, re-extract via
    ArcFace directly, compute similarity vs. A-side cached embedding.
    """
    sims      = []
    n_matched = 0
    n_valid   = 0

    for pair_idx in pair_indices:
        emb_a = cached_embs[pair_idx * 2]           # A-side cached

        b_path = LFW_EXTRACTED / f"pair_{pair_idx:04d}_b.jpg"
        img    = cv2.imread(str(b_path))
        if img is None:
            continue

        perturbed = fn(img, severity)
        emb_b     = extract_embedding(sess, inp_name, perturbed)
        if emb_b is None:
            continue

        sim = float(np.dot(emb_a, emb_b))
        sims.append(sim)
        n_valid   += 1
        n_matched += int(sim >= THRESHOLD)

    match_rate = n_matched / n_valid if n_valid > 0 else 0.0
    mean_sim   = float(np.mean(sims)) if sims else 0.0
    return {"match_rate": match_rate, "mean_sim": mean_sim, "n_valid": n_valid}


def plot_degradation(results: dict, save_path: str) -> None:
    """Publication-quality degradation curves for all perturbation types."""
    n_types = len(results)
    fig, axes = plt.subplots(1, n_types, figsize=(4 * n_types, 5), dpi=120)
    if n_types == 1:
        axes = [axes]

    colors = ["#2b6cb0", "#c05621", "#2f855a", "#744210", "#6b46c1"]

    for ax, (name, data), color in zip(axes, results.items(), colors):
        sevs  = [d["severity"] for d in data]
        rates = [d["match_rate"] * 100 for d in data]

        ax.plot(sevs, rates, color=color, linewidth=2.2,
                marker="o", markersize=6)
        ax.axhline(y=rates[0], color="gray", linestyle="--", linewidth=1.0,
                   alpha=0.5, label=f"Baseline {rates[0]:.1f}%")
        ax.set_title(name, fontsize=11, fontweight="bold")
        ax.set_xlabel(results[name][0].get("x_label", "severity"), fontsize=9)
        ax.set_ylabel("Match Rate (%)", fontsize=9)
        ax.set_ylim([0, 105])
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)

    plt.suptitle(
        f"Robustness Degradation — ArcFace buffalo_l\n"
        f"(N={N_PAIRS} LFW genuine pairs, threshold={THRESHOLD})",
        fontsize=12, fontweight="bold",
    )
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Degradation plot saved → {save_path}")


def main():
    rng = np.random.default_rng(SEED)

    # ── Select 1000 genuine pairs ─────────────────────────────────────────────
    data    = np.load(str(LFW_EMB), allow_pickle=True)
    issame  = data["issame"].astype(bool)
    cached_embs = data["embeddings"]          # (12000, 512)
    genuine = np.where(issame)[0]
    pair_indices = rng.choice(genuine, size=min(N_PAIRS, len(genuine)), replace=False)
    print(f"Selected {len(pair_indices)} genuine pairs for robustness eval.")

    # ── Load ArcFace recognition model (direct — no RetinaFace) ──────────────
    print("Loading ArcFace model (direct, no RetinaFace) …")
    sess, inp_name = load_arcface()
    # Sanity-check on first genuine pair
    b0 = LFW_EXTRACTED / f"pair_{pair_indices[0]:04d}_b.jpg"
    img0 = cv2.imread(str(b0))
    emb_test = extract_embedding(sess, inp_name, img0)
    emb_cache = cached_embs[pair_indices[0] * 2 + 1]
    sim_check = float(np.dot(emb_test, emb_cache))
    print(f"Model ready. Sanity-check similarity (re-extracted vs cached): {sim_check:.4f}")
    print(f"  (expected ~0.9+ for same 112×112 image)\n")

    # ── Evaluate each perturbation ────────────────────────────────────────────
    all_results = {}

    for name, fn, severities, x_label in PERTURBATIONS:
        print(f"[{name}]  severities: {severities}")
        pert_results = []

        for sev in severities:
            t0 = time.perf_counter()
            res = evaluate_perturbation(sess, inp_name, pair_indices, fn, sev,
                                        cached_embs)
            elapsed = time.perf_counter() - t0
            pert_results.append({
                "severity":   sev,
                "match_rate": res["match_rate"],
                "mean_sim":   res["mean_sim"],
                "n_valid":    res["n_valid"],
                "x_label":    x_label,
            })
            print(f"  sev={sev:>6}  match_rate={res['match_rate']*100:.1f}%  "
                  f"mean_sim={res['mean_sim']:.4f}  ({elapsed:.1f}s)")

        all_results[name] = pert_results
        baseline = pert_results[0]["match_rate"] * 100
        worst    = min(d["match_rate"] for d in pert_results) * 100
        drop     = baseline - worst
        print(f"  → Drop: {drop:.1f} pp (baseline {baseline:.1f}% → worst {worst:.1f}%)\n")

    # ── Plot ──────────────────────────────────────────────────────────────────
    plot_degradation(all_results, str(PLOT_OUT))

    # ── Save JSON ─────────────────────────────────────────────────────────────
    json_payload = {
        "task":           "robustness_evaluation",
        "n_pairs":        int(len(pair_indices)),
        "threshold":      THRESHOLD,
        "perturbations":  all_results,
    }
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_OUT, "w") as f:
        json.dump(json_payload, f, indent=2)
    print(f"Results saved → {JSON_OUT}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "="*55)
    print("  ROBUSTNESS SUMMARY")
    print("="*55)
    for name, rows in all_results.items():
        base  = rows[0]["match_rate"] * 100
        worst = min(r["match_rate"] for r in rows) * 100
        print(f"  {name:<22}  baseline={base:.1f}%  worst={worst:.1f}%  drop={base-worst:.1f} pp")
    print("="*55 + "\n")


if __name__ == "__main__":
    main()
