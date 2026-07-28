"""Nutrition report: visualize perturbation records after generation.

Builds a tabular summary of data/perturbations.json plus a set of Plotly panels
highlighting confidence tiers (high/moderate/low) across the record fields that
drive or correlate with confidence, and assembles them into one static HTML report.
Run scripts/generate_qc_report.py first.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
import plotly.graph_objects as go

if TYPE_CHECKING:
    from mglia.schema import PerturbationRecord

# Colors used in nutrition report
CONFIDENCE_ORDER = ["high", "moderate", "low"]
CONFIDENCE_COLORS = {"high": "#0ca30c", "moderate": "#fab219", "low": "#d03b3b"}

MIXSCALE_ORDER = ["binary", "graded", "unknown"]
MIXSCALE_COLORS = {"binary": "#2a78d6", "graded": "#1baf7a", "unknown": "#898781"}

DIVERGING_SCALE = [
    [0.0, "#104281"],
    [0.5, "#f0efec"],
    [1.0, "#e34948"],
]
SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"

DEG_DOWN_COLOR = GRIDLINE
DEG_UP_COLOR = INK_SECONDARY

CONFIDENCE_THRESHOLDS = {
    "n_cells_high": 200,
    "n_cells_moderate": 100,
    "perc_kd_high": 60,
    "perc_kd_moderate": 40,
}
BIMODALITY_THRESHOLD = 0.555


def build_qc_dataframe(records: list["PerturbationRecord"]) -> pd.DataFrame:
    """Flatten records into one QC row per record.

    Args:
        records: Validated PerturbationRecord list (e.g. from
            mglia.schema.validate_all_records).

    Returns:
        DataFrame with columns: perturbation, cell_model, confidence,
        n_cells, percent_knockdown, mixscale_response,
        bimodality_coefficient, n_deg_positive, n_deg_negative,
        mean_abs_delta_pctl, n_schpf_factors, n_flags, has_functional_readout.
    """
    rows = []
    for r in records:
        deg = r.prediction_targets.get("deg", {})
        signature_shift = r.prediction_targets.get("signature_shift", {})
        schpf_factors = r.prediction_targets.get("schpf_factors", {})
        mixscale_detail = r.prediction_targets.get("mixscale_response_detail", {})

        reliable_shifts = [
            abs(v["delta_pctl"]) for v in signature_shift.values() if v.get("reliable")
        ]
        mean_abs_delta_pctl = (
            sum(reliable_shifts) / len(reliable_shifts) if reliable_shifts else None
        )

        rows.append(
            {
                "perturbation": r.perturbation,
                "cell_model": r.cell_model,
                "confidence": r.confidence,
                "n_cells": r.n_cells,
                "percent_knockdown": r.percent_knockdown,
                "mixscale_response": r.mixscale_response,
                "bimodality_coefficient": mixscale_detail.get("bimodality_coefficient"),
                "n_deg_positive": deg.get("n_positive", 0),
                "n_deg_negative": deg.get("n_negative", 0),
                "mean_abs_delta_pctl": mean_abs_delta_pctl,
                "n_schpf_factors": len(schpf_factors),
                "n_flags": len(r.method_assumptions.flags),
                "has_functional_readout": bool(r.functional_readouts),
            }
        )
    return pd.DataFrame(rows)


def _label(row: pd.Series) -> str:
    return f"{row['perturbation']} ({row['cell_model']})"


def _base_layout(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        title=title,
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        font={"color": INK_PRIMARY, "family": "system-ui, -apple-system, sans-serif"},
        xaxis={"gridcolor": GRIDLINE, "linecolor": BASELINE, "automargin": True},
        yaxis={"gridcolor": GRIDLINE, "linecolor": BASELINE, "automargin": True},
        legend={"bgcolor": SURFACE},
        margin={"l": 60, "r": 40, "t": 60, "b": 80},
    )
    return fig


def render_cell_count_panel(df: pd.DataFrame) -> go.Figure:
    """Cell count per gene x model, colored by confidence tier."""
    fig = go.Figure()
    for tier in CONFIDENCE_ORDER:
        sub = df[df["confidence"] == tier].sort_values("n_cells")
        fig.add_trace(
            go.Bar(
                x=sub.apply(_label, axis=1),
                y=sub["n_cells"],
                name=tier,
                marker_color=CONFIDENCE_COLORS[tier],
            )
        )
    fig.add_hline(
        y=CONFIDENCE_THRESHOLDS["n_cells_high"],
        line_dash="dot",
        line_color=INK_MUTED,
        annotation_text="high threshold (200)",
    )
    fig.add_hline(
        y=CONFIDENCE_THRESHOLDS["n_cells_moderate"],
        line_dash="dot",
        line_color=INK_MUTED,
        annotation_text="moderate threshold (100)",
    )
    return _base_layout(fig, "Cell count per perturbation, by confidence tier")


def render_confidence_scatter_panel(df: pd.DataFrame) -> go.Figure:
    """Percent knockdown vs. n_cells scatter, colored by confidence tier."""
    fig = go.Figure()
    for tier in CONFIDENCE_ORDER:
        sub = df[df["confidence"] == tier]
        fig.add_trace(
            go.Scatter(
                x=sub["n_cells"],
                y=sub["percent_knockdown"],
                mode="markers",
                name=tier,
                text=sub.apply(_label, axis=1),
                marker={"color": CONFIDENCE_COLORS[tier], "size": 10},
            )
        )
    fig.add_hline(
        y=CONFIDENCE_THRESHOLDS["perc_kd_high"],
        line_dash="dot",
        line_color=INK_MUTED,
        annotation_text="high threshold (60)",
    )
    fig.add_hline(
        y=CONFIDENCE_THRESHOLDS["perc_kd_moderate"],
        line_dash="dot",
        line_color=INK_MUTED,
        annotation_text="moderate threshold (40)",
    )
    fig.update_xaxes(title="n_cells")
    fig.update_yaxes(title="percent_knockdown")
    return _base_layout(fig, "Percent knockdown vs. cell count, by confidence tier")


def render_signature_heatmap_panel(records: list["PerturbationRecord"]) -> go.Figure:
    """Genes x states heatmap of delta_pctl, row-labeled with confidence tier."""
    rows = []
    for r in records:
        shift = r.prediction_targets.get("signature_shift", {})
        row = {"label": f"{r.perturbation} ({r.cell_model}) [{r.confidence}]"}
        for state, v in shift.items():
            row[state] = v["delta_pctl"]
        rows.append(row)
    matrix = pd.DataFrame(rows).set_index("label")

    fig = go.Figure(
        data=go.Heatmap(
            z=matrix.values,
            x=matrix.columns,
            y=matrix.index,
            colorscale=DIVERGING_SCALE,
            zmid=0,
            colorbar={"title": "delta_pctl"},
        )
    )
    fig.update_layout(height=max(400, 20 * len(matrix.index)))
    return _base_layout(fig, "Median Percentile Signature shift vs NTC by state")


def render_deg_counts_panel(df: pd.DataFrame) -> go.Figure:
    """Significant DEG counts (positive/negative) per record, by confidence."""
    fig = go.Figure()
    sorted_df = df.sort_values(["confidence", "n_deg_positive"])
    fig.add_trace(
        go.Bar(
            x=sorted_df.apply(_label, axis=1),
            y=sorted_df["n_deg_positive"],
            name="upregulated",
            marker_color=[CONFIDENCE_COLORS[c] for c in sorted_df["confidence"]],
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Bar(
            x=sorted_df.apply(_label, axis=1),
            y=-sorted_df["n_deg_negative"],
            name="downregulated",
            marker_color=[CONFIDENCE_COLORS[c] for c in sorted_df["confidence"]],
            opacity=0.6,
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Bar(x=[None], y=[None], name="upregulated", marker_color=DEG_UP_COLOR)
    )
    fig.add_trace(
        go.Bar(x=[None], y=[None], name="downregulated", marker_color=DEG_DOWN_COLOR)
    )
    fig.update_layout(barmode="relative")
    return _base_layout(fig, "Significant DEG counts (bar color = confidence tier)")


def render_mixscale_panel(df: pd.DataFrame) -> go.Figure:
    """Bimodality coefficient per record, colored by mixscale response type."""
    fig = go.Figure()
    for kind in MIXSCALE_ORDER:
        sub = df[df["mixscale_response"] == kind]
        fig.add_trace(
            go.Scatter(
                x=sub.apply(_label, axis=1),
                y=sub["bimodality_coefficient"],
                mode="markers",
                name=kind,
                marker={"color": MIXSCALE_COLORS[kind], "size": 10},
            )
        )
    fig.add_hline(
        y=BIMODALITY_THRESHOLD,
        line_dash="dot",
        line_color=INK_MUTED,
        annotation_text=f"binary/graded threshold ({BIMODALITY_THRESHOLD})",
    )
    return _base_layout(fig, "Mixscale bimodality coefficient, by response type")


def render_flags_panel(
    df: pd.DataFrame, records: list["PerturbationRecord"]
) -> go.Figure:
    """Method-assumption flag counts per record, colored by confidence tier.

    Hovering a bar shows the specific flag text(s) for that record.
    """
    flags_by_label = {
        f"{r.perturbation} ({r.cell_model})": r.method_assumptions.flags
        for r in records
    }
    sorted_df = df.sort_values(["confidence", "n_flags"], ascending=[True, False])
    labels = sorted_df.apply(_label, axis=1)
    hover_text = [
        "<br>".join(flags_by_label.get(label, [])) or "no flags" for label in labels
    ]
    fig = go.Figure(
        data=go.Bar(
            x=labels,
            y=sorted_df["n_flags"],
            marker_color=[CONFIDENCE_COLORS[c] for c in sorted_df["confidence"]],
            hovertext=hover_text,
            hoverinfo="text",
        )
    )
    return _base_layout(
        fig, "Method-assumption flag count (bar color = confidence tier)"
    )


def render_functional_coverage_panel(df: pd.DataFrame) -> go.Figure:
    """Indicator of which records have real functional readout data."""
    sorted_df = df.sort_values(["has_functional_readout", "perturbation"])
    fig = go.Figure(
        data=go.Bar(
            x=sorted_df.apply(_label, axis=1),
            y=sorted_df["has_functional_readout"].astype(int),
            marker_color=[
                "#2a78d6" if v else INK_MUTED
                for v in sorted_df["has_functional_readout"]
            ],
        )
    )
    fig.update_yaxes(tickvals=[0, 1], ticktext=["no", "yes"])
    return _base_layout(fig, "Functional readout coverage")


def build_summary_counts(df: pd.DataFrame) -> dict:
    """Top-line counts for the report header.

    Args:
        df: QC dataframe from build_qc_dataframe.

    Returns:
        Dict with confidence tier counts and n with warnings.
    """
    return {
        "n_records": len(df),
        "by_confidence": df["confidence"].value_counts().to_dict(),
        "n_with_warnings": int((df["n_flags"] > 0).sum()),
    }


def render_summary_table(summary: dict) -> go.Figure:
    """Render the top-line summary counts as a Plotly table."""
    rows = [
        ("Total records", summary["n_records"]),
        *[
            (f"Confidence: {tier}", summary["by_confidence"].get(tier, 0))
            for tier in CONFIDENCE_ORDER
        ],
        ("Records with >=1 warning flag", summary["n_with_warnings"]),
    ]
    fig = go.Figure(
        data=go.Table(
            header={
                "values": ["Metric", "Count"],
                "fill_color": SURFACE,
                "font": {"color": INK_PRIMARY},
                "line_color": GRIDLINE,
            },
            cells={
                "values": [[r[0] for r in rows], [r[1] for r in rows]],
                "fill_color": SURFACE,
                "font": {"color": INK_SECONDARY},
                "line_color": GRIDLINE,
            },
        )
    )
    return _base_layout(fig, "Summary")


def render_qc_report(df: pd.DataFrame, records: list["PerturbationRecord"]) -> str:
    """Assemble all panels into one self-contained HTML report.

    Args:
        df: QC dataframe from build_qc_dataframe.
        records: The same records used to build df (needed for the per-state
            signature heatmap, which isn't fully flattened into df).

    Returns:
        Full HTML document as a string.
    """
    summary = build_summary_counts(df)
    panels = [
        render_summary_table(summary),
        render_cell_count_panel(df),
        render_confidence_scatter_panel(df),
        render_signature_heatmap_panel(records),
        render_deg_counts_panel(df),
        render_mixscale_panel(df),
        render_flags_panel(df, records),
        render_functional_coverage_panel(df),
    ]

    body_parts = []
    for i, fig in enumerate(panels):
        include_js = "cdn" if i == 0 else False
        body_parts.append(fig.to_html(full_html=False, include_plotlyjs=include_js))

    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Perturbation Records QC Report</title>
<style>
  body {{ background: {SURFACE}; color: {INK_PRIMARY};
          font-family: system-ui, -apple-system, sans-serif; margin: 24px; }}
  h1 {{ font-size: 20px; }}
  .panel {{ margin-bottom: 32px; }}
</style>
</head>
<body>
<h1>Perturbation Records QC Report</h1>
{"".join(f'<div class="panel">{p}</div>' for p in body_parts)}
</body>
</html>
"""
    return html
