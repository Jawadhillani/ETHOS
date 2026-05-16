"""
Image perturbation functions for robustness evaluation.

All functions accept and return uint8 BGR numpy arrays (cv2 convention).
Designed to test how degraded images affect ArcFace embedding similarity.

Perturbation types modelled after NIST FRVT robustness test conditions:
  - Gaussian blur        (lens defocus / motion blur)
  - Brightness shift     (lighting variation)
  - Rotation             (off-angle presentation)
  - Downsampling         (low-resolution capture)
  - Gaussian noise       (sensor / compression noise)
"""

from __future__ import annotations

import cv2
import numpy as np


def gaussian_blur(img: np.ndarray, sigma: float) -> np.ndarray:
    """
    Apply Gaussian blur.

    Args:
        img:   BGR uint8 image.
        sigma: Standard deviation in pixels.  0 = no change.
    """
    if sigma <= 0:
        return img.copy()
    # Kernel size must be odd and large enough to contain the Gaussian
    ksize = int(6 * sigma + 1)
    if ksize % 2 == 0:
        ksize += 1
    return cv2.GaussianBlur(img, (ksize, ksize), sigma)


def brightness(img: np.ndarray, factor: float) -> np.ndarray:
    """
    Multiply pixel values by `factor` (clip to [0, 255]).

    Args:
        img:    BGR uint8 image.
        factor: 1.0 = unchanged, <1 = darker, >1 = brighter.
    """
    out = img.astype(np.float32) * factor
    return np.clip(out, 0, 255).astype(np.uint8)


def rotation(img: np.ndarray, deg: float) -> np.ndarray:
    """
    Rotate image around its centre by `deg` degrees (counter-clockwise).

    Args:
        img: BGR uint8 image.
        deg: Rotation angle in degrees.  0 = no change.
    """
    if deg == 0:
        return img.copy()
    h, w = img.shape[:2]
    M    = cv2.getRotationMatrix2D((w / 2, h / 2), deg, 1.0)
    return cv2.warpAffine(img, M, (w, h),
                          flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)


def downsample(img: np.ndarray, scale: float) -> np.ndarray:
    """
    Downscale then upscale back to original resolution (simulates low-res capture).

    Args:
        img:   BGR uint8 image.
        scale: Fraction of original size to downscale to.
               1.0 = no change, 0.25 = downscale to 25% then back.
    """
    if scale >= 1.0:
        return img.copy()
    h, w  = img.shape[:2]
    small = cv2.resize(img, (max(1, int(w * scale)), max(1, int(h * scale))),
                       interpolation=cv2.INTER_LINEAR)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)


def gaussian_noise(img: np.ndarray, sigma: float) -> np.ndarray:
    """
    Add zero-mean Gaussian noise.

    Args:
        img:   BGR uint8 image.
        sigma: Standard deviation of the noise.  0 = no change.
    """
    if sigma <= 0:
        return img.copy()
    noise = np.random.normal(0, sigma, img.shape).astype(np.float32)
    out   = img.astype(np.float32) + noise
    return np.clip(out, 0, 255).astype(np.uint8)
