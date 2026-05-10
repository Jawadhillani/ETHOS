"""
ETHOS custom CSS and Gradio theme.
Dark professional palette matching the PDF + chart colour system.
"""

import gradio as gr

# ── Colour tokens ─────────────────────────────────────────────────────────────
BG_BASE    = "#0f1419"
BG_SURFACE = "#1a2233"
BG_CARD    = "#1e2d3d"
ACCENT     = "#2b6cb0"
ACCENT_LT  = "#4299e1"
SUCCESS    = "#2f855a"
WARNING    = "#c05621"
DANGER     = "#e53e3e"
TEXT_PRI   = "#e2e8f0"
TEXT_SEC   = "#a0aec0"
TEXT_MUTED = "#718096"
BORDER     = "#2d3748"


def ethos_theme() -> gr.Theme:
    return gr.themes.Base(
        primary_hue=gr.themes.colors.blue,
        secondary_hue=gr.themes.colors.slate,
        neutral_hue=gr.themes.colors.slate,
        font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
    ).set(
        # Background
        body_background_fill=BG_BASE,
        body_background_fill_dark=BG_BASE,
        block_background_fill=BG_SURFACE,
        block_background_fill_dark=BG_SURFACE,
        block_border_color=BORDER,
        block_border_color_dark=BORDER,
        # Inputs
        input_background_fill=BG_CARD,
        input_background_fill_dark=BG_CARD,
        input_border_color=BORDER,
        input_border_color_dark=BORDER,
        input_placeholder_color=TEXT_MUTED,
        # Buttons
        button_primary_background_fill=ACCENT,
        button_primary_background_fill_dark=ACCENT,
        button_primary_text_color=TEXT_PRI,
        button_primary_background_fill_hover=ACCENT_LT,
        button_secondary_background_fill=BG_CARD,
        button_secondary_background_fill_dark=BG_CARD,
        button_secondary_text_color=TEXT_PRI,
        button_secondary_border_color=BORDER,
        # Text
        body_text_color=TEXT_PRI,
        body_text_color_dark=TEXT_PRI,
        block_label_text_color=TEXT_SEC,
        block_title_text_color=TEXT_PRI,
        # Misc
        block_radius="8px",
        input_radius="6px",
        button_large_radius="6px",
        button_small_radius="4px",
        checkbox_background_color=BG_CARD,
        checkbox_background_color_dark=BG_CARD,
        slider_color=ACCENT,
        slider_color_dark=ACCENT,
    )


CUSTOM_CSS = f"""
/* ── Global ─────────────────────────────────────────────────────────────── */
* {{ box-sizing: border-box; }}

footer {{ display: none !important; }}
.gradio-container {{ max-width: 1200px !important; margin: 0 auto; }}

/* ── Tab bar ─────────────────────────────────────────────────────────────── */
.tab-nav button {{
    color: {TEXT_SEC} !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    letter-spacing: 0.02em !important;
    padding: 10px 18px !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.15s ease !important;
}}
.tab-nav button:hover {{
    color: {TEXT_PRI} !important;
}}
.tab-nav button.selected {{
    color: {ACCENT_LT} !important;
    border-bottom: 2px solid {ACCENT_LT} !important;
    background: transparent !important;
}}

/* ── Cards ───────────────────────────────────────────────────────────────── */
.ethos-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 12px;
}}
.metric-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 16px 20px;
    text-align: center;
}}
.metric-value {{
    font-size: 28px;
    font-weight: 700;
    color: {TEXT_PRI};
    margin: 4px 0;
}}
.metric-label {{
    font-size: 11px;
    color: {TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.pass-badge  {{ color: {SUCCESS} !important; font-weight: 700; }}
.fail-badge  {{ color: {DANGER}  !important; font-weight: 700; }}
.warn-badge  {{ color: {WARNING} !important; font-weight: 700; }}

/* ── Landing hero ────────────────────────────────────────────────────────── */
.hero-title {{
    font-size: 42px;
    font-weight: 800;
    color: {TEXT_PRI};
    letter-spacing: -0.02em;
    line-height: 1.15;
    margin: 0 0 8px 0;
}}
.hero-accent {{
    color: {ACCENT_LT};
}}
.hero-sub {{
    font-size: 17px;
    color: {TEXT_SEC};
    line-height: 1.6;
    margin: 0 0 24px 0;
    max-width: 640px;
}}
.hero-divider {{
    border: none;
    border-top: 1px solid {BORDER};
    margin: 24px 0;
}}
.stat-row {{
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
    margin: 16px 0;
}}
.stat-item {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 14px 20px;
    min-width: 140px;
}}
.stat-num  {{ font-size: 22px; font-weight: 700; color: {ACCENT_LT}; }}
.stat-desc {{ font-size: 11px; color: {TEXT_MUTED}; margin-top: 2px; }}

/* ── Similarity meter ────────────────────────────────────────────────────── */
.sim-high {{ color: {SUCCESS} !important; font-weight: 700; font-size: 22px; }}
.sim-low  {{ color: {DANGER}  !important; font-weight: 700; font-size: 22px; }}
.sim-mid  {{ color: {WARNING} !important; font-weight: 700; font-size: 22px; }}

/* ── Chat bubbles ────────────────────────────────────────────────────────── */
.message.user {{
    background: {ACCENT} !important;
    border-radius: 16px 16px 4px 16px !important;
    color: white !important;
    margin-left: auto !important;
    max-width: 75% !important;
}}
.message.bot {{
    background: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 16px 16px 16px 4px !important;
    color: {TEXT_PRI} !important;
    max-width: 85% !important;
}}

/* ── Identify results ────────────────────────────────────────────────────── */
.rank-item {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 6px;
    margin-bottom: 6px;
}}
.rank-badge {{
    background: {ACCENT};
    color: white;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
    flex-shrink: 0;
}}

/* ── Status bar ──────────────────────────────────────────────────────────── */
.status-ok  {{ color: {SUCCESS}; font-size: 13px; }}
.status-err {{ color: {DANGER};  font-size: 13px; }}
.status-run {{ color: {ACCENT_LT}; font-size: 13px; }}
"""
