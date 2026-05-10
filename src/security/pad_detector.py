"""
Presentation Attack Detector (PAD) — MiniFASNetV2, ONNX Runtime.

Model: Silent-Face-Anti-Spoofing / MiniFASNetV2
Weights: 2.7_80x80_MiniFASNetV2.pth → exported to ONNX
Architecture: 0.43M params, depthwise-separable MobileNet-style
Input: (1, 3, 80, 80) float32 in [0, 255] range (BGR channel order)
Output: (1, 3) raw logits — class 0: wrap/3D, class 1: real, class 2: print/replay
Performance: ~3ms / ~300 FPS on M4 (CoreML EP)

Usage:
    pad = PADDetector()
    result = pad.score(bgr_frame, bbox_xyxy)
    if result.is_real:
        embed(frame)
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort

ROOT = Path(__file__).parent.parent.parent
MODEL_PATH = ROOT / "data/models/pad/MiniFASNetV2_80x80.onnx"

# Class indices from CASIA-SURF training labels
_CLASS_REAL  = 1
_CLASS_NAMES = ["Wrap/3D Mask", "Real Face", "Print/Screen Replay"]

# Softmax thresholds for verdict display
_REAL_HIGH  = 0.75   # confident real → green
_REAL_LOW   = 0.45   # below this → definite spoof → red


@dataclass
class PADResult:
    real_score: float        # P(real) after softmax, in [0, 1]
    predicted_class: int     # argmax of softmax (1 = real)
    attack_label: str        # human-readable label
    is_real: bool            # True iff predicted_class == 1
    inference_ms: float      # wall-clock inference time

    @property
    def confidence_level(self) -> str:
        """One of: 'high', 'uncertain', 'spoof'."""
        if self.real_score >= _REAL_HIGH:
            return "high"
        if self.real_score >= _REAL_LOW:
            return "uncertain"
        return "spoof"

    @property
    def color_bgr(self) -> tuple[int, int, int]:
        mapping = {
            "high":      (47, 133, 90),   # green
            "uncertain": (246, 173, 85),  # orange
            "spoof":     (229, 62, 62),   # red
        }
        return mapping[self.confidence_level]


def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max())
    return e / e.sum()


def _crop_face_patch(bgr: np.ndarray, bbox_xyxy: np.ndarray,
                     scale: float = 2.7, size: int = 80) -> np.ndarray:
    """
    Expand the face bbox by `scale` and crop a square patch, resized to size×size.
    Matches CropImage logic from Silent-Face-Anti-Spoofing exactly.
    """
    h, w = bgr.shape[:2]
    x1, y1, x2, y2 = float(bbox_xyxy[0]), float(bbox_xyxy[1]), \
                      float(bbox_xyxy[2]), float(bbox_xyxy[3])
    bw = x2 - x1
    bh = y2 - y1
    cx = x1 + bw / 2
    cy = y1 + bh / 2

    # Clamp scale so crop stays within image
    scale = min(scale, min((h - 1) / bh, (w - 1) / bw))
    new_w = bw * scale
    new_h = bh * scale

    lx = int(max(0, cx - new_w / 2))
    ly = int(max(0, cy - new_h / 2))
    rx = int(min(w - 1, cx + new_w / 2))
    ry = int(min(h - 1, cy + new_h / 2))

    crop = bgr[ly : ry + 1, lx : rx + 1]
    return cv2.resize(crop, (size, size))


def _to_input(crop_bgr: np.ndarray) -> np.ndarray:
    """BGR uint8 HWC → float32 NCHW [0, 255] (matches to_tensor in SFA repo)."""
    return crop_bgr.astype(np.float32).transpose(2, 0, 1)[np.newaxis]


class PADDetector:
    """
    Presentation Attack Detector wrapping MiniFASNetV2 (ONNX).

    Thread-safe after construction (onnxruntime sessions are thread-safe).
    """

    def __init__(self, model_path: str | Path = MODEL_PATH) -> None:
        self._sess = ort.InferenceSession(
            str(model_path),
            providers=["CoreMLExecutionProvider", "CPUExecutionProvider"],
        )
        self._inp_name = self._sess.get_inputs()[0].name
        # Warmup — avoids cold-start latency on first real frame
        dummy = np.zeros((1, 3, 80, 80), dtype=np.float32)
        for _ in range(3):
            self._sess.run(None, {self._inp_name: dummy})

    def score(
        self,
        bgr_frame: np.ndarray,
        bbox_xyxy: np.ndarray | list,
        scale: float = 2.7,
    ) -> PADResult:
        """
        Run PAD on a single face.

        Args:
            bgr_frame:  Full-frame BGR image (from cv2 or InsightFace).
            bbox_xyxy:  Face bounding box [x1, y1, x2, y2] in pixel coords.
            scale:      Expansion factor for face crop (2.7 matches the model filename).

        Returns:
            PADResult with scores and verdict.
        """
        crop = _crop_face_patch(bgr_frame, bbox_xyxy, scale=scale, size=80)
        inp  = _to_input(crop)

        t0 = time.perf_counter()
        logits = self._sess.run(None, {self._inp_name: inp})[0][0]
        ms = (time.perf_counter() - t0) * 1000.0

        probs = _softmax(logits)
        pred  = int(np.argmax(probs))

        return PADResult(
            real_score      = float(probs[_CLASS_REAL]),
            predicted_class = pred,
            attack_label    = _CLASS_NAMES[pred],
            is_real         = (pred == _CLASS_REAL),
            inference_ms    = ms,
        )
