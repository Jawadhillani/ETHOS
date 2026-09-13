"""
ETHOS — Ethical Trust & Holistic Oversight System
Gradio GUI  |  Premium dark dashboard redesign

Run:
    /opt/miniconda3/envs/ethos/bin/python3 gui/app.py
"""

import json
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

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
import app.state as state

from src.matching.engine import MatchingEngine
from src.matching.verifier import Verifier
from src.matching.identifier import Identifier
from src.llm.ethics_officer import EthicsOfficer
from src.security.pad_detector import PADDetector

DEFAULT_THRESHOLD = 0.1810

_fps_times: list = []


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


# ── UI helpers ────────────────────────────────────────────────────────────────

def _section(title: str, subtitle: str = "") -> str:
    sub = f'<p class="section-sub">{subtitle}</p>' if subtitle else ""
    return f'<div class="section-header"><h2 class="section-title">{title}</h2>{sub}</div>'


# ── Sticky nav ────────────────────────────────────────────────────────────────
# In Gradio 6, <script> inside gr.HTML is injected via innerHTML and does NOT
# execute. Use head= (injected into <head>, executes) and js_on_load= instead.

NAV_HEAD = """\
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap">
"""

NAV_JS = """\
window._ethosShowPage = function(idx) {
    document.querySelectorAll('.ethos-page').forEach(function(el, i) {
        el.classList.toggle('ethos-page-active', i === idx);
    });
};

window.ethosNav = function(idx) {
    document.querySelectorAll('.e-nav-item').forEach(function(b, i) {
        b.classList.toggle('e-active', i === idx);
    });
    window._ethosShowPage(idx);
};

element.querySelectorAll('.e-nav-item').forEach(function(btn, i) {
    btn.addEventListener('click', function() { window.ethosNav(i); });
});

(function _initPages() {
    var pages = document.querySelectorAll('.ethos-page');
    if (pages.length >= 8) { window._ethosShowPage(0); }
    else { setTimeout(_initPages, 120); }
})();
"""

NAV_HTML = """\
<div class="ethos-header" id="ethos-header">
  <div class="ethos-brand">
    <span class="ethos-logo-icon">◈</span>
    <span class="ethos-logo-text">ETHOS</span>
  </div>
  <nav class="ethos-nav">
    <button class="e-nav-item e-active">Overview</button>
    <button class="e-nav-item">Verify 1:1</button>
    <button class="e-nav-item">Identify 1:N</button>
    <button class="e-nav-item">Fairness</button>
    <button class="e-nav-item">Metrics</button>
    <button class="e-nav-item">Ethics Chat</button>
    <button class="e-nav-item">Live PAD</button>
    <button class="e-nav-item">Report</button>
  </nav>
  <span class="ethos-act-badge">EU AI Act</span>
</div>
"""

# ── Tab 1: Landing ────────────────────────────────────────────────────────────

LANDING_HTML = """
<div class="hero-section">

  <div class="hero-badge">
    <span class="badge-dot"></span>
    Master's Thesis &nbsp;·&nbsp; UPEC Spring 2026
  </div>

  <div class="hero-name">ETHOS</div>
  <div class="hero-tagline">Ethical Trust &amp; Holistic Oversight System</div>

  <p class="hero-desc">
    A facial biometric fairness auditor built for EU AI Act compliance.<br>
    Measures recognition accuracy across race, gender, and age —<br>
    then generates a regulator-ready compliance report.
  </p>

  <div class="metric-grid">
    <div class="metric-card neutral">
      <div class="metric-num cyan">99.70%</div>
      <div class="metric-label">LFW Accuracy</div>
    </div>
    <div class="metric-card neutral">
      <div class="metric-num cyan">0.30%</div>
      <div class="metric-label">Equal Error Rate</div>
    </div>
    <div class="metric-card neutral">
      <div class="metric-num cyan">0.9994</div>
      <div class="metric-label">AUC — LFW</div>
    </div>
    <div class="metric-card neutral">
      <div class="metric-num cyan">0.1810</div>
      <div class="metric-label">EER Threshold</div>
    </div>
    <div class="metric-card neutral">
      <div class="metric-num cyan">86 k</div>
      <div class="metric-label">FairFace Images</div>
    </div>
  </div>

  <div class="metric-grid" style="margin-top:10px;">
    <div class="metric-card fail">
      <div class="metric-num red">9.19×</div>
      <div class="metric-label">Race FMRD · FAIL</div>
    </div>
    <div class="metric-card pass">
      <div class="metric-num green">1.37×</div>
      <div class="metric-label">Gender FMRD · PASS</div>
    </div>
    <div class="metric-card fail">
      <div class="metric-num red">42.30×</div>
      <div class="metric-label">Age FMRD · FAIL</div>
    </div>
    <div class="metric-card neutral">
      <div class="metric-num cyan">47.87%</div>
      <div class="metric-label">Rank-1 · 3 k gallery</div>
    </div>
    <div class="metric-card neutral">
      <div class="metric-num cyan">299 FPS</div>
      <div class="metric-label">PAD · Apple M4</div>
    </div>
  </div>

  <hr class="ethos-divider"/>

  <div class="stack-chips">
    <span class="stack-chip">InsightFace buffalo_l</span>
    <span class="stack-chip">ArcFace</span>
    <span class="stack-chip">RetinaFace</span>
    <span class="stack-chip">CoreML · Apple M4</span>
    <span class="stack-chip">MiniFASNetV2</span>
    <span class="stack-chip">FairFace 86 k</span>
    <span class="stack-chip">LFW 12 k</span>
    <span class="stack-chip">Claude Sonnet</span>
    <span class="stack-chip">EU AI Act Art. 10 / 13 / 15</span>
    <span class="stack-chip">Gradio · Plotly · ReportLab</span>
  </div>

</div>
"""


# ── Tab 2: Verify ─────────────────────────────────────────────────────────────

def verify_faces(img_a_path, img_b_path, threshold):
    from app.inference import embed_image

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
    <div class="{'verdict-match' if match else 'verdict-nomatch'}">
      <div class="verdict-icon">{'✅' if match else '❌'}</div>
      <div class="verdict-text" style="color:{'var(--success)' if match else 'var(--danger)'};">
        {'MATCH' if match else 'NO MATCH'}
      </div>
      <div class="verdict-sim">
        Similarity&nbsp;<b style="color:var(--text-pri);">{sim:.4f}</b>
        &nbsp;·&nbsp;
        Threshold&nbsp;<b style="color:var(--text-pri);">{threshold:.4f}</b>
      </div>
    </div>
    """

    fig    = similarity_bar(sim, threshold)
    status = "✓ Both faces embedded · similarity computed"
    return fig, status, verdict_html


# ── Tab 3: Identify ───────────────────────────────────────────────────────────

def identify_face(img_path, top_k=5):
    from app.inference import embed_image

    if img_path is None:
        return "Upload an image first.", ""

    emb, msg = embed_image(img_path)
    if emb is None:
        return msg, ""

    ff             = state.fairface()
    gallery_embs   = ff["embeddings"]
    gallery_files  = ff["filenames"]
    gallery_race   = ff["race"]
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
        color  = "var(--accent)" if rank == 1 else "var(--text-sec)"
        bg     = "rgba(0,212,255,0.12)" if rank == 1 else "rgba(255,255,255,0.06)"
        rows_html += f"""
        <div class="rank-item">
          <div class="rank-badge" style="background:{bg}; color:{color};">#{rank}</div>
          <div style="flex:1; min-width:0;">
            <div style="font-size:13px; color:var(--text-pri); font-weight:600;
                        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
              {fname}
            </div>
            <div style="font-size:11px; color:var(--text-muted); margin:2px 0 6px 0;">
              {race} &nbsp;·&nbsp; {gender}
            </div>
            <div style="height:4px; background:rgba(255,255,255,0.06); border-radius:2px; overflow:hidden;">
              <div style="width:{bar_w}%; height:100%;
                          background:{color}; border-radius:2px;
                          transition:width 0.3s ease;"></div>
            </div>
          </div>
          <div style="font-size:15px; font-weight:800; color:{color};
                      margin-left:12px; flex-shrink:0; font-variant-numeric:tabular-nums;">
            {sim:.4f}
          </div>
        </div>
        """

    status = f"✓ Gallery: {len(gallery_embs):,} images &nbsp;·&nbsp; Top-{top_k} retrieved"
    return status, rows_html


# ── Tab 4: Fairness Dashboard ─────────────────────────────────────────────────

def load_dashboard():
    report    = state.fairness_report()
    audits    = report["audits"]
    threshold = report["metadata"]["threshold"]

    lfw  = state.lfw()
    embs_a = lfw["embeddings"][0::2]
    embs_b = lfw["embeddings"][1::2]
    sims   = np.sum(embs_a * embs_b, axis=1)
    issame = lfw["issame"].astype(bool)
    genuine_scores  = sims[issame]
    impostor_scores = sims[~issame]

    race_fig   = far_bar_chart(audits["race"]["per_group"],   "Race")
    gender_fig = far_bar_chart(audits["gender"]["per_group"], "Gender")
    age_fig    = far_bar_chart(audits["age"]["per_group"],    "Age")

    race_fmrd_fig   = fmrd_gauge(audits["race"]["fairness_ratios"]["fmrd"])
    gender_fmrd_fig = fmrd_gauge(audits["gender"]["fairness_ratios"]["fmrd"])
    age_fmrd_fig    = fmrd_gauge(audits["age"]["fairness_ratios"]["fmrd"])

    dist_fig = score_distribution(genuine_scores, impostor_scores, threshold)

    def verdict_badge(passed: bool) -> str:
        if passed:
            return '<span class="pass-badge">✓ PASS</span>'
        return '<span class="fail-badge">✗ FAIL</span>'

    rows = ""
    for axis, label in [("race", "Race"), ("gender", "Gender"), ("age", "Age")]:
        a = audits[axis]
        r = a["fairness_ratios"]
        c = a["compliance"]
        s = a["summary"]
        fmrd_color = "var(--danger)" if not c["fmrd_compliant"] else "var(--success)"
        rows += f"""
        <tr>
          <td style="font-weight:600;">{label}</td>
          <td style="text-align:center; font-weight:800; color:{fmrd_color};">{r['fmrd']:.2f}×</td>
          <td style="text-align:center;">{r['disparate_impact']:.4f}</td>
          <td style="text-align:center;">{verdict_badge(c['fmrd_compliant'])}</td>
          <td style="color:var(--text-sec); font-size:12px;">
            {s['best_far_group']} → {s['worst_far_group']}
          </td>
        </tr>
        """

    summary_html = f"""
    <table class="compliance-table">
      <thead>
        <tr>
          <th>Axis</th><th style="text-align:center;">FMRD</th>
          <th style="text-align:center;">DI</th><th style="text-align:center;">Verdict</th>
          <th>Range (best → worst)</th>
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


# ── Tab 5: Identification Metrics + Robustness ────────────────────────────────

def load_id_metrics():
    m = state.id_metrics()
    r = state.robustness_results()

    cmc_fig = cmc_curve(m["rank_k"], m["n_gallery"], m["n_probes"])
    rob_fig = robustness_chart(r) if r else go.Figure()

    summary = f"""
    <div class="metric-grid" style="grid-template-columns:repeat(4,1fr); margin-bottom:16px;">
      <div class="metric-card neutral">
        <div class="metric-num cyan">{m['rank_1']*100:.2f}%</div>
        <div class="metric-label">Rank-1 ({m['n_gallery']:,}-gallery)</div>
      </div>
      <div class="metric-card neutral">
        <div class="metric-num cyan">{m['rank_5']*100:.2f}%</div>
        <div class="metric-label">Rank-5</div>
      </div>
      <div class="metric-card neutral">
        <div class="metric-num cyan">{m['rank_10']*100:.2f}%</div>
        <div class="metric-label">Rank-10</div>
      </div>
      <div class="metric-card neutral">
        <div class="metric-num cyan">{m['n_probes']:,}</div>
        <div class="metric-label">Probe images</div>
      </div>
    </div>
    <p style="color:var(--text-sec); font-size:13px; max-width:680px; line-height:1.6; margin:0 0 8px 0;">
      Rank-1 of <b style="color:var(--text-pri);">{m['rank_1']*100:.2f}%</b> is expected
      for 1:N identification in a {m['n_gallery']:,}-subject gallery — the same model achieves
      99.70% in 1:1 verification. Rank-10 at
      <b style="color:var(--success);">{m['rank_10']*100:.2f}%</b> confirms embeddings are
      well-separated; gallery size is the primary driver of Rank-1 degradation.
    </p>
    """

    rob_rows = ""
    if r and "perturbations" in r:
        for name, rows in r["perturbations"].items():
            base  = rows[0]["match_rate"] * 100
            worst = min(row["match_rate"] for row in rows) * 100
            drop  = base - worst
            color = "var(--danger)" if drop > 20 else "var(--warning)" if drop > 5 else "var(--success)"
            rob_rows += f"""
            <tr>
              <td>{name}</td>
              <td style="text-align:center; color:var(--accent);">{base:.1f}%</td>
              <td style="text-align:center; color:{color};">{worst:.1f}%</td>
              <td style="text-align:center; color:{color}; font-weight:700;">−{drop:.1f} pp</td>
            </tr>"""

    if rob_rows:
        rob_summary = f"""
        <table class="compliance-table" style="margin-top:8px;">
          <thead>
            <tr>
              <th>Perturbation</th><th style="text-align:center;">Baseline</th>
              <th style="text-align:center;">Worst</th><th style="text-align:center;">Drop</th>
            </tr>
          </thead>
          <tbody>{rob_rows}</tbody>
        </table>"""
    else:
        rob_summary = (
            "<p style='color:var(--text-sec); font-size:13px; margin-top:8px;'>"
            "Run <code>scripts/evaluate_robustness.py</code> to populate this table.</p>"
        )

    return summary, cmc_fig, rob_fig, rob_summary


# ── Tab 6: Ethics Officer Chat ────────────────────────────────────────────────

def _build_chat_context() -> str:
    parts = ["You are the Ethics Officer of ETHOS.\n\n"]
    if state.FAIRNESS_JSON.exists():
        parts.append("FAIRNESS AUDIT:\n" + json.dumps(state.fairness_report(), indent=2))
    if state.ID_METRICS_JSON.exists():
        parts.append("\n\nIDENTIFICATION METRICS:\n" + json.dumps(state.id_metrics(), indent=2))
    if state.ROBUSTNESS_JSON.exists():
        rob = state.robustness_results()
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

    # Gradio 6 uses messages format: [{"role": "user"|"assistant", "content": "..."}]
    api_messages = []
    for msg in (history or []):
        api_messages.append({"role": msg["role"], "content": msg["content"]})
    api_messages.append({"role": "user", "content": message})

    import anthropic
    from dotenv import load_dotenv
    import os
    load_dotenv(ROOT / ".env")

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system=_chat_context,
        messages=api_messages,
    )
    reply = response.content[0].text
    new_history = list(history or [])
    new_history.append({"role": "user",      "content": message})
    new_history.append({"role": "assistant", "content": reply})
    return new_history, ""


# ── Tab 7: Live Assessment ────────────────────────────────────────────────────

def process_live_frame(frame_rgb: np.ndarray | None):
    global _fps_times

    if frame_rgb is None:
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        return blank, _fps_html(0), _score_html(0.0), _verdict_html(None)

    t_frame = time.perf_counter()
    bgr     = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

    from app.inference import _model as _insightface_model
    app_if = _insightface_model()
    faces  = app_if.get(bgr)

    pad_result = None
    for face in faces:
        bbox       = face.bbox.astype(int)
        pad_result = get_pad().score(bgr, bbox)
        c          = pad_result.color_bgr
        color      = (int(c[0]), int(c[1]), int(c[2]))
        cv2.rectangle(bgr, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
        label = f"{pad_result.attack_label}  {pad_result.real_score:.2f}"
        lx, ly = bbox[0], max(bbox[1] - 10, 0)
        cv2.putText(bgr, label, (lx, ly),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)

    _fps_times.append(t_frame)
    _fps_times = [t for t in _fps_times if t_frame - t <= 2.0]
    fps = (
        max(1, len(_fps_times) - 1) / max(t_frame - _fps_times[0], 1e-6)
        if len(_fps_times) > 1 else 0
    )

    annotated_rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return (
        annotated_rgb,
        _fps_html(fps, pad_result.inference_ms if pad_result else 0),
        _score_html(pad_result.real_score if pad_result else 0.0),
        _verdict_html(pad_result),
    )


def _fps_html(fps: float, inf_ms: float = 0) -> str:
    color = "var(--success)" if fps >= 10 else "var(--danger)"
    return (
        f'<div style="font-family:monospace; font-size:14px; color:{color}; '
        f'display:inline-flex; align-items:center; gap:16px; '
        f'padding:7px 16px; background:var(--bg-card); '
        f'border:1px solid var(--border); border-radius:20px;">'
        f'<span>FPS <b style="color:{color};">{fps:.1f}</b></span>'
        f'<span style="color:var(--text-muted);">|</span>'
        f'<span style="color:var(--text-sec);">Inference <b style="color:var(--text-pri);">{inf_ms:.1f}ms</b></span>'
        f'</div>'
    )


def _score_html(real_score: float) -> str:
    pct = int(real_score * 100)
    if real_score >= 0.75:
        bar_color = "var(--success)"; label = "Real Face"
    elif real_score >= 0.45:
        bar_color = "var(--warning)"; label = "Uncertain"
    else:
        bar_color = "var(--danger)"; label = "Spoof"
    return f"""
    <div style="padding:12px 16px; background:var(--bg-card);
                border:1px solid var(--border); border-radius:var(--radius-sm);">
      <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
        <span style="font-size:12px; color:var(--text-sec); font-weight:600; text-transform:uppercase;
                     letter-spacing:0.06em;">PAD Score</span>
        <span style="font-size:13px; font-weight:700; color:{bar_color};">
          {label} &nbsp; {real_score:.3f}
        </span>
      </div>
      <div style="height:6px; background:rgba(255,255,255,0.06); border-radius:3px; overflow:hidden;">
        <div style="width:{pct}%; height:100%; background:{bar_color}; border-radius:3px;
                    transition:width 0.15s ease;"></div>
      </div>
    </div>"""


def _verdict_html(result) -> str:
    if result is None:
        return (
            '<div style="font-size:18px; color:var(--text-muted); '
            'padding:16px; text-align:center;">No face detected</div>'
        )
    if result.is_real:
        return (
            '<div style="font-size:22px; font-weight:800; color:var(--success); '
            'padding:16px; text-align:center; background:rgba(16,185,129,0.08); '
            'border:1px solid rgba(16,185,129,0.2); border-radius:var(--radius-sm);">'
            '✅ &nbsp; Real Face</div>'
        )
    return (
        f'<div style="font-size:22px; font-weight:800; color:var(--danger); '
        f'padding:16px; text-align:center; background:rgba(239,68,68,0.08); '
        f'border:1px solid rgba(239,68,68,0.2); border-radius:var(--radius-sm);">'
        f'❌ &nbsp; Spoof — {result.attack_label}</div>'
    )


# ── Tab 8: Generate Report ────────────────────────────────────────────────────

def generate_pdf_report(progress=gr.Progress()):
    progress(0.10, desc="Ethics Officer — analysing fairness report…")
    officer = get_officer()
    report  = state.fairness_report()
    analysis = officer.analyze_fairness_report(report)

    progress(0.55, desc="Generating compliance summary…")
    summary = officer.generate_compliance_summary(report)

    progress(0.80, desc="Building PDF…")
    from src.reports.compliance_pdf import ComplianceReportGenerator
    gen   = ComplianceReportGenerator(plots_dir=str(state.PLOTS_DIR))
    ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"ethos_compliance_audit_{ts}.pdf"
    
    # Resolve to canonical absolute paths to handle macOS symlinks
    resolved_dir = Path(state.REPORTS_DIR).resolve()
    pdf_path = str(resolved_dir / fname)
    gen.generate(report, analysis, summary, pdf_path)

    progress(1.0, desc="Done.")
    size_kb = Path(pdf_path).stat().st_size // 1024

    import urllib.parse
    encoded_path = urllib.parse.quote(pdf_path)

    viewer_html = f"""
    <div style="margin-top:16px;">
      <p style="color:var(--text-sec); font-size:13px; margin-bottom:12px;">
        ✓ &nbsp;<b style="color:var(--text-pri);">{fname}</b>
        &nbsp;({size_kb} KB) — scroll below to read
      </p>
      <iframe
        src="/file={encoded_path}"
        width="100%" height="860px"
        style="border:1px solid var(--border); border-radius:var(--radius); background:#fff;"
      ></iframe>
    </div>
    """
    return pdf_path, f"✓ {size_kb} KB — ready", viewer_html


# ── Build UI ──────────────────────────────────────────────────────────────────

def build_app() -> gr.Blocks:
    with gr.Blocks(title="ETHOS — Fairness Auditor") as app:

        gr.HTML(NAV_HTML, head=NAV_HEAD, js_on_load=NAV_JS)

        # All pages rendered in DOM (visible=True).
        # CSS class .ethos-page hides them; .ethos-page-active shows one at a time.
        # JS in NAV_HTML toggles these classes — no Gradio event system involved.

        # ── Page 0: Overview ──────────────────────────────────────────────────
        with gr.Column(elem_classes=["ethos-page", "ethos-page-active"]) as page_0:
            gr.HTML(LANDING_HTML)

        # ── Page 1: Verify ────────────────────────────────────────────────────
        with gr.Column(elem_classes=["ethos-page"]) as page_1:
            gr.HTML(_section(
                "Face Verification — 1:1",
                "Upload two face photos. The system decides whether they show the same person.",
            ))
            with gr.Row():
                img_a = gr.Image(label="Face A", type="filepath", height=240)
                img_b = gr.Image(label="Face B", type="filepath", height=240)

            threshold_slider = gr.Slider(
                minimum=0.05, maximum=0.95,
                value=DEFAULT_THRESHOLD, step=0.005,
                label=f"Decision threshold  (EER-optimal = {DEFAULT_THRESHOLD})",
            )
            verify_btn     = gr.Button("Verify", variant="primary")
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

        # ── Page 2: Identify ──────────────────────────────────────────────────
        with gr.Column(elem_classes=["ethos-page"]) as page_2:
            gr.HTML(_section(
                "Face Identification — 1:N",
                "Upload a face photo. The system searches the FairFace gallery "
                "(86,486 images) and returns the 5 most similar entries.",
            ))
            with gr.Row():
                with gr.Column(scale=1):
                    query_img = gr.Image(label="Query Face", type="filepath", height=260)
                    id_btn    = gr.Button("Identify", variant="primary")
                    id_status = gr.Markdown("", elem_classes=["status-ok"])
                with gr.Column(scale=2):
                    id_results = gr.HTML()

            id_btn.click(
                fn=identify_face,
                inputs=[query_img],
                outputs=[id_status, id_results],
            )

        # ── Page 3: Fairness Dashboard ────────────────────────────────────────
        with gr.Column(elem_classes=["ethos-page"]) as page_3:
            gr.HTML(_section(
                "Fairness Audit Results",
                "Per-demographic False Acceptance Rates measured on FairFace (86k images). "
                "Threshold = 0.1810 (EER-optimal from LFW).",
            ))
            dash_btn     = gr.Button("Load Dashboard", variant="primary")
            summary_html = gr.HTML()

            gr.HTML('<p style="color:var(--text-sec);font-size:12px;font-weight:600;'
                    'text-transform:uppercase;letter-spacing:0.07em;margin:20px 0 4px;">'
                    'Score Distributions — LFW</p>')
            dist_fig = gr.Plot()

            gr.HTML('<p style="color:var(--text-sec);font-size:12px;font-weight:600;'
                    'text-transform:uppercase;letter-spacing:0.07em;margin:20px 0 4px;">Race</p>')
            with gr.Row():
                race_bar_fig  = gr.Plot()
                race_fmrd_fig = gr.Plot()

            gr.HTML('<p style="color:var(--text-sec);font-size:12px;font-weight:600;'
                    'text-transform:uppercase;letter-spacing:0.07em;margin:20px 0 4px;">Gender</p>')
            with gr.Row():
                gender_bar_fig  = gr.Plot()
                gender_fmrd_fig = gr.Plot()

            gr.HTML('<p style="color:var(--text-sec);font-size:12px;font-weight:600;'
                    'text-transform:uppercase;letter-spacing:0.07em;margin:20px 0 4px;">Age</p>')
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

        # ── Page 4: Identification Metrics + Robustness ───────────────────────
        with gr.Column(elem_classes=["ethos-page"]) as page_4:
            gr.HTML(_section(
                "1:N Identification Metrics & Robustness",
                "CMC curve on a 3,000-subject LFW gallery. Robustness shows match-rate drop "
                "under blur, brightness shift, rotation, downsampling, and Gaussian noise.",
            ))
            metrics_btn     = gr.Button("Load Results", variant="primary")
            id_summary_html = gr.HTML()
            with gr.Row():
                cmc_plot_fig = gr.Plot(label="CMC Curve")
                rob_plot_fig = gr.Plot(label="Robustness Degradation")
            rob_table_html = gr.HTML()

            metrics_btn.click(
                fn=load_id_metrics,
                inputs=[],
                outputs=[id_summary_html, cmc_plot_fig, rob_plot_fig, rob_table_html],
            )

        # ── Page 5: Ethics Officer Chat ───────────────────────────────────────
        with gr.Column(elem_classes=["ethos-page"]) as page_5:
            gr.HTML(_section(
                "Ethics Officer",
                "Ask the AI Ethics Officer anything about the system's bias findings, "
                "EU AI Act compliance status, or mitigation strategies.",
            ))
            chatbot = gr.Chatbot(height=460)
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

        # ── Page 6: Live Assessment ───────────────────────────────────────────
        with gr.Column(elem_classes=["ethos-page"]) as page_6:
            gr.HTML(_section(
                "Live Liveness Assessment",
                "Real-time Presentation Attack Detection via webcam. "
                "RetinaFace detects the face, MiniFASNetV2 runs PAD. Target: ≥10 FPS on M4.",
            ))
            with gr.Row():
                with gr.Column(scale=1):
                    webcam_in = gr.Image(
                        sources=["webcam"], streaming=True,
                        label="Webcam Feed", type="numpy", height=360,
                    )
                with gr.Column(scale=1):
                    live_out = gr.Image(label="Annotated Output", type="numpy", height=360)

            fps_display    = gr.HTML(_fps_html(0))
            pad_score_disp = gr.HTML(_score_html(0.0))
            verdict_disp   = gr.HTML(_verdict_html(None))

            webcam_in.stream(
                fn=process_live_frame,
                inputs=[webcam_in],
                outputs=[live_out, fps_display, pad_score_disp, verdict_disp],
                stream_every=0.04,
                time_limit=300,
            )

        # ── Page 7: Generate Report ───────────────────────────────────────────
        with gr.Column(elem_classes=["ethos-page"]) as page_7:
            gr.HTML(_section(
                "EU AI Act Compliance Report",
                "Generates a full 9-page PDF compliance audit document. "
                "Calls the Ethics Officer API, embeds fairness charts, and formats "
                "to NIST/ISO regulator standards.",
            ))
            gen_btn    = gr.Button("Generate PDF Report", variant="primary")
            gen_status = gr.Markdown("")
            pdf_output = gr.File(label="Download Report")
            pdf_viewer = gr.HTML()

            gen_btn.click(
                fn=generate_pdf_report,
                inputs=[],
                outputs=[pdf_output, gen_status, pdf_viewer],
            )

    return app


# ── Entry point ───────────────────────────────────────────────────────────────

def _preload_background():
    import threading

    def _load():
        print("  [preload] Loading InsightFace model…")
        t = time.time()
        from app.inference import _model
        _model()
        print(f"  [preload] InsightFace ready  ({time.time()-t:.1f}s)")

        print("  [preload] Loading FairFace embeddings cache…")
        t = time.time()
        _ = state.fairface()
        print(f"  [preload] FairFace ready  ({len(state.fairface()['embeddings']):,} embs, {time.time()-t:.1f}s)")

        print("  [preload] Loading PAD model…")
        t = time.time()
        get_pad()
        print(f"  [preload] PAD ready  ({time.time()-t:.2f}s)")

        print("  [preload] All resources warm ✓")

    threading.Thread(target=_load, daemon=True).start()


if __name__ == "__main__":
    t0 = time.time()
    print("Starting ETHOS GUI…")
    app = build_app()
    print(f"App built in {(time.time()-t0)*1000:.0f} ms")
    _preload_background()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        theme=ethos_theme(),
        css=CUSTOM_CSS,
        allowed_paths=[str(Path(state.REPORTS_DIR).resolve())],
    )
