"""Statistical computations: signature shifts, DEGs, Mixscale stratification."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    import mudata
    from anndata import AnnData


def compute_signature_shifts(
    mdata: "mudata.MuData",
    gene: str,
    model: str,
) -> dict[str, dict]:
    """Compute median percentile shift per state for a knockdown vs NTC.

    Uses Mann-Whitney U test with BH FDR correction across states.

    Args:
        mdata: Loaded MuData object.
        gene: Target gene name.
        model: Cell model name ("iTF-MG" or "iMG"), used for logging only.

    Returns:
        Dict keyed by state name (from constants.STATES). Each value is a dict
        with keys: delta_pctl (float), p_value (float), fdr (float), reliable (bool).
    """
    raise NotImplementedError


def compute_deg_list(
    mdata: "mudata.MuData",
    gene: str,
    model: str,
    top_n: int = 50,
) -> dict[str, list[str] | int]:
    """Return top N positive and negative DEGs from Mixscale-weighted analysis.

    Uses precomputed DEGs from mdata['rna'].uns if available; otherwise computes.

    Args:
        mdata: Loaded MuData object.
        gene: Target gene name.
        model: Cell model name.
        top_n: Number of top DEGs to return per direction.

    Returns:
        Dict with keys: top_positive (list[str]), top_negative (list[str]),
        n_positive (int), n_negative (int), assumption_flags (list[str]).
    """
    raise NotImplementedError


def stratify_by_mixscale(
    mdata: "mudata.MuData",
    gene: str,
) -> dict[str, "AnnData | int"]:
    """Split KD cells into thirds by Mixscale score.

    Args:
        mdata: Loaded MuData object.
        gene: Target gene name.

    Returns:
        Dict with keys: bottom (AnnData), middle (AnnData), top (AnnData),
        n_bottom (int), n_middle (int), n_top (int).
    """
    raise NotImplementedError


def classify_mixscale_response(gene: str) -> str:
    """Return the Mixscale response type for a gene from constants.

    Args:
        gene: Target gene name.

    Returns:
        One of "binary", "graded", or "unknown". Falls back to "unknown"
        if gene is not in MIXSCALE_RESPONSE_TYPE.
    """
    raise NotImplementedError


def compute_protein_correlation(
    mdata: "mudata.MuData",
    state: str,
) -> pd.DataFrame:
    """Compute Pearson correlation of each CITE-seq protein with a state's UCell score.

    Args:
        mdata: Loaded MuData object.
        state: State key from constants.STATES.

    Returns:
        DataFrame sorted by |correlation|, columns: protein, correlation, p_value.
    """
    raise NotImplementedError


def compute_confidence(n_cells: int, kd_efficiency: float | None) -> str:
    """Compute confidence tier for a knockdown record.

    Rules:
        high:     n_cells > 200 and kd_efficiency > 0.6
        moderate: n_cells > 100 and kd_efficiency > 0.4
        low:      otherwise

    Args:
        n_cells: Number of cells assigned to this KD.
        kd_efficiency: RT-qPCR knockdown efficiency (fraction, 0–1). None = unknown.

    Returns:
        One of "high", "moderate", or "low".
    """
    raise NotImplementedError


def compute_nutrition_scores(records: list[dict]) -> dict:
    """Aggregate quality metrics across all perturbation records.

    Args:
        records: List of raw record dicts loaded from perturbations.json.

    Returns:
        Dict matching the NutritionLabel schema structure.
    """
    raise NotImplementedError
