"""
ETHOS — Futuristic AI research lab aesthetic.
Deep space background · electric cyan glows · animated effects.
"""

import gradio as gr

BG_BASE    = "#04080f"
BG_SURFACE = "#080f1c"
BG_CARD    = "#0c1526"
ACCENT     = "#00e5ff"
SUCCESS    = "#10b981"
DANGER     = "#ef4444"
WARNING    = "#f59e0b"
TEXT_PRI   = "#f0f6ff"
TEXT_SEC   = "#8ba3c7"
TEXT_MUTED = "#3d5470"
BORDER     = "rgba(0,229,255,0.08)"


def ethos_theme() -> gr.Theme:
    return gr.themes.Base(
        primary_hue=gr.themes.colors.cyan,
        secondary_hue=gr.themes.colors.slate,
        neutral_hue=gr.themes.colors.slate,
        font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
    ).set(
        body_background_fill=BG_BASE,
        body_background_fill_dark=BG_BASE,
        block_background_fill=BG_SURFACE,
        block_background_fill_dark=BG_SURFACE,
        block_border_color=BORDER,
        block_border_color_dark=BORDER,
        input_background_fill=BG_CARD,
        input_background_fill_dark=BG_CARD,
        input_border_color=BORDER,
        input_border_color_dark=BORDER,
        input_placeholder_color=TEXT_MUTED,
        button_primary_background_fill=ACCENT,
        button_primary_background_fill_dark=ACCENT,
        button_primary_text_color="#04080f",
        button_primary_background_fill_hover="#33eeff",
        button_secondary_background_fill=BG_CARD,
        button_secondary_background_fill_dark=BG_CARD,
        button_secondary_text_color=TEXT_PRI,
        button_secondary_border_color=BORDER,
        body_text_color=TEXT_PRI,
        body_text_color_dark=TEXT_PRI,
        block_label_text_color=TEXT_SEC,
        block_title_text_color=TEXT_PRI,
        block_radius="12px",
        input_radius="8px",
        button_large_radius="8px",
        button_small_radius="6px",
        checkbox_background_color=BG_CARD,
        checkbox_background_color_dark=BG_CARD,
        slider_color=ACCENT,
        slider_color_dark=ACCENT,
    )


CUSTOM_CSS = """
/* ══════════════════════════════════════════════════════════════════════════════
   ETHOS — Futuristic dark theme
   ══════════════════════════════════════════════════════════════════════════════ */

/* ── CSS variables ─────────────────────────────────────────────────────────── */
:root {
    --bg-base:    #04080f;
    --bg-surface: #080f1c;
    --bg-card:    #0c1526;
    --accent:     #00e5ff;
    --accent2:    #7c3aed;
    --success:    #10b981;
    --danger:     #ef4444;
    --warning:    #f59e0b;
    --text-pri:   #f0f6ff;
    --text-sec:   #8ba3c7;
    --text-muted: #3d5470;
    --border:     rgba(0,229,255,0.08);
    --glow-cyan:  rgba(0,229,255,0.5);
    --radius:     12px;
    --radius-sm:  8px;
}

/* ── Base & background atmosphere ──────────────────────────────────────────── */
footer { display: none !important; }

body, #root {
    background: var(--bg-base) !important;
    /* Ambient radial glow blobs */
    background-image:
        radial-gradient(ellipse 60% 40% at 15% 45%, rgba(0,229,255,0.055) 0%, transparent 70%),
        radial-gradient(ellipse 50% 35% at 85% 20%, rgba(124,58,237,0.06) 0%, transparent 70%),
        radial-gradient(ellipse 40% 30% at 55% 85%, rgba(16,185,129,0.04) 0%, transparent 70%) !important;
}

.gradio-container {
    max-width: 1280px !important;
    margin: 0 auto !important;
    background: transparent !important;
    padding-top: 0 !important;
    position: relative;
}

/* Subtle dot-grid overlay on the whole page */
.gradio-container::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        radial-gradient(circle, rgba(0,229,255,0.12) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
    opacity: 0.35;
}

/* ── Hide Gradio tab bars (not used — pages are gr.Column) ──────────────────── */
[role="tablist"], .tab-nav {
    display: none !important;
}

/* ── Page visibility — JS toggles .ethos-page-active ────────────────────────── */
.ethos-page          { display: none !important; }
.ethos-page-active   { display: block !important; }

/* ── Sticky nav bar ────────────────────────────────────────────────────────── */
.ethos-header {
    position: sticky;
    top: 0;
    z-index: 200;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 28px;
    height: 58px;
    background: rgba(4,8,15,0.82) !important;
    backdrop-filter: blur(24px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
    border-bottom: 1px solid rgba(0,229,255,0.12) !important;
    box-shadow:
        0 1px 0 rgba(0,229,255,0.06),
        0 8px 32px rgba(0,0,0,0.6) !important;
    gap: 16px;
}

.ethos-brand { display: flex; align-items: center; gap: 9px; flex-shrink: 0; }

.ethos-logo-icon {
    font-size: 20px;
    font-weight: 900;
    background: linear-gradient(135deg, #00e5ff, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    display: inline-block;
    filter: drop-shadow(0 0 6px rgba(0,229,255,0.6));
    animation: icon-breathe 3s ease-in-out infinite alternate;
}
@keyframes icon-breathe {
    from { filter: drop-shadow(0 0 4px rgba(0,229,255,0.5)); }
    to   { filter: drop-shadow(0 0 14px rgba(0,229,255,0.9)); }
}

.ethos-logo-text {
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-pri);
    text-shadow: 0 0 20px rgba(0,229,255,0.3);
}

.ethos-nav {
    display: flex;
    align-items: center;
    gap: 2px;
    flex: 1;
    justify-content: center;
    overflow-x: auto;
    scrollbar-width: none;
}
.ethos-nav::-webkit-scrollbar { display: none; }

.e-nav-item {
    background: transparent;
    border: 1px solid transparent;
    color: var(--text-sec);
    font-size: 12.5px;
    font-weight: 500;
    padding: 5px 13px;
    border-radius: 6px;
    cursor: pointer;
    white-space: nowrap;
    font-family: Inter, system-ui, sans-serif;
    transition: all 0.18s ease;
    letter-spacing: 0.01em;
}
.e-nav-item:hover {
    color: var(--text-pri);
    background: rgba(0,229,255,0.05);
    border-color: rgba(0,229,255,0.1);
}
.e-nav-item.e-active {
    color: var(--accent);
    background: rgba(0,229,255,0.08);
    border-color: rgba(0,229,255,0.25);
    text-shadow: 0 0 10px rgba(0,229,255,0.6);
    box-shadow: 0 0 16px rgba(0,229,255,0.08), inset 0 0 8px rgba(0,229,255,0.04);
}

.ethos-act-badge {
    flex-shrink: 0;
    font-size: 9.5px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--accent);
    background: rgba(0,229,255,0.06);
    border: 1px solid rgba(0,229,255,0.2);
    border-radius: 20px;
    padding: 3px 10px;
    animation: badge-glow 2.5s ease-in-out infinite alternate;
}
@keyframes badge-glow {
    from { border-color: rgba(0,229,255,0.18); box-shadow: 0 0 6px rgba(0,229,255,0.1); }
    to   { border-color: rgba(0,229,255,0.4);  box-shadow: 0 0 14px rgba(0,229,255,0.25); }
}

/* ── Hero section ──────────────────────────────────────────────────────────── */
.hero-section {
    padding: 64px 0 44px 0;
    text-align: center;
    position: relative;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 10.5px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--accent);
    background: rgba(0,229,255,0.06);
    border: 1px solid rgba(0,229,255,0.18);
    border-radius: 20px;
    padding: 5px 14px;
    margin-bottom: 28px;
}

.badge-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: var(--accent);
    flex-shrink: 0;
    animation: dot-pulse 2s ease-in-out infinite;
    box-shadow: 0 0 6px var(--accent);
}
@keyframes dot-pulse {
    0%, 100% { transform: scale(1);   opacity: 1; }
    50%       { transform: scale(1.4); opacity: 0.6; }
}

.hero-name {
    font-size: 116px;
    font-weight: 900;
    font-family: 'Orbitron', 'Inter', system-ui, sans-serif;
    letter-spacing: -0.03em;
    line-height: 0.9;
    margin: 0 0 20px 0;
    background: linear-gradient(135deg, #00e5ff 0%, #a855f7 45%, #f0f6ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: hero-glow 4s ease-in-out infinite alternate;
}
@keyframes hero-glow {
    from { filter: drop-shadow(0 0 20px rgba(0,229,255,0.35)); }
    to   { filter: drop-shadow(0 0 55px rgba(0,229,255,0.7)); }
}

.hero-tagline {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--accent);
    margin: 0 0 12px 0;
    opacity: 0.8;
}

.hero-subtitle {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-pri);
    margin: 0 0 10px 0;
    letter-spacing: -0.01em;
}

.hero-desc {
    font-size: 14px;
    color: var(--text-sec);
    line-height: 1.8;
    max-width: 540px;
    margin: 0 auto 40px auto;
}

/* ── Metric grid ───────────────────────────────────────────────────────────── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin: 0 0 10px 0;
}

.metric-card {
    background: rgba(8,15,28,0.8);
    border: 1px solid rgba(0,229,255,0.1);
    border-radius: var(--radius-sm);
    padding: 20px 14px 16px 14px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all 0.22s cubic-bezier(0.4,0,0.2,1);
}
.metric-card:hover {
    border-color: rgba(0,229,255,0.3);
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0,229,255,0.08);
}
/* Top accent bar */
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.metric-card.neutral::before { background: linear-gradient(90deg, var(--accent), #7c3aed); }
.metric-card.pass::before    { background: var(--success); }
.metric-card.fail::before    { background: var(--danger); }

/* Shimmer sweep */
.metric-card::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(105deg, transparent 40%, rgba(0,229,255,0.04) 50%, transparent 60%);
    transform: translateX(-100%);
    animation: card-shimmer 6s ease-in-out infinite;
    pointer-events: none;
}
@keyframes card-shimmer {
    0%, 30%  { transform: translateX(-100%); }
    55%, 100%{ transform: translateX(200%); }
}

.metric-num {
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin-bottom: 6px;
    line-height: 1;
    font-variant-numeric: tabular-nums;
}
.metric-num.cyan  { color: var(--accent);  text-shadow: 0 0 18px rgba(0,229,255,0.55); }
.metric-num.green { color: var(--success); text-shadow: 0 0 18px rgba(16,185,129,0.55); }
.metric-num.red   { color: var(--danger);  text-shadow: 0 0 18px rgba(239,68,68,0.55); }
.metric-num.amber { color: var(--warning); text-shadow: 0 0 18px rgba(245,158,11,0.55); }

.metric-label {
    font-size: 9.5px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
}

/* ── Stack chips ───────────────────────────────────────────────────────────── */
.stack-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 20px;
    justify-content: center;
}
.stack-chip {
    font-size: 11px;
    font-weight: 500;
    color: var(--text-sec);
    background: rgba(0,229,255,0.03);
    border: 1px solid rgba(0,229,255,0.08);
    border-radius: 20px;
    padding: 4px 13px;
    transition: all 0.15s ease;
}
.stack-chip:hover {
    border-color: rgba(0,229,255,0.25);
    color: var(--accent);
    box-shadow: 0 0 10px rgba(0,229,255,0.08);
}

/* ── Divider ───────────────────────────────────────────────────────────────── */
.ethos-divider {
    height: 1px;
    border: none;
    margin: 30px 0;
    background: linear-gradient(90deg, transparent, rgba(0,229,255,0.15) 50%, transparent);
}

/* ── Section headers ───────────────────────────────────────────────────────── */
.section-header { margin: 8px 0 20px 0; }
.section-title {
    font-size: 21px;
    font-weight: 700;
    color: var(--text-pri);
    letter-spacing: -0.02em;
    margin: 0 0 5px 0;
    text-shadow: 0 0 30px rgba(0,229,255,0.12);
}
.section-sub {
    font-size: 13px;
    color: var(--text-sec);
    line-height: 1.6;
    margin: 0;
    max-width: 680px;
}

/* ── Glassmorphic Gradio blocks ────────────────────────────────────────────── */
.gradio-container .block {
    background: rgba(8,15,28,0.72) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(0,229,255,0.09) !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.03) !important;
    transition: border-color 0.2s ease !important;
}
.gradio-container .block:hover {
    border-color: rgba(0,229,255,0.2) !important;
}

/* ── Buttons ───────────────────────────────────────────────────────────────── */
button.primary {
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    font-size: 11.5px !important;
    transition: all 0.2s ease !important;
    position: relative;
    overflow: hidden;
}
button.primary:hover {
    box-shadow: 0 0 28px rgba(0,229,255,0.5), 0 4px 16px rgba(0,229,255,0.25) !important;
    transform: translateY(-1px) !important;
}

/* ── Verdict cards ─────────────────────────────────────────────────────────── */
.verdict-match {
    background: rgba(16,185,129,0.06);
    border: 1px solid rgba(16,185,129,0.3);
    box-shadow: 0 0 30px rgba(16,185,129,0.08);
    border-radius: var(--radius);
    padding: 28px;
    text-align: center;
}
.verdict-nomatch {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.3);
    box-shadow: 0 0 30px rgba(239,68,68,0.08);
    border-radius: var(--radius);
    padding: 28px;
    text-align: center;
}
.verdict-icon { font-size: 40px; line-height: 1; margin-bottom: 10px; }
.verdict-text { font-size: 20px; font-weight: 800; letter-spacing: 0.08em; }
.verdict-sim  { font-size: 13px; color: var(--text-sec); margin-top: 8px; }

/* ── Rank items ────────────────────────────────────────────────────────────── */
.rank-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: rgba(8,15,28,0.7);
    border: 1px solid rgba(0,229,255,0.08);
    border-radius: var(--radius-sm);
    margin-bottom: 8px;
    transition: all 0.18s ease;
}
.rank-item:hover {
    border-color: rgba(0,229,255,0.28);
    transform: translateX(4px);
    box-shadow: -4px 0 12px rgba(0,229,255,0.06);
}
.rank-badge {
    width: 28px; height: 28px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 800;
    flex-shrink: 0;
}

/* ── Compliance table ──────────────────────────────────────────────────────── */
.compliance-table {
    width: 100%;
    border-collapse: collapse;
    background: rgba(8,15,28,0.6);
    border-radius: var(--radius);
    overflow: hidden;
    border: 1px solid rgba(0,229,255,0.1);
}
.compliance-table thead tr {
    background: rgba(0,229,255,0.04);
    border-bottom: 1px solid rgba(0,229,255,0.1);
}
.compliance-table th {
    padding: 11px 16px;
    font-size: 10px; font-weight: 700;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--text-muted);
}
.compliance-table td {
    padding: 11px 16px;
    font-size: 14px; color: var(--text-pri);
    border-bottom: 1px solid rgba(0,229,255,0.05);
}
.compliance-table tbody tr:last-child td { border-bottom: none; }
.compliance-table tbody tr:hover td { background: rgba(0,229,255,0.02); }
.pass-badge { color: var(--success) !important; font-weight: 700; }
.fail-badge { color: var(--danger)  !important; font-weight: 700; }

/* ── Chat ──────────────────────────────────────────────────────────────────── */
.message.user {
    background: rgba(0,229,255,0.08) !important;
    border: 1px solid rgba(0,229,255,0.2) !important;
    border-radius: 16px 16px 4px 16px !important;
    color: var(--text-pri) !important;
    max-width: 75% !important;
    margin-left: auto !important;
}
.message.bot {
    background: rgba(8,15,28,0.85) !important;
    border: 1px solid rgba(0,229,255,0.1) !important;
    border-radius: 16px 16px 16px 4px !important;
    color: var(--text-pri) !important;
    max-width: 85% !important;
}

/* ── Status ────────────────────────────────────────────────────────────────── */
.status-ok  { color: var(--success); font-size: 13px; }
.status-err { color: var(--danger);  font-size: 13px; }
.status-run { color: var(--accent);  font-size: 13px; }

/* ── Scrollbar ─────────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: rgba(0,229,255,0.15); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,229,255,0.3); }
"""
