"""
Inference helpers for the GUI — face embedding extraction from uploaded images.

Uses PIL as the primary image loader (supports HEIC/HEIF from iPhone via
pillow-heif) then converts to BGR numpy array for InsightFace/cv2.
"""

import cv2
import numpy as np
from pathlib import Path
from PIL import Image
from insightface.app import FaceAnalysis

_app: FaceAnalysis | None = None


def _model() -> FaceAnalysis:
    """
    Return a singleton FaceAnalysis instance.

    CoreML EP is excluded here: it can fail with "Error in dynamically
    resizing for sequence length" on arbitrary-resolution uploaded images.
    CPU-only gives stable results at acceptable latency for non-live inference.
    The PAD detector (pad_detector.py) uses its own CoreML ONNX session which
    processes fixed 80×80 crops and is unaffected.
    """
    global _app
    if _app is None:
        _app = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"],
        )
        _app.prepare(ctx_id=0, det_size=(640, 640))
    return _app


def embed_image(image_path: str) -> tuple[np.ndarray | None, str]:
    """
    Extract a 512-dim L2-normalised embedding from an uploaded image.

    Returns (embedding, status_message). Embedding is None on failure.
    """
    # Use PIL so HEIC/HEIF (iPhone) and all other formats work, then convert
    # to BGR numpy array for InsightFace (which expects cv2-style images).
    try:
        pil_img = Image.open(str(image_path)).convert("RGB")
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        return None, f"Could not read image: {e}"

    faces = _model().get(img)
    if not faces:
        return None, "No face detected. Try a clearer, well-lit frontal photo."

    face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
    emb = face.normed_embedding.astype(np.float32)
    return emb, f"Face detected. Embedding extracted (512-dim, norm={float(np.linalg.norm(emb)):.4f})."
