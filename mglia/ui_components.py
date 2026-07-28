"""Reusable Streamlit UI components for the mglia explorer."""

from __future__ import annotations

import io
from pathlib import Path
from typing import TYPE_CHECKING

import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from mglia import qc_report
from mglia.constants import (
    CHART_FONT_COLOR,
    COLOR_DANGER,
    COLOR_DOWN,
    COLOR_MUTED,
    COLOR_NEUTRAL,
    COLOR_NOT_MEASURED,
    COLOR_RESPONSE_BADGE,
    COLOR_SUCCESS,
    COLOR_UP,
    CONFIDENCE_COLORS,
    RNA_VOLCANO_COLORS,
    SEVERITY_COLORS,
    STATES,
)
from mglia.method_assumptions import get_all_flags

if TYPE_CHECKING:
    from mglia.schema import FunctionalReadout, PerturbationRecord

_DIRECTION_ARROWS = {"up": "↑", "down": "↓", "no_change": "—", "not_measured": "—"}

_KD_SOURCE_LABELS = {
    "measured_rtqpcr": "RT-qPCR",
    "measured_transcriptomic": "Transcriptomic",
    "not_measured": "Not measured",
}

# Shared palette with mglia.qc_report
GREEN = qc_report.CONFIDENCE_COLORS["high"]
YELLOW = qc_report.CONFIDENCE_COLORS["moderate"]
RED = qc_report.CONFIDENCE_COLORS["low"]


def render_global_styles() -> None:
    """Inject CSS bumping st.caption() text to a more readable size.

    Streamlit's default caption size (~0.8rem) reads as too small throughout
    the app. Called on top of every page to standardize styling.
    """
    st.markdown(
        "<style>"
        "[data-testid='stCaptionContainer'] { font-size: 1rem; }"
        "[data-testid='stMetricLabel'] { font-size: 3rem; }"
        "[data-testid='stMetricValue'] { font-size: 3rem; }"
        "[data-testid='stMetricDelta'] { font-size: 3rem; }"
        "</style>",
        unsafe_allow_html=True,
    )


def _pill(label: str, color: str) -> str:
    return (
        f'<span style="background-color:{color}22;color:{color};'
        f"border:1px solid {color};border-radius:999px;padding:2px 10px;"
        f'font-size:0.85em;font-weight:600;white-space:nowrap;">{label}</span>'
    )


def render_confidence_badge(confidence: str) -> None:
    """Render a colored confidence badge using markdown.

    Args:
        confidence: one of "high", "moderate", or "low".
    """
    color = CONFIDENCE_COLORS.get(confidence, COLOR_NEUTRAL)
    st.markdown(_pill(f"Confidence: {confidence}", color), unsafe_allow_html=True)


def render_method_assumptions(record: "PerturbationRecord") -> None:
    """Render all active method-assumption caveats as colored chips with expander detail.

    Green = no outstanding warnings beyond the universal chemokine caveat,
    yellow/red = warnings scaled by severity. The chemokine caveat is shown
    separately with an informational (non-warning) treatment, since it
    describes an orthogonal-data finding rather than a data-quality issue.

    Args:
        record: PerturbationRecord whose method_assumptions should be rendered.
    """
    flags = get_all_flags(record)

    non_universal = [f for f in flags if f["flag"] != "chemokine_signature_reliability"]
    chemokine_flag = next(
        (f for f in flags if f["flag"] == "chemokine_signature_reliability"), None
    )
    if not non_universal:
        st.markdown(
            _pill(
                "No outstanding method-assumption warnings", CONFIDENCE_COLORS["high"]
            ),
            unsafe_allow_html=True,
        )
    else:
        cols = st.columns(len(non_universal))
        for col, flag in zip(cols, non_universal):
            color = SEVERITY_COLORS.get(flag["severity"], COLOR_NEUTRAL)
            with col:
                st.markdown(
                    _pill(flag["flag"].replace("_", " "), color), unsafe_allow_html=True
                )

    for flag in non_universal:
        with st.expander(f"{flag['flag'].replace('_', ' ')} ({flag['severity']})"):
            st.markdown(flag["explanation"])

    if chemokine_flag is not None:
        st.markdown(
            _pill(
                "Chemokine signature: orthogonal-data caveat", SEVERITY_COLORS["info"]
            ),
            unsafe_allow_html=True,
        )
        with st.expander("Chemokine signature: orthogonal-data caveat"):
            st.markdown(chemokine_flag["explanation"])


def render_signature_bars(
    shifts: dict[str, dict],
    reliable_states: list[str],
    x_range: float | None = None,
    height: int = 450,
) -> go.Figure:
    """Render a horizontal bar chart of signature shifts centered at 0.

    Colors bars by direction (red = up, blue = down). Greys out unreliable states.
    Adds FDR significance stars as text annotations.

    Args:
        shifts: Dict keyed by state name with delta_pctl and fdr values.
        reliable_states: List of state keys that are considered reliable.
            Unreliable states are rendered in grey with a note.
        x_range: Optional symmetric x-axis half-width, so multiple charts can
            share the same scale (e.g. on the compare page).
        height: Chart height in pixels.

    Returns:
        Plotly Figure. Caller should render with st.plotly_chart(fig, config={"displaylogo": False}).
    """
    state_keys = [k for k in STATES if k in shifts]
    labels = [STATES[k]["display"] for k in state_keys]
    deltas = [shifts[k]["delta_pctl"] for k in state_keys]
    fdrs = [shifts[k]["fdr"] for k in state_keys]

    colors = []
    for k, d in zip(state_keys, deltas):
        if k not in reliable_states:
            colors.append(COLOR_MUTED)
        else:
            colors.append(COLOR_UP if d >= 0 else COLOR_DOWN)

    def _stars(fdr: float) -> str:
        if fdr < 0.001:
            return "***"
        if fdr < 0.01:
            return "**"
        if fdr < 0.05:
            return "*"
        return ""

    text = [_stars(f) for f in fdrs]

    fig = go.Figure(
        go.Bar(
            x=deltas,
            y=labels,
            orientation="h",
            marker_color=colors,
            text=text,
            textposition="outside",
        )
    )
    max_abs = (
        x_range if x_range is not None else max(1.0, max(abs(d) for d in deltas) * 1.3)
    )
    fig.update_layout(
        xaxis_title="Median Percentile Signature Score Shift Compared to NTC",
        xaxis_range=[-max_abs, max_abs],
        plot_bgcolor="white",
        paper_bgcolor="white",
        font={"color": CHART_FONT_COLOR},
        margin={"l": 30, "r": 30, "t": 30, "b": 50},
        height=height,
    )
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    fig.add_vline(x=0, line_color=COLOR_NEUTRAL, line_width=1)
    return fig


def render_functional_card(
    assay_name: str, readout: "FunctionalReadout | None"
) -> None:
    """Render a metric card for a single functional assay result.

    Shows: direction arrow (↑↓—), validated badge, n_wells.
    If not measured (or no readout exists for this assay), renders a greyed card
    with "not measured" label.

    Args:
        assay_name: Display name for the assay.
        readout: FunctionalReadout instance, or None if no data exists for this
            gene/model/assay combination.
    """
    if readout is None or readout.direction == "not_measured":
        st.markdown(
            f"**{assay_name}**\n\n<span style='color:{COLOR_NOT_MEASURED};'>— not measured</span>",
            unsafe_allow_html=True,
        )
        return

    arrow = _DIRECTION_ARROWS.get(readout.direction, "—")
    arrow_color = (
        COLOR_UP
        if readout.direction == "up"
        else COLOR_DOWN
        if readout.direction == "down"
        else COLOR_NEUTRAL
    )
    validated_pill = _pill(
        "validated" if readout.validated else "not validated",
        COLOR_SUCCESS if readout.validated else COLOR_DANGER,
    )
    st.markdown(
        f"**{assay_name}**\n\n"
        f"<span style='font-size:1.6em;color:{arrow_color};'>{arrow}</span> {validated_pill}",
        unsafe_allow_html=True,
    )
    if readout.n_wells is not None:
        st.caption(f"n_wells = {readout.n_wells}")


def render_discordance_box(discordances: list[dict]) -> None:
    """Render a warning box listing mRNA/protein direction discordances.

    Args:
        discordances: List of discordance dicts with keys: gene, mrna_direction,
            protein_direction, likely_cause.
    """
    if not discordances:
        return
    lines = [
        f"- **{d['gene']}**: mRNA {d['mrna_direction']} vs protein {d['protein_direction']} "
        f"— likely cause: {d['likely_cause']}"
        for d in discordances
    ]
    st.warning("mRNA/protein discordance detected:\n\n" + "\n".join(lines))


def render_gene_header(record: "PerturbationRecord") -> None:
    """Render the full gene info header: a 3x2 metric grid plus badges.

    Grid (left): Cells, Percent knockdown, Num guides, Mean NTC expression,
    Frac NTC expressing, Knockdown source.
    Tags (right): confidence badge, Mixscale response badge.

    Args:
        record: Validated PerturbationRecord.
    """
    st.markdown(f"### {record.perturbation}: {record.cell_model}")

    kd_detail = record.prediction_targets.get("percent_knockdown_detail", {})
    num_guides = kd_detail.get("num_guides")
    ntc_mean_expr = kd_detail.get("ntc_mean_expression")
    ntc_frac_expr = kd_detail.get("ntc_fraction_expressing")
    kd_source_label = _KD_SOURCE_LABELS.get(kd_detail.get("source"), "—")

    grid_col, tags_col = st.columns([3, 1])

    with grid_col:
        row1 = st.columns(3)
        with row1[0]:
            st.metric("Cells", record.n_cells)
        with row1[1]:
            st.metric(
                "Percent knockdown",
                f"{record.percent_knockdown:.0f}%"
                if record.percent_knockdown is not None
                else "Not measured",
            )
        with row1[2]:
            st.metric("Number of guides", num_guides if num_guides is not None else "—")

        row2 = st.columns(3)
        with row2[0]:
            st.metric(
                "Mean NTC expression of target gene",
                f"{ntc_mean_expr:.2f}" if ntc_mean_expr is not None else "—",
            )
        with row2[1]:
            st.metric(
                "Fraction of NTC cells expressing target gene",
                f"{ntc_frac_expr:.0%}" if ntc_frac_expr is not None else "—",
            )
        with row2[2]:
            st.metric("Knockdown source", kd_source_label)

    with tags_col:
        render_confidence_badge(record.confidence)
        st.markdown(
            _pill(f"Response: {record.mixscale_response}", COLOR_RESPONSE_BADGE),
            unsafe_allow_html=True,
        )


def render_static_image(
    path: "Path | None",
    caption: str,
    height: int | None = None,
    width: int | None = None,
    to_crop: bool | None = False,
) -> None:
    """Render a static image if present, otherwise a caption noting its absence.

    Args:
        path: Path to the image file, or None if it wasn't found on disk.
        caption: Label used both as the image caption and the "not available" note.
        height: Optional fixed pixel height, so the image panel can be sized to match
            a paired Plotly chart. If None, the image renders at its natural aspect
            ratio scaled to the container width.
        width: Optional fixed pixel width. Only used when `height` is also set;
            defaults to filling the container width.
        to_crop: Optional parameter to crop static image.
    """

    if not to_crop:
        image_input = str(path)
    else:
        img = Image.open(str(path))
        # Cropping Size
        w, h = img.size
        crop_box = (w * 0.02, h * 0.09, w * 0.95, h * 0.95)
        cropped_img = img.crop(crop_box)
        image_input = cropped_img

    if path is None:
        st.caption(f"{caption} not available")
        return
    if height is None:
        st.image(image_input, caption=caption, width="stretch")
        return
    with st.container(height=height):
        if width is not None:
            st.image(image_input, caption=caption, width=width)
        else:
            st.image(image_input, caption=caption, width="stretch")


def render_volcano_legend(states: list[str], protein: bool = False) -> None:
    """Render a boxed color-swatch legend for a volcano plot's state-signature colors.

    Args:
        states: State keys (from RNA_VOLCANO_COLORS/STATES) to include, in order.
        protein: If True, labels genes as protein-abundance correlations rather
            than RNA state-signature membership.
    """
    title = "Protein abundance correlation" if protein else "State signature genes"
    n_cols = 2 if protein else 3

    st.markdown(f"**{title}**")
    for row_start in range(0, len(states), n_cols):
        row_states = states[row_start : row_start + n_cols]
        cols = st.columns(n_cols)
        for col, state in zip(cols, row_states):
            color = RNA_VOLCANO_COLORS.get(state, COLOR_NEUTRAL)
            display = STATES.get(state, {}).get("display", state)
            label = (
                f"Protein abundance correlated with RNA-derived {display} signature"
                if protein
                else display
            )
            col.markdown(
                f"{_nutrition_indicator(color)} {label}", unsafe_allow_html=True
            )


def render_factor_bars(factors: dict[str, dict], top_n: int = 10) -> go.Figure:
    """Render a horizontal bar chart of the most-shifted scHPF factors.

    Mirrors render_signature_bars's layout, but for the larger scHPF factor set:
    takes the top `top_n` factors by absolute delta_pctl instead of a fixed state list.

    Args:
        factors: Dict keyed by factor code/label with delta_pctl, fdr, label values.
        top_n: Number of top-shifted factors to include.

    Returns:
        Plotly Figure. Caller should render with st.plotly_chart(fig, config={"displaylogo": False}).
    """
    top_items = sorted(
        factors.items(), key=lambda kv: abs(kv[1]["delta_pctl"]), reverse=True
    )[:top_n]
    top_items = sorted(top_items, key=lambda kv: kv[1]["delta_pctl"])

    labels = [v.get("label", k) for k, v in top_items]
    deltas = [v["delta_pctl"] for _, v in top_items]
    fdrs = [v["fdr"] for _, v in top_items]
    colors = [COLOR_UP if d >= 0 else COLOR_DOWN for d in deltas]

    def _stars(fdr: float) -> str:
        if fdr < 0.001:
            return "***"
        if fdr < 0.01:
            return "**"
        if fdr < 0.05:
            return "*"
        return ""

    fig = go.Figure(
        go.Bar(
            x=deltas,
            y=labels,
            orientation="h",
            marker_color=colors,
            text=[_stars(f) for f in fdrs],
            textposition="outside",
        )
    )
    max_abs = max(1.0, max(abs(d) for d in deltas) * 1.3)
    fig.update_layout(
        xaxis_title="Median Percentile Signature Score Shift Compared to NTC",
        xaxis_range=[-max_abs, max_abs],
        plot_bgcolor="white",
        paper_bgcolor="white",
        font={"color": CHART_FONT_COLOR},
        margin={"l": 30, "r": 30, "t": 30, "b": 50},
        height=max(600, 32 * len(labels)),
    )
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    fig.add_vline(x=0, line_color=COLOR_NEUTRAL, line_width=1)
    return fig


def render_multistate_heatmap(
    records: list["PerturbationRecord"],
    model: str,
    highlight_genes: dict[str, str] | None = None,
) -> go.Figure:
    """Build a plotly heatmap of all genes × 6 states, colored by delta_pctl.

    Args:
        records: List of all perturbation records (filtered to one model).
        model: Cell model name, used for title.
        highlight_genes: Optional {gene: hex_color} map. Matching genes get their
            row label colored and boxed with the given color.

    Returns:
        Plotly Figure. Pass to st.plotly_chart with config={"displaylogo": False}.
    """
    model_records = sorted(
        (r for r in records if r.cell_model == model), key=lambda r: r.perturbation
    )
    state_keys = list(STATES.keys())
    labels = [STATES[k]["display"] for k in state_keys]
    genes = [r.perturbation for r in model_records]
    highlight_genes = highlight_genes or {}

    z = [
        [r.prediction_targets["signature_shift"][k]["delta_pctl"] for k in state_keys]
        for r in model_records
    ]

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=labels,
            y=genes,
            colorscale="RdBu",
            reversescale=True,
            zmid=0,
            zmin=-20,
            zmax=20,
            colorbar={
                "title": {
                    "text": "Median Percentile Signature Score Shift Compared to NTC",
                    "side": "right",
                }
            },
        ),
    )
    fig.update_layout(
        xaxis_title="Signature",
        yaxis_title="Gene Knockdown",
    )

    if highlight_genes:
        ticktext = [
            f"<b><span style='color:{highlight_genes[g]}'>{g}</span></b>"
            if g in highlight_genes
            else g
            for g in genes
        ]
        fig.update_yaxes(tickmode="array", tickvals=genes, ticktext=ticktext)
        for row_index, gene in enumerate(genes):
            if gene in highlight_genes:
                fig.add_shape(
                    type="rect",
                    x0=-0.5,
                    x1=len(state_keys) - 0.5,
                    y0=row_index - 0.5,
                    y1=row_index + 0.5,
                    line={"color": highlight_genes[gene], "width": 2},
                    fillcolor="rgba(0,0,0,0)",
                )

    fig.update_layout(
        title=f"Median Percentile Signature Score Shift: {model}",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font={"color": CHART_FONT_COLOR},
        margin={"l": 40, "r": 130, "t": 60, "b": 70},
        height=max(700, 18 * len(genes)),
    )
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    return fig


def _nutrition_indicator(color: str) -> str:
    """Return a small colored dot as markdown/HTML."""
    return f'<span style="color:{color}; font-size:1.1em;">&#9679;</span>'


def _nutrition_row(st, label: str, value: object, color: str) -> None:
    """Render one key-value line with a colored indicator."""
    c1, c2, c3 = st.columns([2, 1, 1])
    c1.markdown(str(label))
    c2.markdown(str(value))
    c3.markdown(_nutrition_indicator(color), unsafe_allow_html=True)


def render_nutrition_label(label: dict) -> None:
    """Render the nutrition label as a Streamlit 2×2 grid of metric cards.

    Each metric is shown as a key-value row with a colored indicator:
    green (good), yellow (warning), red (limitation).

    Args:
        label: Dict from compute_nutrition_label or loaded from nutrition_label.json.
    """
    coverage = label.get("coverage")
    quality = label.get("perturbation_quality")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Coverage")
        if coverage is None:
            st.caption("Coverage not included in this label.")
        else:
            _nutrition_row(st, "Total KDs", coverage["total_kds"], GREEN)
            _nutrition_row(
                st, "Median cells per KD", coverage["median_cells_per_kd"], GREEN
            )
            _nutrition_row(st, "Min cells per KD", coverage["min_cells_per_kd"], GREEN)
            _nutrition_row(
                st,
                "States profiled",
                coverage["states_profiled"],
                GREEN,
            )
            _nutrition_row(
                st,
                "Reliable states",
                coverage["reliable_states"],
                YELLOW
                if coverage["reliable_states"] < coverage["states_profiled"]
                else GREEN,
            )
            _nutrition_row(
                st, "Proteins measured", coverage["proteins_measured"], GREEN
            )

    with col2:
        st.markdown("### Perturbation quality")
        if quality is None:
            st.caption("Perturbation quality not included in this label.")
        else:
            median_pk = quality["median_percent_knockdown"]
            _nutrition_row(
                st,
                "Median percent knockdown",
                f"{median_pk:.0f}%" if median_pk is not None else "Not measured",
                GREEN,
            )
            _nutrition_row(
                st,
                "N with weak knockdown",
                quality["n_efficiency_below_threshold"],
                YELLOW if quality["n_efficiency_below_threshold"] > 0 else GREEN,
            )
            _nutrition_row(st, "N binary response", quality["n_binary_response"], GREEN)
            _nutrition_row(st, "N graded response", quality["n_graded_response"], GREEN)
            _nutrition_row(
                st,
                "N with orthogonal characterization",
                quality["n_with_orthogonal_characterization"],
                YELLOW if quality["n_with_orthogonal_characterization"] == 0 else GREEN,
            )
            _nutrition_row(
                st,
                "N low cell count",
                quality["n_low_cell_count"],
                YELLOW if quality["n_low_cell_count"] > 0 else GREEN,
            )
