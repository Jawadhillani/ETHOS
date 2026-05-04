"""
ArcFace embedding extractor for ETHOS.

Uses InsightFace buffalo_l (RetinaFace + ArcFace) with CoreML acceleration.
All embeddings are L2-normalised 512-dim vectors.
"""

import logging
import os
from pathlib import Path

import cv2
import numpy as np
from insightface.app import FaceAnalysis
from tqdm import tqdm

logger = logging.getLogger(__name__)


class EmbeddingExtractor:
    """
    Wraps InsightFace FaceAnalysis for batch embedding extraction.

    Usage:
        extractor = EmbeddingExtractor()
        emb = extractor.extract_single("path/to/image.jpg")   # (512,) or None
        results = extractor.extract_batch(["a.jpg", "b.jpg"]) # list of (512,) or None
    """

    def __init__(
        self,
        model_name: str = "buffalo_l",
        det_size: tuple = (640, 640),
        providers: list = None,
    ):
        if providers is None:
            providers = ["CoreMLExecutionProvider", "CPUExecutionProvider"]

        self.app = FaceAnalysis(name=model_name, providers=providers)
        self.app.prepare(ctx_id=0, det_size=det_size)
        logger.info(f"EmbeddingExtractor ready — model={model_name}, providers={providers}")

    def extract_single(self, image_path: str) -> np.ndarray | None:
        """
        Extract embedding for the largest face in an image.

        Returns:
            np.ndarray of shape (512,) — L2-normalised, or None if no face detected.
        """
        img = cv2.imread(str(image_path))
        if img is None:
            logger.warning(f"Could not read image: {image_path}")
            return None

        faces = self.app.get(img)
        if not faces:
            logger.warning(f"No face detected: {image_path}")
            return None

        # Pick the largest bounding box if multiple faces
        face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
        return face.normed_embedding.astype(np.float32)

    def extract_batch(
        self,
        image_paths: list,
        error_log: str = None,
        desc: str = "Extracting",
    ) -> tuple[list, list]:
        """
        Extract embeddings for a list of image paths.

        Args:
            image_paths: list of path strings
            error_log:   optional file path to log skipped images
            desc:        tqdm bar label

        Returns:
            (embeddings, valid_paths)
            embeddings:  list of np.ndarray (512,) — one per successfully processed image
            valid_paths: list of str — paths that matched an embedding (same order)
        """
        embeddings = []
        valid_paths = []
        skipped = []

        for path in tqdm(image_paths, desc=desc, unit="img", dynamic_ncols=True):
            emb = self.extract_single(path)
            if emb is not None:
                embeddings.append(emb)
                valid_paths.append(str(path))
            else:
                skipped.append(str(path))

        if skipped:
            logger.warning(f"Skipped {len(skipped)} images (no face or unreadable)")
            if error_log:
                Path(error_log).parent.mkdir(parents=True, exist_ok=True)
                with open(error_log, "a") as f:
                    f.write("\n".join(skipped) + "\n")

        return embeddings, valid_paths

    def extract_chip(self, image_path: str) -> np.ndarray | None:
        """
        Extract embedding from a pre-cropped face chip (e.g. LFW 112×112 images).
        Bypasses RetinaFace detection — feeds directly to ArcFace recognition model.

        Returns:
            np.ndarray of shape (512,) — L2-normalised, or None on read error.
        """
        img = cv2.imread(str(image_path))
        if img is None:
            logger.warning(f"Could not read image: {image_path}")
            return None

        img = cv2.resize(img, (112, 112))
        rec = self.app.models["recognition"]
        feat = rec.get_feat(img)            # (1, 512), unnormalized
        feat = feat.flatten().astype(np.float32)
        feat /= np.linalg.norm(feat)        # L2-normalise
        return feat

    def extract_chips_batch(
        self,
        image_paths: list,
        error_log: str = None,
        desc: str = "Extracting chips",
    ) -> tuple[list, list]:
        """
        Batch version of extract_chip for pre-cropped face images.
        Same return signature as extract_batch.
        """
        embeddings = []
        valid_paths = []
        skipped = []

        for path in tqdm(image_paths, desc=desc, unit="img", dynamic_ncols=True):
            emb = self.extract_chip(path)
            if emb is not None:
                embeddings.append(emb)
                valid_paths.append(str(path))
            else:
                skipped.append(str(path))

        if skipped:
            logger.warning(f"Skipped {len(skipped)} chips (unreadable)")
            if error_log:
                Path(error_log).parent.mkdir(parents=True, exist_ok=True)
                with open(error_log, "a") as f:
                    f.write("\n".join(skipped) + "\n")

        return embeddings, valid_paths

    def save_embeddings(
        self,
        embeddings: list,
        valid_paths: list,
        output_path: str,
        labels: dict = None,
    ) -> None:
        """
        Save embeddings and metadata to a compressed .npz file.

        Args:
            embeddings:   list of (512,) arrays
            valid_paths:  list of filenames (same order as embeddings)
            output_path:  path to output .npz file
            labels:       optional dict of str -> array, e.g. {"race": [...], "gender": [...]}
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        emb_array = np.stack(embeddings, axis=0)  # (N, 512)
        payload = {
            "embeddings": emb_array,
            "filenames": np.array(valid_paths, dtype=object),
        }
        if labels:
            payload.update(labels)

        np.savez_compressed(str(output_path), **payload)
        logger.info(f"Saved {len(embeddings)} embeddings → {output_path} "
                    f"(shape {emb_array.shape})")
