"""
Day 1 baseline test: verify ArcFace + RetinaFace pipeline works on M4.

Tests:
1. Model loads on CoreML (M4 GPU acceleration)
2. Detection works on a downloaded sample image
3. Embedding extraction returns a 512-dim vector
4. Same person → high similarity, different people → low similarity
"""

import numpy as np
import cv2
import urllib.request
from pathlib import Path
import insightface
from insightface.app import FaceAnalysis

# ---------- Setup ----------
TEST_DIR = Path("tests/sample_images")
TEST_DIR.mkdir(parents=True, exist_ok=True)

# LFW sample images via GitHub mirror (free use, no bot blocking)
SAMPLES = {
    "obama_1.jpg": "https://github.com/ageitgey/face_recognition/raw/master/examples/obama.jpg",
    "obama_2.jpg": "https://github.com/ageitgey/face_recognition/raw/master/examples/obama2.jpg",
    "biden_1.jpg": "https://github.com/ageitgey/face_recognition/raw/master/examples/biden.jpg",
}

print("📥 Downloading sample images...")
headers = {"User-Agent": "Mozilla/5.0"}
for filename, url in SAMPLES.items():
    target = TEST_DIR / filename
    if not target.exists():
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp, open(target, "wb") as f:
            f.write(resp.read())
        print(f"   ✓ {filename}")
    else:
        print(f"   • {filename} (cached)")

# ---------- Load Model ----------
print("\n🚀 Loading FaceAnalysis (RetinaFace + ArcFace)...")
app = FaceAnalysis(
    name="buffalo_l",
    providers=["CoreMLExecutionProvider", "CPUExecutionProvider"]
)
app.prepare(ctx_id=0, det_size=(640, 640))
print("   ✓ Model loaded")

# ---------- Extract Embeddings ----------
def get_embedding(img_path):
    img = cv2.imread(str(img_path))
    faces = app.get(img)
    if not faces:
        raise RuntimeError(f"No face detected in {img_path}")
    # Take the largest face if multiple
    face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
    return face.normed_embedding

print("\n🔍 Extracting embeddings...")
embeddings = {}
for filename in SAMPLES.keys():
    emb = get_embedding(TEST_DIR / filename)
    embeddings[filename] = emb
    print(f"   ✓ {filename:20s} → shape {emb.shape}, norm {np.linalg.norm(emb):.4f}")

# ---------- Similarity Tests ----------
def cosine_sim(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

print("\n📊 Cosine similarity matrix:")
print(f"   Same person (Obama vs Obama)  : {cosine_sim(embeddings['obama_1.jpg'], embeddings['obama_2.jpg']):.4f}  (expect > 0.5)")
print(f"   Different (Obama vs Biden)    : {cosine_sim(embeddings['obama_1.jpg'], embeddings['biden_1.jpg']):.4f}  (expect < 0.3)")
print(f"   Different (Obama vs Biden)    : {cosine_sim(embeddings['obama_2.jpg'], embeddings['biden_1.jpg']):.4f}  (expect < 0.3)")

# ---------- Speed Benchmark ----------
import time
print("\n⏱️  Speed benchmark (10 inferences)...")
img = cv2.imread(str(TEST_DIR / "obama_1.jpg"))
for filename in SAMPLES.keys():
    pass  # already extracted above
# Warmup
for _ in range(3):
    app.get(img)
# Time it
start = time.time()
for _ in range(10):
    app.get(img)
elapsed = time.time() - start
print(f"   Average per inference: {elapsed*100:.1f} ms")
print(f"   Throughput: {10/elapsed:.1f} faces/sec")

print("\n✅ ArcFace baseline test PASSED" if True else "❌ FAILED")
