"""
Lazy-loaded global state for the ETHOS GUI.

Embeddings and the FairFace gallery are loaded on first access — startup stays
under 2 seconds even with an 86k-entry cache sitting on disk.
"""

import json
import threading
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent

# ── Paths ─────────────────────────────────────────────────────────────────────
LFW_CACHE      = ROOT / "data/embeddings_cache/lfw_embeddings.npz"
FF_TRAIN_CACHE = ROOT / "data/embeddings_cache/fairface_train_embeddings.npz"
FAIRNESS_JSON   = ROOT / "outputs/reports/fairness_audit.json"
ID_METRICS_JSON = ROOT / "outputs/reports/lfw_identification_metrics.json"
ROBUSTNESS_JSON = ROOT / "outputs/reports/robustness_results.json"
PLOTS_DIR       = ROOT / "outputs/plots"
REPORTS_DIR     = ROOT / "outputs/reports"

# ── Lazy state ────────────────────────────────────────────────────────────────
_lock = threading.Lock()

_lfw_data:    dict | None = None
_ff_data:     dict | None = None
_fairness:    dict | None = None
_id_metrics:  dict | None = None
_robustness:  dict | None = None

# In-session enrollment store: {label: np.ndarray (512,)}
enrolled: dict = {}


def lfw() -> dict:
    global _lfw_data
    if _lfw_data is None:
        with _lock:
            if _lfw_data is None:
                d = np.load(str(LFW_CACHE), allow_pickle=True)
                _lfw_data = {k: d[k] for k in d}
    return _lfw_data


def fairface() -> dict:
    global _ff_data
    if _ff_data is None:
        with _lock:
            if _ff_data is None:
                d = np.load(str(FF_TRAIN_CACHE), allow_pickle=True)
                _ff_data = {k: d[k] for k in d}
    return _ff_data


def fairness_report() -> dict:
    global _fairness
    if _fairness is None:
        with _lock:
            if _fairness is None:
                with open(FAIRNESS_JSON) as f:
                    _fairness = json.load(f)
    return _fairness


def id_metrics() -> dict:
    global _id_metrics
    if _id_metrics is None:
        with _lock:
            if _id_metrics is None:
                with open(ID_METRICS_JSON) as f:
                    _id_metrics = json.load(f)
    return _id_metrics


def robustness_results() -> dict:
    global _robustness
    if _robustness is None:
        with _lock:
            if _robustness is None:
                if ROBUSTNESS_JSON.exists():
                    with open(ROBUSTNESS_JSON) as f:
                        _robustness = json.load(f)
                else:
                    _robustness = {}
    return _robustness
