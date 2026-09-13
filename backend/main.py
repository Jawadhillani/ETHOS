"""
ETHOS FastAPI backend — serves the React frontend's API calls.
Run: /opt/miniconda3/envs/ethos/bin/uvicorn backend.main:app --reload --port 8000
"""

import base64
import io
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pydantic import BaseModel

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import app.state as state
from src.matching.engine import MatchingEngine
from src.matching.verifier import Verifier
from src.matching.identifier import Identifier
from src.llm.ethics_officer import EthicsOfficer
from src.security.pad_detector import PADDetector

DEFAULT_THRESHOLD = 0.1810

app = FastAPI(title="ETHOS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Lazy singletons ───────────────────────────────────────────────────────────

_verifier:   Verifier      | None = None
_identifier: Identifier    | None = None
_officer:    EthicsOfficer | None = None
_pad:        PADDetector   | None = None


def get_verifier(threshold: float = DEFAULT_THRESHOLD) -> Verifier:
    global _verifier
    if _verifier is None or _verifier.engine.threshold != threshold:
        _verifier = Verifier(engine=MatchingEngine(threshold=threshold))
    return _verifier


def get_identifier() -> Identifier:
    global _identifier
    if _identifier is None:
        _identifier = Identifier(batch_size=5000)
    return _identifier


def get_officer() -> EthicsOfficer:
    global _officer
    if _officer is None:
        _officer = EthicsOfficer()
    return _officer


def get_pad() -> PADDetector:
    global _pad
    if _pad is None:
        _pad = PADDetector()
    return _pad


def _embed_image(img_array: np.ndarray) -> tuple[np.ndarray | None, str]:
    """Extract ArcFace embedding from a numpy RGB image."""
    from app.inference import embed_image as _embed
    import tempfile, cv2
    bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        cv2.imwrite(f.name, bgr)
        emb, msg = _embed(f.name)
    os.unlink(f.name)
    return emb, msg


def _file_to_array(upload: UploadFile) -> np.ndarray:
    data = upload.file.read()
    img = Image.open(io.BytesIO(data)).convert("RGB")
    return np.array(img)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/api/verify")
async def verify(
    image_a: UploadFile = File(...),
    image_b: UploadFile = File(...),
    threshold: float = Form(DEFAULT_THRESHOLD),
):
    arr_a = _file_to_array(image_a)
    arr_b = _file_to_array(image_b)
    emb_a, msg_a = _embed_image(arr_a)
    emb_b, msg_b = _embed_image(arr_b)
    if emb_a is None:
        raise HTTPException(400, f"Image A: {msg_a}")
    if emb_b is None:
        raise HTTPException(400, f"Image B: {msg_b}")
    result = get_verifier(threshold).verify(emb_a, emb_b)
    return {"similarity": float(result.similarity), "is_match": bool(result.is_match), "threshold": threshold}


@app.post("/api/identify")
async def identify(
    image: UploadFile = File(...),
    top_k: int = Form(5),
):
    arr = _file_to_array(image)
    emb, msg = _embed_image(arr)
    if emb is None:
        raise HTTPException(400, msg)

    ff            = state.fairface()
    gallery_embs  = ff["embeddings"]
    gallery_files = ff["filenames"]
    gallery_race  = ff["race"]
    gallery_gender = ff["gender"]

    result = get_identifier().identify(
        emb, gallery_embs,
        gallery_ids=list(range(len(gallery_files))),
        top_k=top_k,
    )
    results = []
    for rank, (idx, sim) in enumerate(zip(result.top_k_indices, result.top_k_similarities), 1):
        results.append({
            "rank": rank,
            "filename": str(gallery_files[idx]).split("/")[-1],
            "race": str(gallery_race[idx]),
            "gender": str(gallery_gender[idx]),
            "similarity": float(sim),
        })
    return {"results": results, "n_gallery": len(gallery_embs)}


@app.get("/api/fairness")
async def fairness():
    return state.fairness_report()


@app.get("/api/metrics")
async def metrics():
    m = state.id_metrics()
    r = state.robustness_results() if state.ROBUSTNESS_JSON.exists() else None
    return {"id_metrics": m, "robustness": r}


class ChatRequest(BaseModel):
    message: str
    history: list[dict[str, str]] = []


@app.post("/api/chat")
async def chat(req: ChatRequest):
    import anthropic
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")

    # Build system context
    parts = ["You are the Ethics Officer of ETHOS.\n\n"]
    if state.FAIRNESS_JSON.exists():
        parts.append("FAIRNESS AUDIT:\n" + json.dumps(state.fairness_report(), indent=2))
    if state.ID_METRICS_JSON.exists():
        parts.append("\n\nIDENTIFICATION METRICS:\n" + json.dumps(state.id_metrics(), indent=2))
    parts.append("\n\nAnswer questions about bias, EU AI Act compliance, accuracy, or robustness. Be precise and cite numbers.")
    system_ctx = "".join(parts)

    api_messages = []
    for msg in req.history:
        api_messages.append({"role": msg["role"], "content": msg["content"]})
    api_messages.append({"role": "user", "content": req.message})

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_ctx,
        messages=api_messages,
    )
    return {"reply": response.content[0].text}


class ExplainRequest(BaseModel):
    context_type: str  # "verify" | "identify"
    data: dict


@app.post("/api/explain")
async def explain(req: ExplainRequest):
    import anthropic
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")

    PLAIN = "Reply in plain text only — no markdown, no bullet points, no bold, no headers. Maximum 3 sentences."
    CTX   = "ETHOS is a facial biometric fairness auditor built for EU AI Act compliance research. It studies demographic disparities in ArcFace recognition accuracy across race, gender, and age groups using the FairFace 86k dataset."

    if req.context_type == "verify":
        sim       = req.data["similarity"]
        threshold = req.data["threshold"]
        delta     = abs(threshold - sim)
        verdict   = "ACCEPTED" if sim >= threshold else "REJECTED"
        prompt = (
            f"{CTX}\n\n"
            f"A 1:1 face verification was {verdict}.\n"
            f"ArcFace cosine similarity: {sim:.4f} | Decision threshold (EER-optimal): {threshold:.4f} | Gap: {delta:.4f}\n\n"
            f"Explain in exactly 3 plain sentences focused on FAIRNESS: "
            f"(1) what this cosine similarity score means in terms of biometric embedding distance, "
            f"(2) how the chosen EER-optimal threshold affects different demographic groups differently "
            f"(a single threshold can cause higher false rejection rates for underrepresented groups), "
            f"and (3) the EU AI Act Article 10 implication — whether this outcome could reflect "
            f"training data bias or demographic underrepresentation in ArcFace. {PLAIN}"
        )
    elif req.context_type == "identify":
        results   = req.data["results"]
        n_gallery = req.data.get("n_gallery", "unknown")
        if not results:
            raise HTTPException(400, "No results to explain")

        best_sim  = results[0]["similarity"]
        spread    = results[0]["similarity"] - results[-1]["similarity"] if len(results) > 1 else 0

        # Demographic distribution of top-K
        from collections import Counter
        race_counts   = Counter(r.get("race", "Unknown") for r in results)
        gender_counts = Counter(r.get("gender", "Unknown") for r in results)
        top_race      = results[0].get("race", "Unknown")
        top_gender    = results[0].get("gender", "Unknown")

        race_str   = ", ".join(f"{v}× {k}" for k, v in race_counts.most_common())
        gender_str = ", ".join(f"{v}× {k}" for k, v in gender_counts.most_common())

        prompt = (
            f"{CTX}\n\n"
            f"A 1:N face search against a {n_gallery}-image FairFace gallery returned {len(results)} nearest neighbours.\n"
            f"Top match: similarity {best_sim:.4f} | FairFace-predicted demographics: {top_race}, {top_gender}\n"
            f"Score spread across all ranks: {spread:.4f}\n"
            f"Demographic distribution of top-{len(results)} matches — Race: {race_str} | Gender: {gender_str}\n\n"
            f"Explain in exactly 3 plain sentences focused on FAIRNESS: "
            f"(1) what the demographic distribution of the top-K matches reveals about the probe face "
            f"and how ArcFace embedding space clusters by race/gender, "
            f"(2) what the score spread indicates about demographic ambiguity — a tight spread where "
            f"all races score similarly suggests the model may not discriminate well across groups, "
            f"(3) the EU AI Act high-risk system implication: what these demographic predictions mean "
            f"for bias auditing and whether the results suggest an underrepresented group. {PLAIN}"
        )
    else:
        raise HTTPException(400, f"Unknown context_type: {req.context_type}")

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return {"explanation": response.content[0].text}


@app.post("/api/report")
async def report():
    officer = get_officer()
    rep     = state.fairness_report()
    analysis = officer.analyze_fairness_report(rep)
    summary  = officer.generate_compliance_summary(rep)

    from src.reports.compliance_pdf import ComplianceReportGenerator
    gen   = ComplianceReportGenerator(plots_dir=str(state.PLOTS_DIR))
    ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"ethos_compliance_audit_{ts}.pdf"
    pdf_path = str(Path(state.REPORTS_DIR).resolve() / fname)
    gen.generate(rep, analysis, summary, pdf_path)

    size_kb = Path(pdf_path).stat().st_size // 1024
    return {
        "pdf_url": f"/api/files/{fname}",
        "size_kb": size_kb,
        "filename": fname,
    }


@app.get("/api/files/{fname}")
async def serve_file(fname: str):
    path = Path(state.REPORTS_DIR).resolve() / fname
    if not path.exists():
        raise HTTPException(404, "File not found")
    return FileResponse(str(path), media_type="application/pdf", filename=fname)


@app.get("/api/plots/{fname}")
async def serve_plot(fname: str):
    path = Path(state.PLOTS_DIR).resolve() / fname
    if not path.exists():
        raise HTTPException(404, "Plot not found")
    return FileResponse(str(path), media_type="image/png")


# ── Enrollment endpoints ──────────────────────────────────────────────────────

@app.post("/api/enroll")
async def enroll(
    name: str = Form(...),
    image: UploadFile = File(...),
):
    arr = _file_to_array(image)
    emb, msg = _embed_image(arr)
    if emb is None:
        raise HTTPException(400, msg)
    state.enrolled[name] = emb
    return {"enrolled": name, "total": len(state.enrolled)}


@app.get("/api/enrolled")
async def list_enrolled():
    return {"identities": list(state.enrolled.keys()), "count": len(state.enrolled)}


@app.delete("/api/enrolled/{name}")
async def delete_enrolled(name: str):
    if name not in state.enrolled:
        raise HTTPException(404, f"Identity '{name}' not found")
    del state.enrolled[name]
    return {"deleted": name, "total": len(state.enrolled)}


@app.post("/api/identify-enrolled")
async def identify_enrolled(
    image: UploadFile = File(...),
    top_k: int = Form(5),
):
    if not state.enrolled:
        raise HTTPException(400, "No enrolled identities. Enroll faces first.")
    arr = _file_to_array(image)
    emb, msg = _embed_image(arr)
    if emb is None:
        raise HTTPException(400, msg)

    names   = list(state.enrolled.keys())
    gallery = np.stack([state.enrolled[n] for n in names])
    k       = min(top_k, len(names))

    result = get_identifier().identify(
        emb, gallery,
        gallery_ids=list(range(len(names))),
        top_k=k,
    )
    results = [
        {"rank": rank, "name": names[idx], "similarity": float(sim)}
        for rank, (idx, sim) in enumerate(
            zip(result.top_k_indices, result.top_k_similarities), 1
        )
    ]
    return {"results": results, "n_enrolled": len(names)}


class LivenessRequest(BaseModel):
    frame_b64: str


@app.post("/api/liveness")
async def liveness(req: LivenessRequest):
    import cv2
    data = base64.b64decode(req.frame_b64)
    arr  = np.frombuffer(data, dtype=np.uint8)
    img  = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return {"is_real": False, "real_score": 0.0, "attack_label": "decode_error", "inference_ms": 0}

    from app.inference import _model as _insightface_model
    app_if = _insightface_model()
    faces  = app_if.get(img)

    if not faces:
        return {"is_real": None, "real_score": None, "attack_label": None, "inference_ms": 0}

    t0 = time.perf_counter()
    bbox = faces[0].bbox.astype(int)
    pad  = get_pad().score(img, bbox)
    inf_ms = (time.perf_counter() - t0) * 1000

    return {
        "is_real":      bool(pad.is_real),
        "real_score":   float(pad.real_score),
        "attack_label": pad.attack_label,
        "inference_ms": round(inf_ms, 2),
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting ETHOS API on http://127.0.0.1:8000")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
