"""Load MuData objects and extract per-perturbation subsets."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    import mudata
    from anndata import AnnData

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"


def load_mdata(model: str) -> "mudata.MuData":
    """Load the MuData object for a given cell model.

    Args:
        model: One of "iTF-MG" or "iMG".

    Returns:
        MuData object with 'rna' and 'prot' modalities.

    Raises:
        FileNotFoundError: If the .h5mu file is not found in data/raw/.
            Error message includes download instructions.
        ValueError: If model name is not recognised.
    """
    raise NotImplementedError


def get_rna(mdata: "mudata.MuData") -> "AnnData":
    """Extract the RNA modality from a MuData object.

    Args:
        mdata: Loaded MuData object.

    Returns:
        AnnData view of mdata['rna'].
    """
    raise NotImplementedError


def get_prot(mdata: "mudata.MuData") -> "AnnData":
    """Extract the protein modality from a MuData object.

    Args:
        mdata: Loaded MuData object.

    Returns:
        AnnData view of mdata['prot'].
    """
    raise NotImplementedError


def get_perturbation_cells(mdata: "mudata.MuData", gene: str) -> "AnnData":
    """Subset the RNA modality to cells assigned to a specific sgRNA target.

    Args:
        mdata: Loaded MuData object.
        gene: Target gene name (must match values in rna.obs['perturbed_gene']).

    Returns:
        AnnData subset containing only cells where perturbed_gene == gene.

    Raises:
        KeyError: If perturbed_gene column is missing.
        ValueError: If gene not found in the dataset.
    """
    raise NotImplementedError


def get_ntc_cells(mdata: "mudata.MuData") -> "AnnData":
    """Return non-targeting control cells from the RNA modality.

    Args:
        mdata: Loaded MuData object.

    Returns:
        AnnData subset where perturbed_gene == 'NTC'.
    """
    raise NotImplementedError


def get_mixscale_scores(mdata: "mudata.MuData", gene: str) -> pd.Series:
    """Return per-cell Mixscale scores for a given knockdown.

    Args:
        mdata: Loaded MuData object.
        gene: Target gene name.

    Returns:
        Series of Mixscale scores indexed by cell barcode.

    Raises:
        KeyError: If 'mixscale_score' column is missing from rna.obs.
        ValueError: If gene not found.
    """
    raise NotImplementedError


def get_signature_scores(mdata: "mudata.MuData", gene: str) -> pd.DataFrame:
    """Return per-cell UCell scores for all 6 states for a given knockdown.

    Args:
        mdata: Loaded MuData object.
        gene: Target gene name.

    Returns:
        DataFrame (cells × states) of UCell scores.
        Columns are the canonical state keys from constants.STATES.
    """
    raise NotImplementedError


def get_schpf_factors(mdata: "mudata.MuData", gene: str) -> pd.DataFrame:
    """Return per-cell scHPF factor scores for a given knockdown.

    Args:
        mdata: Loaded MuData object.
        gene: Target gene name.

    Returns:
        DataFrame (cells × factors) with columns matching constants.SCHPF_FACTORS.
    """
    raise NotImplementedError


def check_mdata_schema(mdata: "mudata.MuData") -> dict[str, list[str]]:
    """Validate that all required obs columns are present in the MuData object.

    Checks rna.obs for: perturbed_gene, guide, mixscale_score,
    all scHPF factor columns, and all UCell score columns.

    Args:
        mdata: Loaded MuData object.

    Returns:
        Dict with keys 'missing_critical' and 'missing_optional',
        each a list of column names. Empty lists mean schema is valid.
    """
    raise NotImplementedError
