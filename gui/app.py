"""
ETHOS — Ethical Trust & Holistic Oversight System
Gradio GUI  |  Week 7

Run:
    /opt/miniconda3/envs/ethos/bin/python3 gui/app.py
"""

import json
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

# Register HEIC/HEIF support so iPhone photos work with PIL
import pillow_heif
pillow_heif.register_heif_opener()

import cv2
import gradio as gr
import numpy as np
import plotly.graph_objects as go

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from gui.styles import ethos_theme, CUSTOM_CSS
from gui.plots import (
    far_bar_chart, fmrd_gauge, score_distribution, roc_curve, similarity_bar,
    cmc_curve, robustness_chart,
)
import gui.state as state

from src.matching.engine import MatchingEngine
from src.matching.verifier import Verifier
from src.matching.identifier import Identifier
from src.llm.ethics_officer import EthicsOfficer
from src.security.pad_detector import PADDetector

DEFAULT_THRESHOLD = 0.1810

# Rolling FPS tracker shared across streaming frames
_fps_times: list = []


# ── Lazy singletons ───────────────────────────────────────────────────────────

_verifier:  Verifier     | None = None
_identifier: Identifier  | None = None
_officer:   EthicsOfficer | None = None
_pad:       PADDetector   | None = None


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


# ── Tab 1: Landing ────────────────────────────────────────────────────────────

LANDING_HTML = """
<div style="padding: 8px 0 16px 0;">
  <div class="hero-title">ETHOS <span class="hero-accent">—</span></div>
  <div class="hero-title" style="font-size:28px; font-weight:600; margin-top:-4px;">
    Ethical Trust &amp; Holistic Oversight System
  </div>
  <p class="hero-sub" style="margin-top:14px;">
    A facial biometric fairness auditor built for EU AI Act compliance.
    Measures recognition accuracy across race, gender, and age demographics —
    then generates a regulator-ready compliance report.
  </p>
  <hr class="hero-divider"/>
  <div class="stat-row">
    <div class="stat-item">
      <div class="stat-num">99.70%</div>
      <div class="stat-desc">LFW Accuracy</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">0.30%</div>
      <div class="stat-desc">Equal Error Rate</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">9.19×</div>
      <div class="stat-desc">Race FMRD (FAIL)</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">42.30×</div>
      <div class="stat-desc">Age FMRD (FAIL)</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">1.37×</div>
      <div class="stat-desc">Gender FMRD (PASS)</div>
    </div>
  </div>
  <hr class="hero-divider"/>
  <div class="stat-row">
    <div class="stat-item">
      <div class="stat-num">47.87%</div>
      <div class="stat-desc">1:N Rank-1 (3k gallery)</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">97.30%</div>
      <div class="stat-desc">1:N Rank-5</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">99.77%</div>
      <div class="stat-desc">1:N Rank-10</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">MiniFASNet</div>
      <div class="stat-desc">PAD · 299 FPS on M4</div>
    </div>
  </div>
  <hr class="hero-divider"/>
  <p style="color:#a0aec0; font-size:13px; line-height:1.7; max-width:680px;">
    <b style="color:#e2e8f0;">Stack:</b>
    InsightFace buffalo_l · ArcFace · RetinaFace · CoreML (Apple M4) ·
    FairFace (86k images) · LFW (12k images) · Anthropic claude-sonnet-4-5 · EU AI Act
    <br/>
    <b style="color:#e2e8f0;">Author:</b> Jawad · UPEC Master's Thesis · Spring 2026
  </p>
</div>
"""


# ── Tab 2: Verify ─────────────────────────────────────────────────────────────

def verify_faces(img_a_path, img_b_path, threshold):
    from gui.inference import embed_image

    if img_a_path is None or img_b_path is None:
        return None, "Upload both images first.", ""

    emb_a, msg_a = embed_image(img_a_path)
    emb_b, msg_b = embed_image(img_b_path)

    if emb_a is None:
        return None, f"Image 1: {msg_a}", ""
    if emb_b is None:
        return None, f"Image 2: {msg_b}", ""

    result = get_verifier(threshold).verify(emb_a, emb_b)
    sim    = result.similarity
    match  = result.is_match

    verdict_html = f"""
    <div class="ethos-card" style="text-align:center;">
      <div style="font-size:36px; margin-bottom:8px;">
        {'✅' if match else '❌'}
      </div>
      <div style="font-size:20px; font-weight:700;
                  color:{'#2f855a' if match else '#e53e3e'};">
        {'MATCH' if match else 'NO MATCH'}
      </div>
      <div style="font-size:13px; color:#a0aec0; margin-top:6px;">
        Similarity: <b style="color:#e2e8f0;">{sim:.4f}</b>
        &nbsp;·&nbsp; Threshold: <b style="color:#e2e8f0;">{threshold:.4f}</b>
      </div>
    </div>
    """

    fig = similarity_bar(sim, threshold)
    status = f"✓ Face 1 ok · Face 2 ok · Similarity computed"
    return fig, status, verdict_html


def update_threshold_label(val):
    return f"Threshold: {val:.3f}"


# ── Tab 3: Identify ───────────────────────────────────────────────────────────

def identify_face(img_path, top_k=5):
    from gui.inference import embed_image

    if img_path is None:
        return "Upload an image first.", ""

    emb, msg = embed_image(img_path)
    if emb is None:
        return msg, ""

    ff = state.fairface()
    gallery_embs = ff["embeddings"]
    gallery_files = ff["filenames"]
    gallery_race  = ff["race"]
    gallery_gender = ff["gender"]

    result = get_identifier().identify(
        emb, gallery_embs,
        gallery_ids=list(range(len(gallery_files))),
        top_k=top_k,
    )

    rows_html = ""
    for rank, (idx, sim) in enumerate(zip(result.top_k_indices, result.top_k_similarities), 1):
        fname  = str(gallery_files[idx]).split("/")[-1]
        race   = str(gallery_race[idx])
        gender = str(gallery_gender[idx])
        bar_w  = int(sim * 100)
        color  = "#4299e1" if rank == 1 else "#718096"
        rows_html += f"""
        <div class="rank-item">
          <div class="rank-badge" style="background:{color};">#{rank}</div>
          <div style="flex:1; min-width:0;">
            <div style="font-size:13px; color:#e2e8f0; font-weight:600;
                        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
              {fname}
            </div>
            <div style="font-size:11px; color:#a0aec0; margin:2px 0 6px 0;">
              {race} · {gender}
            </div>
            <div style="height:6px; background:#2d3748; border-radius:3px; overflow:hidden;">
              <div style="width:{bar_w}%; height:100%;
                          background:{color}; border-radius:3px;"></div>
            </div>
          </div>
          <div style="font-size:14px; font-weight:700; color:{color};
                      margin-left:12px; flex-shrink:0;">
            {sim:.4f}
          </div>
        </div>
        """

    status = f"✓ Gallery: {len(gallery_embs):,} images · Top-{top_k} retrieved"
    return status, rows_html


# ── Tab 4: Fairness Dashboard ─────────────────────────────────────────────────

def load_dashboard():
    report = state.fairness_report()
    audits = report["audits"]
    threshold = report["metadata"]["threshold"]

    # Score distributions from LFW cache
    lfw = state.lfw()
    embs_a = lfw["embeddings"][0::2]
    embs_b = lfw["embeddings"][1::2]
    sims   = np.sum(embs_a * embs_b, axis=1)
    issame = lfw["issame"].astype(bool)
    genuine_scores  = sims[issame]
    impostor_scores = sims[~issame]

    # Per-axis FAR charts
    race_fig   = far_bar_chart(audits["race"]["per_group"],   "Race")
    gender_fig = far_bar_chart(audits["gender"]["per_group"], "Gender")
    age_fig    = far_bar_chart(audits["age"]["per_group"],    "Age")

    # FMRD gauges
    race_fmrd_fig   = fmrd_gauge(audits["race"]["fairness_ratios"]["fmrd"])
    gender_fmrd_fig = fmrd_gauge(audits["gender"]["fairness_ratios"]["fmrd"])
    age_fmrd_fig    = fmrd_gauge(audits["age"]["fairness_ratios"]["fmrd"])

    # Score dist
    dist_fig = score_distribution(genuine_scores, impostor_scores, threshold)

    # Summary HTML
    def verdict_badge(passed):
        return ('<span class="pass-badge">✓ PASS</span>' if passed
                else '<span class="fail-badge">✗ FAIL</span>')

    rows = ""
    for axis, label in [("race", "Race"), ("gender", "Gender"), ("age", "Age")]:
        a     = audits[axis]
        r     = a["fairness_ratios"]
        c     = a["compliance"]
        s     = a["summary"]
        rows += f"""
        <tr>
          <td style="padding:8px 12px; color:#e2e8f0; font-weight:500;">{label}</td>
          <td style="padding:8px 12px; text-align:center; font-weight:700;
                     color:{'#e53e3e' if not c['fmrd_compliant'] else '#2f855a'};">
            {r['fmrd']:.2f}×
          </td>
          <td style="padding:8px 12px; text-align:center;">
            {r['disparate_impact']:.4f}
          </td>
          <td style="padding:8px 12px; text-align:center;">
            {verdict_badge(c['fmrd_compliant'])}
          </td>
          <td style="padding:8px 12px; color:#a0aec0; font-size:12px;">
            {s['best_far_group']} → {s['worst_far_group']}
          </td>
        </tr>
        """

    summary_html = f"""
    <table style="width:100%; border-collapse:collapse;
                  background:#1e2d3d; border-radius:8px; overflow:hidden;">
      <thead>
        <tr style="background:#1a365d;">
          <th style="padding:10px 12px; text-align:left; color:#e2e8f0;
                     font-size:12px; letter-spacing:0.05em;">AXIS</th>
          <th style="padding:10px 12px; text-align:center; color:#e2e8f0;
                     font-size:12px; letter-spacing:0.05em;">FMRD</th>
          <th style="padding:10px 12px; text-align:center; color:#e2e8f0;
                     font-size:12px; letter-spacing:0.05em;">DI</th>
          <th style="padding:10px 12px; text-align:center; color:#e2e8f0;
                     font-size:12px; letter-spacing:0.05em;">VERDICT</th>
          <th style="padding:10px 12px; text-align:left; color:#e2e8f0;
                     font-size:12px; letter-spacing:0.05em;">RANGE</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    """

    return (
        summary_html,
        race_fig, race_fmrd_fig,
        gender_fig, gender_fmrd_fig,
        age_fig, age_fmrd_fig,
        dist_fig,
    )


# ── Tab 5: Identification Metrics + Robustness ───────────────────────────────

def load_id_metrics():
    """Load CMC + robustness data and return chart figures + summary HTML."""
    m = state.id_metrics()
    r = state.robustness_results()

    cmc_fig  = cmc_curve(m["rank_k"], m["n_gallery"], m["n_probes"])
    rob_fig  = robustness_chart(r) if r else go.Figure()

    summary = f"""
    <div style="display:flex; gap:24px; flex-wrap:wrap; margin-bottom:12px;">
      <div class="stat-item">
        <div class="stat-num">{m['rank_1']*100:.2f}%</div>
        <div class="stat-desc">Rank-1 ({m['n_gallery']:,}-gallery)</div>
      </div>
      <div class="stat-item">
        <div class="stat-num">{m['rank_5']*100:.2f}%</div>
        <div class="stat-desc">Rank-5</div>
      </div>
      <div class="stat-item">
        <div class="stat-num">{m['rank_10']*100:.2f}%</div>
        <div class="stat-desc">Rank-10</div>
      </div>
      <div class="stat-item">
        <div class="stat-num">{m['n_probes']:,}</div>
        <div class="stat-desc">Probe images</div>
      </div>
    </div>
    <p style="color:#a0aec0; font-size:12px; max-width:680px; line-height:1.6;">
      Rank-1 of <b style="color:#e2e8f0;">{m['rank_1']*100:.2f}%</b> is expected for 1:N
      identification in a {m['n_gallery']:,}-subject gallery — the same model achieves
      99.70% in 1:1 verification. Rank-10 at
      <b style="color:#68d391;">{m['rank_10']*100:.2f}%</b> confirms embeddings are
      well-separated; gallery size is the primary driver of Rank-1 degradation.
    </p>
    """

    # Robustness summary text
    rob_rows = ""
    if r and "perturbations" in r:
        for name, rows in r["perturbations"].items():
            base  = rows[0]["match_rate"] * 100
            worst = min(row["match_rate"] for row in rows) * 100
            drop  = base - worst
            color = "#e53e3e" if drop > 20 else "#f6ad55" if drop > 5 else "#68d391"
            rob_rows += f"""
            <tr>
              <td style="padding:6px 10px; color:#e2e8f0;">{name}</td>
              <td style="padding:6px 10px; text-align:center; color:#4299e1;">{base:.1f}%</td>
              <td style="padding:6px 10px; text-align:center; color:{color};">{worst:.1f}%</td>
              <td style="padding:6px 10px; text-align:center; color:{color}; font-weight:700;">
                −{drop:.1f} pp</td>
            </tr>"""

    rob_summary = f"""
    <table style="width:100%; border-collapse:collapse; background:#1e2d3d;
                  border-radius:8px; overflow:hidden; margin-top:8px;">
      <thead>
        <tr style="background:#1a365d;">
          <th style="padding:8px 10px; text-align:left; color:#e2e8f0; font-size:11px;">
            PERTURBATION</th>
          <th style="padding:8px 10px; text-align:center; color:#e2e8f0; font-size:11px;">
            BASELINE</th>
          <th style="padding:8px 10px; text-align:center; color:#e2e8f0; font-size:11px;">
            WORST</th>
          <th style="padding:8px 10px; text-align:center; color:#e2e8f0; font-size:11px;">
            DROP</th>
        </tr>
      </thead>
      <tbody>{rob_rows if rob_rows else
        "<tr><td colspan='4' style='padding:12px; color:#a0aec0; text-align:center;'>"
        "Robustness results not yet available — run evaluate_robustness.py</td></tr>"
      }</tbody>
    </table>
    """ if r and "perturbations" in r else (
        "<p style='color:#a0aec0;'>Run scripts/evaluate_robustness.py to see results.</p>"
    )

    return summary, cmc_fig, rob_fig, rob_summary


# ── Tab 6: Ethics Officer Chat ────────────────────────────────────────────────

def _build_chat_context() -> str:
    parts = ["You are the Ethics Officer of ETHOS.\n\n"]
    if state.FAIRNESS_JSON.exists():
        parts.append("FAIRNESS AUDIT:\n" +
                     json.dumps(state.fairness_report(), indent=2))
    if state.ID_METRICS_JSON.exists():
        parts.append("\n\nIDENTIFICATION METRICS:\n" +
                     json.dumps(state.id_metrics(), indent=2))
    if state.ROBUSTNESS_JSON.exists():
        rob = state.robustness_results()
        # Summarise to save context tokens
        rob_summary = {
            name: {
                "baseline_match_rate": rows[0]["match_rate"],
                "worst_match_rate":    min(r["match_rate"] for r in rows),
                "drop_pp":             round((rows[0]["match_rate"] -
                                              min(r["match_rate"] for r in rows)) * 100, 1),
                "severities":          [r["severity"] for r in rows],
            }
            for name, rows in rob.get("perturbations", {}).items()
        }
        parts.append("\n\nROBUSTNESS RESULTS:\n" + json.dumps(rob_summary, indent=2))
    parts.append(
        "\n\nAnswer questions about bias, EU AI Act compliance, "
        "identification accuracy, or robustness. Be precise and cite numbers."
    )
    return "".join(parts)


_chat_context = _build_chat_context()


def chat_respond(message, history):
    if not message.strip():
        return history, ""

    officer = get_officer()
    # Build messages list from history
    messages = []
    for user_msg, bot_msg in history:
        messages.append({"role": "user",    "content": user_msg})
        messages.append({"role": "assistant","content": bot_msg})
    messages.append({"role": "user", "content": message})

    import anthropic
    from dotenv import load_dotenv
    import os
    load_dotenv(ROOT / ".env")

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system=_chat_context,
        messages=messages,
    )
    reply = response.content[0].text
    history = history + [(message, reply)]
    return history, ""


# ── Tab 6: Live Assessment ───────────────────────────────────────────────────

def process_live_frame(frame_rgb: np.ndarray | None):
    """
    Per-frame callback for the webcam stream.

    Gradio passes frames as RGB numpy arrays (H, W, 3).
    Returns: (annotated_rgb, fps_html, score_html, verdict_html)
    """
    global _fps_times

    if frame_rgb is None:
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        return blank, _fps_html(0), _score_html(0.0), _verdict_html(None)

    t_frame = time.perf_counter()
    bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

    from gui.inference import _model as _insightface_model
    app_if = _insightface_model()
    faces  = app_if.get(bgr)

    pad_result = None
    for face in faces:
        bbox = face.bbox.astype(int)   # [x1, y1, x2, y2]
        pad_result = get_pad().score(bgr, bbox)

        # Pick colour based on confidence level
        c = pad_result.color_bgr
        color = (int(c[0]), int(c[1]), int(c[2]))

        # Bounding box
        cv2.rectangle(bgr, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)

        # Label above box
        label = f"{pad_result.attack_label}  {pad_result.real_score:.2f}"
        lx, ly = bbox[0], max(bbox[1] - 10, 0)
        cv2.putText(bgr, label, (lx, ly),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)

    # Rolling FPS over last 30 frames
    _fps_times.append(t_frame)
    _fps_times = [t for t in _fps_times if t_frame - t <= 2.0]  # last 2s
    fps = max(1, len(_fps_times) - 1) / max(t_frame - _fps_times[0], 1e-6) if len(_fps_times) > 1 else 0

    annotated_rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return (
        annotated_rgb,
        _fps_html(fps, pad_result.inference_ms if pad_result else 0),
        _score_html(pad_result.real_score if pad_result else 0.0),
        _verdict_html(pad_result),
    )


def _fps_html(fps: float, inf_ms: float = 0) -> str:
    color = "#68d391" if fps >= 10 else "#fc8181"
    return (
        f'<div style="font-family:monospace; font-size:14px; color:{color}; '
        f'padding:4px 8px; background:#1a2233; border-radius:4px; display:inline-block;">'
        f'FPS: <b>{fps:.1f}</b>&nbsp;&nbsp;Inference: <b>{inf_ms:.1f} ms</b>'
        f'</div>'
    )


def _score_html(real_score: float) -> str:
    pct  = int(real_score * 100)
    if real_score >= 0.75:
        bar_color = "#68d391"
        label = "Real Face"
    elif real_score >= 0.45:
        bar_color = "#f6ad55"
        label = "Uncertain"
    else:
        bar_color = "#fc8181"
        label = "Spoof"
    return f"""
    <div style="padding:8px; background:#1a2233; border-radius:6px;">
      <div style="font-size:12px; color:#a0aec0; margin-bottom:4px;">
        PAD Score — <b style="color:#e2e8f0;">{label}</b>
        &nbsp;<span style="color:{bar_color}; font-weight:700;">{real_score:.3f}</span>
      </div>
      <div style="height:14px; background:#2d3748; border-radius:7px; overflow:hidden;">
        <div style="width:{pct}%; height:100%;
                    background:{bar_color}; border-radius:7px;
                    transition:width 0.15s ease;"></div>
      </div>
    </div>"""


def _verdict_html(result) -> str:
    if result is None:
        return '<div style="font-size:20px; color:#a0aec0; padding:8px;">No face detected</div>'
    if result.is_real:
        return (
            '<div style="font-size:22px; font-weight:700; color:#68d391; padding:8px;">'
            '✅ Real Face</div>'
        )
    return (
        f'<div style="font-size:22px; font-weight:700; color:#fc8181; padding:8px;">'
        f'❌ Spoof — {result.attack_label}</div>'
    )


# ── Tab 7: Generate Report ────────────────────────────────────────────────────

def generate_pdf_report(progress=gr.Progress()):
    progress(0.10, desc="Calling Ethics Officer — analysis…")
    officer = get_officer()
    report  = state.fairness_report()

    analysis = officer.analyze_fairness_report(report)

    progress(0.55, desc="Generating compliance summary…")
    summary = officer.generate_compliance_summary(report)

    progress(0.80, desc="Building PDF…")
    from src.reports.compliance_pdf import ComplianceReportGenerator
    gen = ComplianceReportGenerator(plots_dir=str(state.PLOTS_DIR))
    ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"ethos_compliance_audit_{ts}.pdf"
    pdf_path = str(state.REPORTS_DIR / fname)
    gen.generate(report, analysis, summary, pdf_path)

    progress(1.0, desc="Done.")
    size_kb = Path(pdf_path).stat().st_size // 1024

    # Inline viewer — Gradio serves the file via /file= endpoint
    viewer_html = f"""
    <div style="margin-top:12px;">
      <p style="color:#a0aec0; font-size:12px; margin-bottom:8px;">
        ✓ <b style="color:#e2e8f0;">{fname}</b> ({size_kb} KB)
        — scroll below to read · use the download button above to save
      </p>
      <iframe
        src="/file={pdf_path}"
        width="100%" height="860px"
        style="border:1px solid #2d3748; border-radius:8px; background:#fff;"
      ></iframe>
    </div>
    """
    return pdf_path, f"✓ {size_kb} KB — ready", viewer_html


# ── Build UI ──────────────────────────────────────────────────────────────────

def build_app() -> gr.Blocks:
    with gr.Blocks(
        title="ETHOS — Fairness Auditor",
    ) as app:

        # ── Tab 1: Landing ────────────────────────────────────────────────────
        with gr.Tab("🏠  Overview"):
            gr.HTML(LANDING_HTML)

        # ── Tab 2: Verify ─────────────────────────────────────────────────────
        with gr.Tab("🔍  Verify  1:1"):
            gr.Markdown("### Face Verification — 1:1")
            gr.Markdown(
                "Upload two face photos. The system decides whether they show the same person.",
                elem_classes=["hero-sub"],
            )
            with gr.Row():
                img_a = gr.Image(label="Face A", type="filepath", height=220)
                img_b = gr.Image(label="Face B", type="filepath", height=220)

            threshold_slider = gr.Slider(
                minimum=0.05, maximum=0.95, value=DEFAULT_THRESHOLD, step=0.005,
                label=f"Decision threshold  (EER-optimal = {DEFAULT_THRESHOLD})",
            )
            verify_btn = gr.Button("Verify", variant="primary")

            verify_status  = gr.Markdown(value="", elem_classes=["status-ok"])
            verify_verdict = gr.HTML()
            sim_plot       = gr.Plot(label="Similarity vs Threshold")

            verify_btn.click(
                fn=verify_faces,
                inputs=[img_a, img_b, threshold_slider],
                outputs=[sim_plot, verify_status, verify_verdict],
            )
            threshold_slider.release(
                fn=verify_faces,
                inputs=[img_a, img_b, threshold_slider],
                outputs=[sim_plot, verify_status, verify_verdict],
            )

        # ── Tab 3: Identify ───────────────────────────────────────────────────
        with gr.Tab("🔎  Identify  1:N"):
            gr.Markdown("### Face Identification — 1:N")
            gr.Markdown(
                "Upload a face photo. The system searches the FairFace gallery "
                "(86,486 images) and returns the 5 most similar entries.",
                elem_classes=["hero-sub"],
            )
            with gr.Row():
                with gr.Column(scale=1):
                    query_img  = gr.Image(label="Query Face", type="filepath", height=240)
                    id_btn     = gr.Button("Identify", variant="primary")
                    id_status  = gr.Markdown("", elem_classes=["status-ok"])
                with gr.Column(scale=2):
                    id_results = gr.HTML(label="Top-5 Matches")

            id_btn.click(
                fn=identify_face,
                inputs=[query_img],
                outputs=[id_status, id_results],
            )

        # ── Tab 4: Fairness Dashboard ─────────────────────────────────────────
        with gr.Tab("📊  Fairness Dashboard"):
            gr.Markdown("### Fairness Audit Results")
            gr.Markdown(
                "Per-demographic False Acceptance Rates measured on FairFace "
                "(86k images). Threshold = 0.1810 (EER-optimal from LFW).",
                elem_classes=["hero-sub"],
            )
            dash_btn     = gr.Button("Load Dashboard", variant="primary")
            summary_html = gr.HTML()

            gr.Markdown("#### Score Distributions (LFW genuine vs impostor)")
            dist_fig = gr.Plot()

            with gr.Tabs():
                with gr.Tab("Race"):
                    with gr.Row():
                        race_bar_fig  = gr.Plot()
                        race_fmrd_fig = gr.Plot()

                with gr.Tab("Gender"):
                    with gr.Row():
                        gender_bar_fig  = gr.Plot()
                        gender_fmrd_fig = gr.Plot()

                with gr.Tab("Age"):
                    with gr.Row():
                        age_bar_fig  = gr.Plot()
                        age_fmrd_fig = gr.Plot()

            dash_btn.click(
                fn=load_dashboard,
                inputs=[],
                outputs=[
                    summary_html,
                    race_bar_fig,   race_fmrd_fig,
                    gender_bar_fig, gender_fmrd_fig,
                    age_bar_fig,    age_fmrd_fig,
                    dist_fig,
                ],
            )

        # ── Tab 5: Identification Metrics + Robustness ───────────────────────
        with gr.Tab("📈  Identification + Robustness"):
            gr.Markdown("### 1:N Identification Metrics & Robustness")
            gr.Markdown(
                "CMC curve on a 3,000-subject LFW gallery. "
                "Robustness shows match-rate drop under blur, brightness shift, "
                "rotation, downsampling, and Gaussian noise.",
                elem_classes=["hero-sub"],
            )
            metrics_btn     = gr.Button("Load Results", variant="primary")
            id_summary_html = gr.HTML()
            with gr.Row():
                cmc_plot_fig = gr.Plot(label="CMC Curve")
                rob_plot_fig = gr.Plot(label="Robustness Degradation")
            rob_table_html  = gr.HTML()

            metrics_btn.click(
                fn=load_id_metrics,
                inputs=[],
                outputs=[id_summary_html, cmc_plot_fig, rob_plot_fig, rob_table_html],
            )

        # ── Tab 6: Ethics Officer Chat ────────────────────────────────────────
        with gr.Tab("💬  Ethics Officer"):
            gr.Markdown("### Ethics Officer")
            gr.Markdown(
                "Ask the AI Ethics Officer anything about the system's bias findings, "
                "EU AI Act compliance status, or mitigation strategies.",
                elem_classes=["hero-sub"],
            )
            chatbot  = gr.Chatbot(height=440)
            with gr.Row():
                chat_input = gr.Textbox(
                    placeholder="e.g. Why does the system fail on Southeast Asian faces?",
                    show_label=False, scale=5,
                )
                chat_send = gr.Button("Send", variant="primary", scale=1)

            starters = [
                "Summarise the race bias findings in plain English.",
                "Is this system deployable in the EU under the AI Act?",
                "Why is the age FMRD so much worse than race FMRD?",
                "What are the top 3 mitigations before deployment?",
            ]
            gr.Examples(examples=starters, inputs=chat_input, label="Quick questions")

            chat_send.click(
                fn=chat_respond,
                inputs=[chat_input, chatbot],
                outputs=[chatbot, chat_input],
            )
            chat_input.submit(
                fn=chat_respond,
                inputs=[chat_input, chatbot],
                outputs=[chatbot, chat_input],
            )

        # ── Tab 7: Live Assessment ────────────────────────────────────────────
        with gr.Tab("🛡️  Live Assessment"):
            gr.Markdown("### Live Liveness Assessment")
            gr.Markdown(
                "Real-time Presentation Attack Detection via webcam. "
                "RetinaFace detects the face, MiniFASNetV2 runs PAD, "
                "ArcFace embeds only if PAD passes. Target: ≥10 FPS on M4.",
                elem_classes=["hero-sub"],
            )
            with gr.Row():
                with gr.Column(scale=1):
                    webcam_in  = gr.Image(
                        sources=["webcam"], streaming=True,
                        label="Webcam Feed", type="numpy", height=360,
                    )
                with gr.Column(scale=1):
                    live_out   = gr.Image(label="Annotated Output", type="numpy", height=360)

            fps_display     = gr.HTML(_fps_html(0))
            pad_score_disp  = gr.HTML(_score_html(0.0))
            verdict_disp    = gr.HTML(_verdict_html(None))

            webcam_in.stream(
                fn=process_live_frame,
                inputs=[webcam_in],
                outputs=[live_out, fps_display, pad_score_disp, verdict_disp],
                stream_every=0.04,   # ~25 FPS target
                time_limit=300,
            )

        # ── Tab 8: Generate Report ────────────────────────────────────────────
        with gr.Tab("📄  Generate Report"):
            gr.Markdown("### EU AI Act Compliance Report")
            gr.Markdown(
                "Generates a full 9-page PDF compliance audit document. "
                "Calls the Ethics Officer API, embeds fairness charts, and "
                "formats to NIST/ISO regulator standards.",
                elem_classes=["hero-sub"],
            )
            with gr.Row():
                gen_btn    = gr.Button("Generate PDF Report", variant="primary", scale=2)
            gen_status = gr.Markdown("")
            pdf_output = gr.File(label="Download Report", visible=True)
            pdf_viewer = gr.HTML()

            gen_btn.click(
                fn=generate_pdf_report,
                inputs=[],
                outputs=[pdf_output, gen_status, pdf_viewer],
            )

    return app


# ── Entry point ───────────────────────────────────────────────────────────────

def _preload_background():
    """
    Warm up slow resources in a background thread so the first user click
    is instant instead of hanging for 20-30 seconds.
    """
    import threading

    def _load():
        print("  [preload] Loading InsightFace model…")
        t = time.time()
        from gui.inference import _model
        _model()
        print(f"  [preload] InsightFace ready  ({(time.time()-t):.1f}s)")

        print("  [preload] Loading FairFace embeddings cache…")
        t = time.time()
        _ = state.fairface()
        print(f"  [preload] FairFace ready  ({len(state.fairface()['embeddings']):,} embs, {(time.time()-t):.1f}s)")

        print("  [preload] Loading PAD model…")
        t = time.time()
        get_pad()
        print(f"  [preload] PAD ready  ({(time.time()-t):.2f}s)")

        print("  [preload] All resources warm ✓")

    threading.Thread(target=_load, daemon=True).start()


if __name__ == "__main__":
    t0 = time.time()
    print("Starting ETHOS GUI…")
    app = build_app()
    print(f"App built in {(time.time()-t0)*1000:.0f} ms")
    _preload_background()   # start warming model + cache in background
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        theme=ethos_theme(),
        css=CUSTOM_CSS,
        allowed_paths=[str(state.REPORTS_DIR)],
    )
