"""Method assumptions registry and per-record caveat-building logic."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mglia.constants import MODEL_DIVERGENT_GENES, STATES

if TYPE_CHECKING:
    from mglia.schema import MethodAssumptions, PerturbationRecord

# ---------------------------------------------------------------------------
# Method assumptions registry
# ---------------------------------------------------------------------------

ASSUMPTION_REGISTRY: dict[str, dict[str, Any]] = {
    "mixscale_scoring": {
        "assumptions": [
            "Mixscale scores are computed per-guide and combined at gene-level",
            "relative to non-targeting control (NTC) cells and assume CRISPRi in comparison",
            "to CRISPR-knockout have cells exhibit a quantitative gradient of responses",
            "consistent with multiple factors that influence variable efficiency of CRISPRi knockdown",
            "(Jiang, 2025). Thus, they replace binarized classification with a continuous scalar value",
            "that reflects the strength of perturbation. ",
            "Binary vs. graded response classification for each perturbation in nutrition_report is inferred from the shape "
            "of the per-cell Mixscale score distribution (bimodality coefficient), ",
        ],
        "violation_conditions": [
            "Fewer than 10 cells assigned to a knockdown makes distribution-shape binary/graded "
            "classification unreliable.",
        ],
        "severity": "moderate",
    },
    "ucell_signature": {
        "assumptions": [
            "UCell signature scores summarize a literature curated gene set into a single per-cell "
            "score and assume the underlying gene set is complete and specific "
            "to the state it represents.",
        ],
        "violation_conditions": [
            "A state's signature gene set was derived from a small number of "
            "validation hits and inconclusive literature results, and may be incomplete.",
        ],
        "severity": "mild",
    },
    "weighted_deg": {
        "assumptions": [
            "DEG lists are computed vs. NTC cells within the same cell model and "
            "assume perturbation strength (mixscale score) should be accounted in calculation",
        ],
        "violation_conditions": [
            "Too few number of cells per knockdown decreases statistical power to call DEGS.",
            "Fewer than the requested top_n genes are significant (FDR < 0.05) "
            "in a given direction.",
        ],
        "severity": "mild",
    },
    "schpf_projection": {
        "assumptions": [
            "scHPF factors are latent and their biological interpretation (label) "
            "is assigned post-hoc based on marker gene loadings from (Marshe et al, bioRxiv 2025).",
            "Projection onto iPSC-model still covers entire factor space.",
        ],
        "violation_conditions": [
            "The iPSC-derived model may not cover the same factor subspace as primary human "
            "microglia, which can lead to inconsistent factor coverage and interpretation.",
        ],
        "severity": "mild",
    },
    "cite_seq_protein": {
        "assumptions": [
            "CITE-seq antibody signal is assumed to be specific and linear within "
            "the measured range. The antibody panel used here has been validated.",
        ],
        "violation_conditions": [
            "A different panel may have better resolution for a given protein.",
        ],
        "severity": "mild",
    },
    "phagocytosis_assay": {
        "assumptions": [
            "Functional readouts are bulk/population-level, not single-cell, and "
            "assume the sgRNA population is homogeneous with respect to knockdown.",
        ],
        "violation_conditions": [
            "The assay was not run for a given gene (not_measured).",
        ],
        "severity": "mild",
    },
    "cross_model_comparison": {
        "assumptions": [
            "iTF-MG and iMG are assumed to model the same biological knockdown "
            "response despite different differentiation protocols and timelines.",
        ],
        "violation_conditions": [
            "A gene is known to produce divergent effects across the two models "
            "(see constants.MODEL_DIVERGENT_GENES).",
        ],
        "severity": "strong",
    },
}


# ---------------------------------------------------------------------------
# Method assumptions builder
# ---------------------------------------------------------------------------
def build_method_assumptions(
    gene: str,
    model: str,
    n_cells: int,
    percent_knockdown: float | None,
    model_consistent: bool,
    percent_knockdown_source: str = "measured_rtqpcr",
) -> "MethodAssumptions":
    """Build the method-assumptions caveats for a single perturbation record.

    Args:
        gene: Target gene name
        model: Cell model name
        n_cells: Number of cells assigned to this KD
        percent_knockdown: Percent knockdown, 0-100. None if not measured.
        model_consistent: Whether effects are consistent across iTF-MG and iMG.
        percent_knockdown_source: "measured_rtqpcr" or "measured_transcriptomic" if
            percent_knockdown is a real measured value, "not_measured" if the gene
            has no usable value from either source.

    Returns:
        MethodAssumptions with all flags populated.
    """
    from mglia.schema import MethodAssumptions

    low_cell_count_warning = n_cells < 100
    # percent_knockdown is 0-100 (0 = no knockdown, 100 = complete knockdown), so a
    # LOW value is a weak/failed knockdown and warrants a warning.
    percent_knockdown_warning = percent_knockdown is None or percent_knockdown < 20
    model_specific_effects = gene in MODEL_DIVERGENT_GENES or not model_consistent

    flags: list[str] = []
    if low_cell_count_warning:
        flags.append(f"Low cell count for {gene} in {model} (n={n_cells} < 100)")
    if percent_knockdown_source == "not_measured" or percent_knockdown is None:
        flags.append(f"Knockdown efficiency for {gene} was not measured")
    elif percent_knockdown_warning:
        flags.append(
            f"Percent knockdown for {gene} is below 20% ({percent_knockdown:.0f}%), "
            "indicating a weak knockdown"
        )
    if model_specific_effects:
        flags.append(f"{gene} has known or suspected model-specific effects")
    flags.append(STATES["chemokine"]["reliability_note"])

    return MethodAssumptions(
        low_cell_count_warning=low_cell_count_warning,
        percent_knockdown_warning=percent_knockdown_warning,
        model_specific_effects=model_specific_effects,
        chemokine_signature_reliability="low",
        flags=flags,
    )


def get_assumption_explanation(method: str) -> dict[str, Any]:
    """Return the full assumption list and violation conditions for a method.

    Used by the UI to render tooltips.

    Args:
        method: Key in ASSUMPTION_REGISTRY.

    Returns:
        Dict with keys: assumptions (list[str]), violation_conditions (list[str]),
        severity (str).

    Raises:
        KeyError: If method is not in ASSUMPTION_REGISTRY.
    """
    return ASSUMPTION_REGISTRY[method]


def get_all_flags(record: "PerturbationRecord") -> list[dict[str, Any]]:
    """Return all active method-assumption caveats for a record with severity and explanation.

    Used to render the method assumptions & caveats UI component.

    Args:
        record: Validated PerturbationRecord.

    Returns:
        List of dicts, each with keys: flag (str), severity (str), explanation (str).
        Empty list if no flags are active.
    """
    audit = record.method_assumptions
    results: list[dict[str, Any]] = []

    flag_to_method = {
        "low_cell_count_warning": "weighted_deg",
        "percent_knockdown_warning": "mixscale_scoring",
        "model_specific_effects": "cross_model_comparison",
    }

    for flag_name, method in flag_to_method.items():
        if getattr(audit, flag_name):
            explanation = ASSUMPTION_REGISTRY.get(method, {})
            results.append(
                {
                    "flag": flag_name,
                    "severity": explanation.get("severity", "mild"),
                    "explanation": "; ".join(explanation.get("assumptions", [])),
                }
            )

    if audit.chemokine_signature_reliability == "low":
        explanation = ASSUMPTION_REGISTRY.get("ucell_signature", {})
        results.append(
            {
                "flag": "chemokine_signature_reliability",
                "severity": "info",
                "explanation": STATES["chemokine"]["reliability_note"],
            }
        )

    return results
