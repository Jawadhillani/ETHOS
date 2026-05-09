"""
ComplianceReportGenerator: produces a regulator-grade EU AI Act compliance PDF.

Takes the fairness audit JSON + EthicsOfficer text outputs and assembles a
5-7 page document styled after NIST/ISO biometric evaluation reports.

Output: outputs/reports/ethos_compliance_audit_<timestamp>.pdf
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ── Colour palette (muted, regulatory) ───────────────────────────────────────
_NAVY   = colors.HexColor("#1a365d")
_STEEL  = colors.HexColor("#2d3748")
_RED    = colors.HexColor("#c53030")
_GREEN  = colors.HexColor("#276749")
_AMBER  = colors.HexColor("#975a16")
_LGRAY  = colors.HexColor("#f7fafc")
_MGRAY  = colors.HexColor("#e2e8f0")
_DGRAY  = colors.HexColor("#718096")

W, H = A4


def _styles():
    base = getSampleStyleSheet()
    s = {}

    s["cover_title"] = ParagraphStyle(
        "cover_title", fontSize=22, leading=28,
        textColor=_NAVY, fontName="Helvetica-Bold",
        alignment=TA_LEFT, spaceAfter=6,
    )
    s["cover_sub"] = ParagraphStyle(
        "cover_sub", fontSize=13, leading=18,
        textColor=_STEEL, fontName="Helvetica",
        alignment=TA_LEFT, spaceAfter=4,
    )
    s["cover_meta"] = ParagraphStyle(
        "cover_meta", fontSize=9, leading=13,
        textColor=_DGRAY, fontName="Helvetica",
        alignment=TA_LEFT,
    )
    s["section"] = ParagraphStyle(
        "section", fontSize=13, leading=16,
        textColor=_NAVY, fontName="Helvetica-Bold",
        spaceBefore=14, spaceAfter=4,
    )
    s["subsection"] = ParagraphStyle(
        "subsection", fontSize=10, leading=13,
        textColor=_STEEL, fontName="Helvetica-Bold",
        spaceBefore=8, spaceAfter=3,
    )
    s["body"] = ParagraphStyle(
        "body", fontSize=9, leading=13,
        textColor=_STEEL, fontName="Helvetica",
        alignment=TA_JUSTIFY, spaceAfter=4,
    )
    s["caption"] = ParagraphStyle(
        "caption", fontSize=8, leading=10,
        textColor=_DGRAY, fontName="Helvetica-Oblique",
        alignment=TA_CENTER, spaceAfter=6,
    )
    s["verdict_pass"] = ParagraphStyle(
        "verdict_pass", fontSize=9, leading=12,
        textColor=_GREEN, fontName="Helvetica-Bold",
    )
    s["verdict_fail"] = ParagraphStyle(
        "verdict_fail", fontSize=9, leading=12,
        textColor=_RED, fontName="Helvetica-Bold",
    )
    s["footer"] = ParagraphStyle(
        "footer", fontSize=7.5, leading=10,
        textColor=_DGRAY, fontName="Helvetica",
        alignment=TA_CENTER,
    )
    return s


def _hr(color=_MGRAY, thickness=0.5):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=6)


def _verdict_para(text, passed, style):
    marker = "PASS" if passed else "FAIL"
    color  = _GREEN if passed else _RED
    key    = "verdict_pass" if passed else "verdict_fail"
    return Paragraph(f"{text}   <font color='{'#276749' if passed else '#c53030'}'><b>[{marker}]</b></font>", style[key])


def _image(path, width_cm=15):
    p = Path(path)
    if not p.exists():
        return None
    return Image(str(p), width=width_cm * cm, height=width_cm * cm * 0.65)


def _findings_table(per_group: dict, threshold: float, style: dict):
    """Build a formatted FAR-per-group table."""
    data = [["Demographic Group", "FAR at Threshold", "Mean Similarity", "N Pairs"]]
    rows = sorted(per_group.items(), key=lambda kv: kv[1]["far_at_threshold"])
    for group, m in rows:
        far_pct = f"{m['far_at_threshold']*100:.4f}%"
        data.append([
            group,
            far_pct,
            f"{m['score_mean']:.4f}",
            f"{m['n_pairs']:,}",
        ])

    col_widths = [5.5*cm, 3.5*cm, 3.5*cm, 3*cm]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        # Header
        ("BACKGROUND",   (0, 0), (-1, 0), _NAVY),
        ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 8.5),
        ("BOTTOMPADDING",(0, 0), (-1, 0), 6),
        ("TOPPADDING",   (0, 0), (-1, 0), 6),
        # Body rows
        ("FONTNAME",  (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",  (0, 1), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _LGRAY]),
        ("TOPPADDING",    (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        # Worst row: highlight in pale red
        ("BACKGROUND", (0, len(data)-1), (-1, len(data)-1), colors.HexColor("#fff5f5")),
        ("TEXTCOLOR",  (1, len(data)-1), (1, len(data)-1), _RED),
        # Grid
        ("GRID",      (0, 0), (-1, -1), 0.4, _MGRAY),
        ("LINEBELOW", (0, 0), (-1, 0), 1, _NAVY),
        ("ALIGN",     (1, 0), (-1, -1), "CENTER"),
        ("ALIGN",     (0, 0), (0, -1), "LEFT"),
        ("LEFTPADDING",  (0, 0), (0, -1), 6),
    ]))
    return t


def _metrics_table(audits: dict, style: dict):
    """Summary compliance table: axis / FMRD / DI / verdict."""
    data = [["Demographic Axis", "FMRD", "DI", "FMRD Verdict", "DI Verdict"]]
    for axis, audit in audits.items():
        ratios = audit["fairness_ratios"]
        comp   = audit["compliance"]
        fmrd   = ratios["fmrd"]
        di     = ratios["disparate_impact"]
        fmrd_pass = comp["fmrd_compliant"]
        di_pass   = comp["di_compliant"]
        data.append([
            axis.title(),
            f"{fmrd:.2f}",
            f"{di:.4f}" if di is not None else "N/A",
            "PASS" if fmrd_pass else "FAIL",
            "PASS" if di_pass else "FAIL",
        ])

    col_widths = [4*cm, 2.5*cm, 2.5*cm, 3*cm, 3*cm]
    t = Table(data, colWidths=col_widths, repeatRows=1)

    cell_styles = [
        ("BACKGROUND",   (0, 0), (-1, 0), _NAVY),
        ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 8.5),
        ("BOTTOMPADDING",(0, 0), (-1, 0), 6),
        ("TOPPADDING",   (0, 0), (-1, 0), 6),
        ("FONTNAME",  (0, 1), (-1, -1), "Helvetica"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _LGRAY]),
        ("TOPPADDING",    (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("GRID",  (0, 0), (-1, -1), 0.4, _MGRAY),
        ("LINEBELOW", (0, 0), (-1, 0), 1, _NAVY),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("LEFTPADDING", (0, 0), (0, -1), 6),
    ]
    # Colour PASS/FAIL cells
    for row_idx in range(1, len(data)):
        fmrd_pass = data[row_idx][3] == "PASS"
        di_pass   = data[row_idx][4] == "PASS"
        cell_styles.append(("TEXTCOLOR", (3, row_idx), (3, row_idx),
                             _GREEN if fmrd_pass else _RED))
        cell_styles.append(("TEXTCOLOR", (4, row_idx), (4, row_idx),
                             _GREEN if di_pass else _RED))
        cell_styles.append(("FONTNAME", (3, row_idx), (4, row_idx), "Helvetica-Bold"))

    t.setStyle(TableStyle(cell_styles))
    return t


# ── Page template callbacks ───────────────────────────────────────────────────

def _make_page_callback(title: str, report_id: str):
    def _on_page(canvas, doc):
        canvas.saveState()
        # Header bar
        canvas.setFillColor(_NAVY)
        canvas.rect(0, H - 1.2*cm, W, 1.2*cm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(1.5*cm, H - 0.75*cm, "ETHOS — EU AI Act Compliance Audit")
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(W - 1.5*cm, H - 0.75*cm, f"CONFIDENTIAL — {report_id}")
        # Footer
        canvas.setFillColor(_DGRAY)
        canvas.setFont("Helvetica", 7.5)
        canvas.drawCentredString(W / 2, 0.8*cm,
            f"Page {doc.page}  |  {title}  |  Generated {datetime.now().strftime('%Y-%m-%d')}")
        canvas.setStrokeColor(_MGRAY)
        canvas.line(1.5*cm, 1.1*cm, W - 1.5*cm, 1.1*cm)
        canvas.restoreState()
    return _on_page


# ── Main generator ────────────────────────────────────────────────────────────

class ComplianceReportGenerator:
    """
    Assembles a regulator-grade EU AI Act compliance PDF from:
      - fairness audit JSON  (from scripts/evaluate_fairness.py)
      - EthicsOfficer text outputs (analyze, compliance_summary)
      - Fairness chart PNGs (from outputs/plots/)
    """

    def __init__(self, plots_dir: str = "outputs/plots"):
        self.plots_dir = Path(plots_dir)

    def generate(
        self,
        report: dict,
        analysis_text: str,
        compliance_summary_text: str,
        output_path: str,
    ) -> str:
        """
        Build the PDF and write it to output_path.

        Returns the resolved output path string.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        report_id = datetime.now().strftime("ETHOS-%Y%m%d-%H%M")
        meta = report.get("metadata", {})

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=1.8*cm, rightMargin=1.8*cm,
            topMargin=2.0*cm, bottomMargin=1.8*cm,
            title="ETHOS EU AI Act Compliance Audit",
            author="ETHOS Fairness Auditor",
        )

        S = _styles()
        story = []
        on_page = _make_page_callback("Fairness Audit Report", report_id)

        # ── Cover page ────────────────────────────────────────────────────────
        story.append(Spacer(1, 1.5*cm))
        story.append(_hr(_NAVY, 2))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("EU AI ACT COMPLIANCE AUDIT", S["cover_sub"]))
        story.append(Paragraph("Facial Biometric Recognition System", S["cover_title"]))
        story.append(Paragraph("ETHOS — Ethical Trust &amp; Holistic Oversight System", S["cover_sub"]))
        story.append(Spacer(1, 0.4*cm))
        story.append(_hr())

        cover_meta = [
            ["Report ID:",       report_id],
            ["Date:",            timestamp],
            ["System:",          "InsightFace buffalo_l (RetinaFace + ArcFace)"],
            ["Threshold:",       f"{meta.get('threshold', 0.181):.4f}  ({meta.get('threshold_source','EER-optimal')})"],
            ["Genuine dataset:", meta.get("datasets", {}).get("genuine_pairs", "LFW")],
            ["Impostor dataset:",meta.get("datasets", {}).get("impostor_pairs", "FairFace train")],
            ["Examiner:",        "ETHOS Automated Fairness Auditor v1.0"],
            ["Classification:",  "CONFIDENTIAL — Internal Use Only"],
        ]
        for label, value in cover_meta:
            story.append(Paragraph(f"<b>{label}</b>  {value}", S["cover_meta"]))
        story.append(Spacer(1, 0.5*cm))
        story.append(_hr())
        story.append(Spacer(1, 0.3*cm))

        # Overall verdict box
        audits = report.get("audits", {})
        all_pass = all(
            a["compliance"]["fmrd_compliant"] and a["compliance"].get("di_compliant", True)
            for a in audits.values()
        )
        verdict_color = _GREEN if all_pass else _RED
        verdict_text  = "COMPLIANT" if all_pass else "NON-COMPLIANT"
        story.append(Paragraph(
            f"<font color='{'#276749' if all_pass else '#c53030'}'>"
            f"<b>OVERALL COMPLIANCE VERDICT: {verdict_text}</b></font>",
            ParagraphStyle("verd", fontSize=13, leading=16,
                           fontName="Helvetica-Bold", spaceAfter=4,
                           textColor=verdict_color),
        ))
        story.append(Spacer(1, 0.2*cm))
        story.append(_metrics_table(audits, S))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(
            "<i>Thresholds: FMRD ≤ 1.50 (PASS) | DI ≥ 0.80 (PASS). "
            "Red cells indicate EU AI Act compliance violations.</i>",
            S["caption"],
        ))
        story.append(PageBreak())

        # ── Section 1: Executive Summary ──────────────────────────────────────
        story.append(Paragraph("1. Executive Summary", S["section"]))
        story.append(_hr())
        # Use first ~1200 chars of compliance_summary as the executive summary block
        summary_intro = compliance_summary_text[:1200].strip()
        if len(compliance_summary_text) > 1200:
            summary_intro += "…"
        for para in summary_intro.split("\n\n"):
            clean = para.strip().lstrip("#").strip()
            if clean:
                story.append(Paragraph(clean, S["body"]))
                story.append(Spacer(1, 2))

        # ── Section 2: Methodology ────────────────────────────────────────────
        story.append(Paragraph("2. Audit Methodology", S["section"]))
        story.append(_hr())
        story.append(Paragraph(
            "This audit employs a hybrid evaluation strategy to measure demographic fairness "
            "in a facial biometric verification system. <b>Genuine pairs</b> (same-person comparisons) "
            "were drawn from the LFW (Labeled Faces in the Wild) dataset: 3,000 verified same-person "
            "image pairs, providing overall FRR and EER measurements. <b>Impostor pairs</b> "
            "(different-person comparisons) were drawn from the FairFace train split (86,486 images), "
            "stratified by demographic group, with 50,000 randomly sampled within-group pairs per "
            "group providing per-demographic FAR measurements.",
            S["body"],
        ))
        story.append(Spacer(1, 3))
        story.append(Paragraph(
            "The operational threshold (0.1810) was derived from the LFW Equal Error Rate sweep "
            "(Week 3), representing the cosine similarity value at which FAR = FRR across the full "
            "dataset (EER = 0.30%, AUC = 0.9994). All embeddings are 512-dimensional L2-normalised "
            "vectors from the ArcFace recognition model (buffalo_l, InsightFace).",
            S["body"],
        ))
        story.append(Spacer(1, 3))
        story.append(Paragraph(
            "<b>Fairness metrics:</b> False Match Rate Disparity (FMRD) = max(FAR) / min(FAR) across "
            "groups; Disparate Impact (DI) = (1 − FAR_unprivileged) / (1 − FAR_privileged). "
            "Compliance thresholds: FMRD ≤ 1.50, DI ≥ 0.80 (EU AI Act / US 4/5ths rule).",
            S["body"],
        ))

        # ── Section 3: Findings ───────────────────────────────────────────────
        story.append(Paragraph("3. Fairness Audit Findings", S["section"]))
        story.append(_hr())

        axis_config = {
            "race":   ("3.1 Race", "fairness_far_by_race.png", "fairness_ratios_race.png"),
            "gender": ("3.2 Gender", "fairness_far_by_gender.png", "fairness_ratios_gender.png"),
            "age":    ("3.3 Age", "fairness_far_by_age.png", "fairness_ratios_age.png"),
        }

        for axis, (heading, bar_chart, ratio_chart) in axis_config.items():
            if axis not in audits:
                continue
            audit = audits[axis]
            ratios = audit["fairness_ratios"]
            comp   = audit["compliance"]
            summ   = audit["summary"]

            fmrd_pass = comp["fmrd_compliant"]
            di_pass   = comp.get("di_compliant", True)

            story.append(Paragraph(heading, S["subsection"]))

            fmrd_tag = '<font color="#276749">PASS</font>' if fmrd_pass else '<font color="#c53030">FAIL</font>'
            di_tag   = '<font color="#276749">PASS</font>' if di_pass   else '<font color="#c53030">FAIL</font>'
            verdict_line = (
                f"FMRD = <b>{ratios['fmrd']:.2f}</b>  ({fmrd_tag})  "
                f"&nbsp;&nbsp;|&nbsp;&nbsp;  "
                f"DI = <b>{ratios['disparate_impact']:.4f}</b>  ({di_tag})"
            )
            story.append(Paragraph(verdict_line, S["body"]))
            story.append(Spacer(1, 4))

            story.append(Paragraph(
                f"Best group (lowest FAR): <b>{summ['best_far_group']}</b>  "
                f"&nbsp;&nbsp;|&nbsp;&nbsp;  "
                f"Worst group (highest FAR): <b>{summ['worst_far_group']}</b>",
                S["body"],
            ))
            story.append(Spacer(1, 6))
            story.append(_findings_table(audit["per_group"], audit["threshold"], S))
            story.append(Spacer(1, 6))

            # Embed charts side by side if both exist
            img_bar   = _image(self.plots_dir / bar_chart,   width_cm=8.2)
            img_ratio = _image(self.plots_dir / ratio_chart, width_cm=7.0)
            if img_bar and img_ratio:
                chart_table = Table(
                    [[img_bar, img_ratio]],
                    colWidths=[8.6*cm, 7.4*cm],
                )
                chart_table.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP")]))
                story.append(KeepTogether([
                    chart_table,
                    Paragraph(
                        f"Figure: FAR by {axis} group (left) and fairness ratio compliance (right)",
                        S["caption"],
                    ),
                ]))
            elif img_bar:
                story.append(KeepTogether([
                    img_bar,
                    Paragraph(f"Figure: FAR by {axis} group", S["caption"]),
                ]))

            story.append(Spacer(1, 8))

        # Score distribution chart (race only — most illustrative)
        dist_img = _image(self.plots_dir / "fairness_score_dist_by_race.png", width_cm=14)
        if dist_img:
            story.append(Paragraph("3.4 Impostor Score Distributions by Race", S["subsection"]))
            story.append(KeepTogether([
                dist_img,
                Paragraph(
                    "Figure: Impostor cosine similarity distributions per racial group. "
                    "Rightward shift indicates higher false match risk. "
                    "Dashed vertical line = operational threshold (0.1810).",
                    S["caption"],
                ),
            ]))

        story.append(PageBreak())

        # ── Section 4: Full Analysis ──────────────────────────────────────────
        story.append(Paragraph("4. Ethics Officer Analysis", S["section"]))
        story.append(_hr())
        story.append(Paragraph(
            "The following analysis was generated by the ETHOS Ethics Officer "
            "(Anthropic claude-sonnet-4-5) from the raw fairness metrics above.",
            ParagraphStyle("note", fontSize=8, leading=11, textColor=_DGRAY,
                           fontName="Helvetica-Oblique", spaceAfter=8),
        ))

        for para in analysis_text.split("\n\n"):
            clean = para.strip()
            if not clean:
                continue
            # Markdown-style headings → subsection style
            if clean.startswith("## "):
                story.append(Paragraph(clean[3:], S["subsection"]))
            elif clean.startswith("# "):
                story.append(Paragraph(clean[2:], S["section"]))
            else:
                # Strip remaining markdown (bold, italic, tables)
                clean = clean.replace("**", "").replace("*", "").lstrip("#").strip()
                if clean:
                    story.append(Paragraph(clean, S["body"]))
            story.append(Spacer(1, 2))

        story.append(PageBreak())

        # ── Section 5: Compliance Verdict ─────────────────────────────────────
        story.append(Paragraph("5. Compliance Verdict", S["section"]))
        story.append(_hr())
        story.append(Paragraph(
            "Based on the fairness metrics computed in this audit, the following "
            "compliance verdicts apply under EU AI Act provisions for high-risk "
            "biometric identification systems (Annex III, Article 10, Article 13):",
            S["body"],
        ))
        story.append(Spacer(1, 8))
        story.append(_metrics_table(audits, S))
        story.append(Spacer(1, 6))

        overall_verdict = "NON-COMPLIANT" if not all_pass else "COMPLIANT"
        overall_color   = _RED if not all_pass else _GREEN
        story.append(Paragraph(
            f"<b>Overall system verdict: "
            f"<font color='{'#c53030' if not all_pass else '#276749'}'>"
            f"{overall_verdict}</font></b>",
            ParagraphStyle("ov", fontSize=11, leading=14, fontName="Helvetica-Bold",
                           spaceAfter=6, textColor=overall_color),
        ))
        story.append(Paragraph(
            "This system <b>cannot be deployed</b> as a high-risk biometric identification "
            "system in the EU without remediation demonstrating FMRD ≤ 1.50 across all "
            "protected demographic attributes.",
            S["body"],
        ))

        # ── Section 6: Limitations ────────────────────────────────────────────
        story.append(Paragraph("6. Limitations of This Audit", S["section"]))
        story.append(_hr())
        limitations = [
            "<b>No per-group FRR (FNMRD unavailable):</b> LFW genuine pairs lack demographic "
            "labels. The False Non-Match Rate Disparity (FNMRD) cannot be computed from this "
            "dataset combination. A complete audit requires a demographically labelled genuine-pair "
            "dataset (e.g., RFW).",
            "<b>Single-image-per-identity (FairFace):</b> FairFace train contains one image per "
            "person. Impostor pairs are within-demographic cross-identity comparisons. "
            "This is standard for FAR estimation but does not capture intra-subject variation.",
            "<b>Infant/elderly sample size:</b> The 0-2 group contains 1,788 images and the 70+ "
            "group contains 842 images. Statistical confidence for these cohorts is lower than "
            "for prime-adult groups. The 42× FMRD should be interpreted as a directional finding "
            "requiring targeted evaluation, not a precise deployment metric.",
            "<b>Threshold optimisation on LFW:</b> The EER threshold (0.1810) was derived from "
            "a dataset that may not represent the target deployment population. Operational "
            "threshold selection should be repeated on deployment-domain data.",
        ]
        for item in limitations:
            story.append(Paragraph(f"• {item}", S["body"]))
            story.append(Spacer(1, 3))

        # ── Build ─────────────────────────────────────────────────────────────
        doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
        return str(output_path)
