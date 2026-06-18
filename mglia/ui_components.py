"""Reusable Streamlit UI components for the mglia explorer."""

from __future__ import annotations

from typing import TYPE_CHECKING

import plotly.graph_objects as go

if TYPE_CHECKING:
    from mglia.schema import AssumptionAudit, FunctionalReadout, PerturbationRecord


def render_confidence_badge(confidence: str) -> None:
    """Render a colored confidence badge using markdown.

    Args:
        confidence: One of "high", "moderate", or "low".
    """
    raise NotImplementedError


def render_assumption_flags(audit: "AssumptionAudit") -> None:
    """Render all active assumption flags as colored chips with expander detail.

    Green = no flags, yellow = warnings, red = serious flags.
    Each chip expands to show the full assumption description and violation condition.

    Args:
        audit: AssumptionAudit from a PerturbationRecord.
    """
    raise NotImplementedError


def render_signature_bars(
    shifts: dict[str, dict],
    reliable_states: list[str],
) -> None:
    """Render a horizontal bar chart of signature shifts centered at 0.

    Colors bars by direction (red = up, blue = down). Greys out unreliable states.
    Adds FDR significance stars as text annotations.

    Args:
        shifts: Dict keyed by state name with delta_pctl and fdr values.
        reliable_states: List of state keys that are considered reliable.
            Unreliable states are rendered in grey with a note.
    """
    raise NotImplementedError


def render_functional_card(assay_name: str, readout: "FunctionalReadout") -> None:
    """Render a metric card for a single functional assay result.

    Shows: direction arrow (↑↓—), validated badge, n_wells.
    If not measured, renders a greyed card with "not measured" label.

    Args:
        assay_name: Display name for the assay.
        readout: FunctionalReadout instance.
    """
    raise NotImplementedError


def render_discordance_box(discordances: list[dict]) -> None:
    """Render a warning box listing mRNA/protein direction discordances.

    Args:
        discordances: List of discordance dicts with keys: gene, mrna_direction,
            protein_direction, likely_cause.
    """
    raise NotImplementedError


def render_gene_header(record: "PerturbationRecord") -> None:
    """Render the full gene info header with all metadata badges.

    Shows: gene name, KD efficiency, n_cells, confidence badge,
    benchmark split badge, Mixscale response type.

    Args:
        record: Validated PerturbationRecord.
    """
    raise NotImplementedError


def render_multistate_heatmap(
    records: list["PerturbationRecord"],
    model: str,
) -> go.Figure:
    """Build a plotly heatmap of all genes × 6 states, colored by delta_pctl.

    Args:
        records: List of all perturbation records (filtered to one model).
        model: Cell model name, used for title.

    Returns:
        Plotly Figure. Pass to st.plotly_chart with config={"displaylogo": False}.
    """
    raise NotImplementedError
