"""
Interactive Plotly charts for the Fairness Dashboard, Identification, and
Robustness tabs.  All return plotly.graph_objects.Figure objects (rendered
by gr.Plot).
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Matches the CSS palette
BG    = "#1a2233"
PAPER = "#1e2d3d"
GRID  = "#2d3748"
TEXT  = "#e2e8f0"
TEXT2 = "#a0aec0"

_COLORS = [
    "#4299e1", "#f6ad55", "#68d391", "#b794f4",
    "#fc8181", "#76e4f7", "#f687b3", "#fbd38d",
    "#9ae6b4",
]

_LAYOUT = dict(
    paper_bgcolor=PAPER,
    plot_bgcolor=BG,
    font=dict(family="Inter, system-ui, sans-serif", color=TEXT, size=12),
    # margin and xaxis/yaxis intentionally omitted — set per-chart to avoid
    # duplicate keyword argument errors when spreading **_LAYOUT
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor=GRID,
        borderwidth=1,
        font=dict(size=11),
    ),
)


def far_bar_chart(per_group: dict, axis_label: str) -> go.Figure:
    """Horizontal bar chart of FAR per group."""
    groups = list(per_group.keys())
    fars   = [per_group[g]["far_at_threshold"] * 100 for g in groups]
    order  = np.argsort(fars)
    groups = [groups[i] for i in order]
    fars   = [fars[i]   for i in order]
    colors = [_COLORS[i % len(_COLORS)] for i in range(len(groups))]

    fig = go.Figure(go.Bar(
        x=fars, y=groups, orientation="h",
        marker_color=colors,
        text=[f"{v:.4f}%" for v in fars],
        textposition="outside",
        textfont=dict(size=11, color=TEXT2),
        hovertemplate="%{y}: %{x:.4f}%<extra></extra>",
    ))
    fig.update_layout(
        **_LAYOUT,
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        margin=dict(l=16, r=80, t=40, b=16),
        title=dict(text=f"False Acceptance Rate by {axis_label}", font=dict(size=14, color=TEXT)),
        xaxis_title="FAR (%)",
        height=max(300, len(groups) * 48 + 80),
        showlegend=False,
    )
    return fig


def fmrd_gauge(fmrd: float, threshold: float = 1.5) -> go.Figure:
    """Gauge chart for FMRD compliance."""
    pct   = min(fmrd / (threshold * 3), 1.0)
    color = "#2f855a" if fmrd <= threshold else "#e53e3e"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fmrd,
        number=dict(font=dict(size=28, color=TEXT), suffix="×"),
        gauge=dict(
            axis=dict(range=[0, threshold * 3],
                      tickcolor=TEXT2, tickfont=dict(color=TEXT2, size=10)),
            bar=dict(color=color, thickness=0.35),
            bgcolor=BG,
            bordercolor=GRID,
            threshold=dict(
                line=dict(color="#fc8181", width=2),
                thickness=0.75,
                value=threshold,
            ),
            steps=[
                dict(range=[0, threshold], color="rgba(47,133,90,0.15)"),
                dict(range=[threshold, threshold * 3], color="rgba(229,62,62,0.10)"),
            ],
        ),
        title=dict(text="FMRD", font=dict(size=14, color=TEXT2)),
    ))
    fig.update_layout(
        **_LAYOUT,
        height=220,
        margin=dict(l=24, r=24, t=40, b=8),
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
    )
    return fig


def score_distribution(genuine: np.ndarray, impostor: np.ndarray, threshold: float) -> go.Figure:
    """Overlaid histogram of genuine vs impostor scores."""
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=impostor, name="Impostor",
        marker_color="#fc8181", opacity=0.65,
        nbinsx=80, histnorm="probability density",
        hovertemplate="Sim: %{x:.3f}<extra>Impostor</extra>",
    ))
    fig.add_trace(go.Histogram(
        x=genuine, name="Genuine",
        marker_color="#4299e1", opacity=0.65,
        nbinsx=80, histnorm="probability density",
        hovertemplate="Sim: %{x:.3f}<extra>Genuine</extra>",
    ))
    fig.add_vline(
        x=threshold, line_dash="dash", line_color=TEXT,
        line_width=1.5,
        annotation_text=f"Threshold {threshold:.3f}",
        annotation_font=dict(color=TEXT2, size=11),
    )
    fig.update_layout(
        **_LAYOUT,
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        margin=dict(l=16, r=16, t=40, b=16),
        barmode="overlay",
        title=dict(text="Score Distributions — Genuine vs Impostor", font=dict(size=14, color=TEXT)),
        xaxis_title="Cosine Similarity",
        yaxis_title="Density",
        height=300,
    )
    return fig


def roc_curve(far: np.ndarray, frr: np.ndarray, auc: float) -> go.Figure:
    tpr   = 1.0 - frr
    order = np.argsort(far)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=far[order], y=tpr[order],
        mode="lines", name=f"ETHOS (AUC={auc:.4f})",
        line=dict(color="#4299e1", width=2.5),
        hovertemplate="FAR: %{x:.4f}<br>TPR: %{y:.4f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode="lines", name="Random",
        line=dict(color=TEXT2, width=1, dash="dash"),
    ))
    fig.update_layout(
        **_LAYOUT,
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        margin=dict(l=16, r=16, t=40, b=16),
        title=dict(text="ROC Curve", font=dict(size=14, color=TEXT)),
        xaxis_title="False Positive Rate (FAR)",
        yaxis_title="True Positive Rate (1 − FRR)",
        height=320,
    )
    return fig


def similarity_bar(similarity: float, threshold: float) -> go.Figure:
    """Single horizontal bar showing similarity vs threshold."""
    color = "#2f855a" if similarity >= threshold else "#e53e3e"
    fig = go.Figure(go.Bar(
        x=[similarity], y=["Similarity"],
        orientation="h",
        marker_color=color,
        text=[f"{similarity:.4f}"],
        textposition="outside",
        textfont=dict(size=14, color=TEXT),
        width=0.4,
    ))
    fig.add_vline(
        x=threshold, line_dash="dash", line_color=TEXT2, line_width=1.5,
        annotation_text=f"Threshold {threshold:.3f}",
        annotation_position="top right",
        annotation_font=dict(color=TEXT2, size=10),
    )
    fig.update_layout(
        **_LAYOUT,
        xaxis=dict(range=[0, 1.05], gridcolor=GRID, zerolinecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        height=130,
        margin=dict(l=8, r=8, t=12, b=8),
        showlegend=False,
    )
    return fig


def cmc_curve(rank_k: list, n_gallery: int, n_probes: int) -> go.Figure:
    """Interactive CMC curve for the Identification Metrics panel."""
    ranks = list(range(1, len(rank_k) + 1))
    pcts  = [v * 100 for v in rank_k]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ranks, y=pcts,
        mode="lines+markers",
        name="ETHOS (ArcFace buffalo_l)",
        line=dict(color="#4299e1", width=2.5),
        marker=dict(size=5),
        hovertemplate="Rank-%{x}: %{y:.2f}%<extra></extra>",
    ))

    # Mark key ranks
    for k, color in [(1, "#fc8181"), (5, "#f6ad55"), (10, "#68d391")]:
        if k <= len(rank_k):
            val = rank_k[k - 1] * 100
            fig.add_vline(x=k, line_dash="dash", line_color=color,
                          line_width=1.5,
                          annotation_text=f"R{k}: {val:.1f}%",
                          annotation_font=dict(color=color, size=10))

    fig.update_layout(
        **_LAYOUT,
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID, title="Rank"),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID, range=[0, 102]),
        margin=dict(l=16, r=16, t=50, b=16),
        title=dict(
            text=f"CMC Curve — {n_probes:,} probes vs {n_gallery:,}-subject gallery",
            font=dict(size=14, color=TEXT),
        ),
        yaxis_title="Identification Rate (%)",
        height=340,
    )
    return fig


def robustness_chart(robustness_data: dict) -> go.Figure:
    """
    Overlaid line chart of match-rate degradation for all perturbation types.
    robustness_data = {name: [{severity, match_rate, x_label}, ...]}
    """
    pert_items = robustness_data.get("perturbations", {})
    fig = go.Figure()

    for i, (name, rows) in enumerate(pert_items.items()):
        sevs  = [str(r["severity"]) for r in rows]
        rates = [r["match_rate"] * 100 for r in rows]
        color = _COLORS[i % len(_COLORS)]
        fig.add_trace(go.Scatter(
            x=list(range(len(sevs))), y=rates,
            mode="lines+markers",
            name=name,
            line=dict(color=color, width=2),
            marker=dict(size=6),
            text=sevs,
            hovertemplate=f"{name}<br>sev=%{{text}}<br>rate=%{{y:.1f}}%<extra></extra>",
        ))

    fig.update_layout(
        **_LAYOUT,
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID, title="Severity Step"),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID, range=[0, 105]),
        margin=dict(l=16, r=16, t=50, b=16),
        title=dict(
            text="Robustness Degradation — Match Rate vs Perturbation Severity",
            font=dict(size=14, color=TEXT),
        ),
        yaxis_title="Match Rate (%)",
        height=340,
    )
    return fig
