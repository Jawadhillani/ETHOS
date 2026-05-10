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

import gradio as gr
import numpy as np

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from gui.styles import ethos_theme, CUSTOM_CSS
from gui.plots import (
    far_bar_chart, fmrd_gauge, score_distribution, roc_curve, similarity_bar
)
import gui.state as state

from src.matching.engine import MatchingEngine
from src.matching.verifier import Verifier
from src.matching.identifier import Identifier
from src.llm.ethics_officer import EthicsOfficer

DEFAULT_THRESHOLD = 0.1810


# ── Lazy singletons ───────────────────────────────────────────────────────────

_verifier: Verifier | None = None
_identifier: Identifier | None = None
_officer: EthicsOfficer | None = None


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


# ── Tab 5: Ethics Officer Chat ────────────────────────────────────────────────

_chat_context = (
    "You are the Ethics Officer of ETHOS. You have access to the following "
    "fairness audit results:\n\n"
    + json.dumps(state.fairness_report() if state.FAIRNESS_JSON.exists() else {}, indent=2)
    + "\n\nAnswer questions about the system's bias findings, EU AI Act compliance, "
    "and mitigation strategies. Be precise and cite numbers."
)


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


# ── Tab 6: Generate Report ────────────────────────────────────────────────────

def generate_pdf_report(progress=gr.Progress()):
    progress(0, desc="Calling Ethics Officer — analysis…")
    officer = get_officer()
    report  = state.fairness_report()

    progress(0.25, desc="Calling Ethics Officer — analysis…")
    analysis = officer.analyze_fairness_report(report)

    progress(0.55, desc="Generating compliance summary…")
    summary = officer.generate_compliance_summary(report)

    progress(0.75, desc="Building PDF…")
    from src.reports.compliance_pdf import ComplianceReportGenerator
    gen = ComplianceReportGenerator(plots_dir=str(state.PLOTS_DIR))
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"ethos_compliance_audit_{ts}.pdf"
    pdf_path = str(state.REPORTS_DIR / fname)
    gen.generate(report, analysis, summary, pdf_path)

    # Also save to photos/
    photos_copy = str(ROOT / "photos" / fname)
    shutil.copy2(pdf_path, photos_copy)

    progress(1.0, desc="Done.")
    size_kb = Path(pdf_path).stat().st_size // 1024
    status = f"✓ Generated: {fname}  ({size_kb} KB)  →  also saved to photos/"
    return pdf_path, status


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

        # ── Tab 5: Ethics Officer Chat ────────────────────────────────────────
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

        # ── Tab 6: Generate Report ────────────────────────────────────────────
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

            gen_btn.click(
                fn=generate_pdf_report,
                inputs=[],
                outputs=[pdf_output, gen_status],
            )

    return app


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    t0 = time.time()
    print("Starting ETHOS GUI…")
    app = build_app()
    startup = time.time() - t0
    print(f"App built in {startup*1000:.0f} ms  (embeddings lazy — not yet loaded)")
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        theme=ethos_theme(),
        css=CUSTOM_CSS,
    )
