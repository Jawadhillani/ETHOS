"""
Smoke tests for Verifier and Identifier.

Loads cached LFW + FairFace val embeddings and runs basic 1:1 and 1:N ops
on small subsets. No model inference — pure matching logic.

Run with:
    python tests/test_verifier_identifier.py
"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.matching.engine import MatchingEngine
from src.matching.verifier import Verifier
from src.matching.identifier import Identifier

# ── Load cached embeddings ────────────────────────────────────────────────────

CACHE_DIR = Path("data/embeddings_cache")

print("Loading LFW embeddings cache...")
lfw = np.load(CACHE_DIR / "lfw_embeddings.npz", allow_pickle=True)
lfw_embs = lfw["embeddings"]       # (12000, 512) float32
lfw_issame = lfw["issame"]         # (6000,) bool  — pair i → rows 2i, 2i+1
lfw_files = lfw["filenames"]       # (12000,)

print("Loading FairFace val embeddings cache...")
ffv = np.load(CACHE_DIR / "fairface_val_embeddings.npz", allow_pickle=True)
ff_embs = ffv["embeddings"]        # (10925, 512) float32
ff_files = ffv["filenames"]        # (10925,)

print(f"  LFW:        {lfw_embs.shape[0]:,} embeddings, {lfw_issame.sum():,} same-person pairs")
print(f"  FairFace val: {ff_embs.shape[0]:,} embeddings")


# ── Helpers ───────────────────────────────────────────────────────────────────

def lfw_pair(pair_idx):
    """Return (emb_a, emb_b, is_same) for LFW pair at index pair_idx."""
    return lfw_embs[2 * pair_idx], lfw_embs[2 * pair_idx + 1], bool(lfw_issame[pair_idx])


def find_first_same():
    for i in range(len(lfw_issame)):
        if lfw_issame[i]:
            return i
    raise RuntimeError("No same-person pairs found")


def find_first_diff():
    for i in range(len(lfw_issame)):
        if not lfw_issame[i]:
            return i
    raise RuntimeError("No diff-person pairs found")


# ── Tests ─────────────────────────────────────────────────────────────────────

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        print(f"  PASS  {name}" + (f"  ({detail})" if detail else ""))
        PASS += 1
    else:
        print(f"  FAIL  {name}" + (f"  ({detail})" if detail else ""))
        FAIL += 1


# ── 1. Verifier: single pair ──────────────────────────────────────────────────
print("\n[1] Verifier — single pair")

verifier = Verifier()

same_idx = find_first_same()
a, b, _ = lfw_pair(same_idx)
r = verifier.verify(a, b)
check("same-person match", r.is_match, f"sim={r.similarity:.4f}")
check("same-person sim > 0.4", r.similarity > 0.4, f"sim={r.similarity:.4f}")

diff_idx = find_first_diff()
a2, b2, _ = lfw_pair(diff_idx)
r2 = verifier.verify(a2, b2)
check("diff-person no-match", not r2.is_match, f"sim={r2.similarity:.4f}")
check("diff-person sim < threshold", r2.similarity < verifier.engine.threshold,
      f"sim={r2.similarity:.4f} < {r2.threshold}")


# ── 2. Verifier: batch ────────────────────────────────────────────────────────
print("\n[2] Verifier — batch (20 pairs)")

BATCH = 20
embs_a = lfw_embs[0:BATCH*2:2]   # even rows
embs_b = lfw_embs[1:BATCH*2:2]   # odd rows
labels = lfw_issame[:BATCH]

results = verifier.verify_batch(embs_a, embs_b)
check("batch returns 20 results", len(results) == BATCH, f"got {len(results)}")
check("VerifyResult has is_match", hasattr(results[0], "is_match"))
check("VerifyResult has similarity", hasattr(results[0], "similarity"))

# Spot-check accuracy on the 20 pairs
correct = sum(r.is_match == l for r, l in zip(results, labels))
check(f"batch accuracy >= 70%", correct / BATCH >= 0.70, f"{correct}/{BATCH}")


# ── 3. Identifier: 1:N single query ──────────────────────────────────────────
print("\n[3] Identifier — 1:N single query")

# Use 200 FairFace val embeddings as gallery; query with the first one
GALLERY_SIZE = 200
gallery = ff_embs[:GALLERY_SIZE]
gallery_ids = list(ff_files[:GALLERY_SIZE])
query = ff_embs[0]  # should be its own nearest neighbour

identifier = Identifier(batch_size=100)  # small batch to exercise chunking
result = identifier.identify(query, gallery, gallery_ids=gallery_ids, top_k=5)

check("returns 5 results", len(result.top_k_indices) == 5, f"got {len(result.top_k_indices)}")
check("top-1 is self (index 0)", result.top_k_indices[0] == 0,
      f"top-1 index={result.top_k_indices[0]}")
check("top-1 sim ≈ 1.0", result.top_k_similarities[0] > 0.999,
      f"sim={result.top_k_similarities[0]:.6f}")
check("ids populated", result.top_k_ids is not None)
check("results are sorted descending",
      result.top_k_similarities == sorted(result.top_k_similarities, reverse=True))


# ── 4. Identifier: batch queries ─────────────────────────────────────────────
print("\n[4] Identifier — batch queries (10 queries vs 200-item gallery)")

queries = ff_embs[:10]
batch_results = identifier.identify_batch(queries, gallery, gallery_ids=gallery_ids, top_k=3)

check("batch returns 10 results", len(batch_results) == 10)
check("each result has 3 hits", all(len(r.top_k_indices) == 3 for r in batch_results))

# Each query embedding is in the gallery, so top-1 index should equal query index
self_match = sum(r.top_k_indices[0] == i for i, r in enumerate(batch_results))
check("self is top-1 for all 10 queries", self_match == 10, f"{self_match}/10")


# ── 5. Chunking correctness ───────────────────────────────────────────────────
print("\n[5] Chunking correctness — batch_size=1 vs batch_size=5000")

id_small = Identifier(batch_size=1)
id_large = Identifier(batch_size=5000)

r_small = id_small.identify(ff_embs[5], gallery, top_k=5)
r_large = id_large.identify(ff_embs[5], gallery, top_k=5)

check("same top-1 index regardless of chunk size",
      r_small.top_k_indices[0] == r_large.top_k_indices[0],
      f"small={r_small.top_k_indices[0]}, large={r_large.top_k_indices[0]}")
check("similarities match to 5 decimal places",
      all(abs(a - b) < 1e-5 for a, b in zip(r_small.top_k_similarities, r_large.top_k_similarities)),
      f"small={r_small.top_k_similarities[:2]}, large={r_large.top_k_similarities[:2]}")


# ── 6. Custom threshold ───────────────────────────────────────────────────────
print("\n[6] Custom threshold")

strict = Verifier(engine=MatchingEngine(threshold=0.99))
a, b, _ = lfw_pair(same_idx)
r_strict = strict.verify(a, b)
check("threshold=0.99 rejects same-person pair", not r_strict.is_match,
      f"sim={r_strict.similarity:.4f} < 0.99")

lenient = Verifier(engine=MatchingEngine(threshold=0.01))
a2, b2, _ = lfw_pair(diff_idx)
r_lenient = lenient.verify(a2, b2)
check("threshold=0.01 accepts diff-person pair", r_lenient.is_match,
      f"sim={r_lenient.similarity:.4f} >= 0.01")


# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
total = PASS + FAIL
print(f"Result: {PASS}/{total} passed" + (" — ALL GOOD" if FAIL == 0 else f" — {FAIL} FAILED"))
if FAIL > 0:
    sys.exit(1)
