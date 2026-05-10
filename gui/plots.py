"""
Interactive Plotly charts for the Fairness Dashboard tab.
All return plotly.graph_objects.Figure objects (rendered by gr.Plot).
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
    margin=dict(l=16, r=16, t=40, b=16),
    xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
    yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
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
        height=130,
        margin=dict(l=8, r=8, t=12, b=8),
        showlegend=False,
    )
    return fig
