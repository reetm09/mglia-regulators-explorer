"""Assumption registry and per-record audit logic."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mglia.schema import AssumptionAudit, PerturbationRecord

# ---------------------------------------------------------------------------
# Assumption registry
# ---------------------------------------------------------------------------

ASSUMPTION_REGISTRY: dict[str, dict[str, Any]] = {
    "mixscale_scoring": {
        "assumptions": [
            # TODO: fill from paper methods
        ],
        "violation_conditions": [
            # TODO
        ],
        "severity": "moderate",
    },
    "ucell_signature": {
        "assumptions": [],
        "violation_conditions": [],
        "severity": "mild",
    },
    "weighted_deg": {
        "assumptions": [],
        "violation_conditions": [],
        "severity": "moderate",
    },
    "schpf_projection": {
        "assumptions": [],
        "violation_conditions": [],
        "severity": "mild",
    },
    "cite_seq_protein": {
        "assumptions": [],
        "violation_conditions": [],
        "severity": "moderate",
    },
    "phagocytosis_assay": {
        "assumptions": [],
        "violation_conditions": [],
        "severity": "mild",
    },
    "cross_model_comparison": {
        "assumptions": [],
        "violation_conditions": [],
        "severity": "strong",
    },
}


# ---------------------------------------------------------------------------
# Audit functions
# ---------------------------------------------------------------------------


def audit_record(
    gene: str,
    model: str,
    n_cells: int,
    kd_efficiency: float | None,
    has_antibody_validation: bool,
    model_consistent: bool,
) -> "AssumptionAudit":
    """Run assumption audit for a single perturbation record.

    Args:
        gene: Target gene name.
        model: Cell model name.
        n_cells: Number of cells assigned to this KD.
        kd_efficiency: RT-qPCR efficiency (fraction, 0–1). None if unknown.
        has_antibody_validation: Whether CITE-seq antibodies are validated for this gene.
        model_consistent: Whether effects are consistent across iTF-MG and iMG.

    Returns:
        AssumptionAudit with all flags populated.
    """
    raise NotImplementedError


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
    raise NotImplementedError


def get_all_flags(record: "PerturbationRecord") -> list[dict[str, Any]]:
    """Return all active assumption flags for a record with severity and explanation.

    Used to render the assumption audit UI component.

    Args:
        record: Validated PerturbationRecord.

    Returns:
        List of dicts, each with keys: flag (str), severity (str), explanation (str).
        Empty list if no flags are active.
    """
    raise NotImplementedError
