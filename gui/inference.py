"""
Inference helpers for the GUI — face embedding extraction from uploaded images.
"""

import cv2
import numpy as np
from pathlib import Path
from insightface.app import FaceAnalysis

_app: FaceAnalysis | None = None


def _model() -> FaceAnalysis:
    global _app
    if _app is None:
        _app = FaceAnalysis(
            name="buffalo_l",
            providers=["CoreMLExecutionProvider", "CPUExecutionProvider"],
        )
        _app.prepare(ctx_id=0, det_size=(640, 640))
    return _app


def embed_image(image_path: str) -> tuple[np.ndarray | None, str]:
    """
    Extract a 512-dim L2-normalised embedding from an uploaded image.

    Returns (embedding, status_message). Embedding is None on failure.
    """
    img = cv2.imread(str(image_path))
    if img is None:
        return None, "Could not read image."

    faces = _model().get(img)
    if not faces:
        return None, "No face detected. Try a clearer, well-lit frontal photo."

    face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
    emb = face.normed_embedding.astype(np.float32)
    return emb, f"Face detected. Embedding extracted (512-dim, norm={float(np.linalg.norm(emb)):.4f})."
