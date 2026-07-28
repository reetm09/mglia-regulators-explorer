"""Cached loading and lookup of PerturbationRecord data for dashboard and MCP."""

from __future__ import annotations

import streamlit as st

from mglia.constants import ALL_KD_GENES
from mglia.dataset_config import REPO_ROOT
from mglia.schema import PerturbationRecord, validate_all_records

RECORDS_PATH = REPO_ROOT / "data" / "perturbations.json"


@st.cache_data
def load_all_records() -> list[PerturbationRecord]:
    """Load and validate every record in data/perturbations.json.

    Returns:
        List of validated PerturbationRecord instances.
    """
    return validate_all_records(RECORDS_PATH)


def get_record(gene: str, model: str) -> PerturbationRecord | None:
    """Look up a single record by gene and cell model.

    Args:
        gene: Perturbation target gene name.
        model: Cell model name ("iTF-MG" or "iMG").

    Returns:
        The matching PerturbationRecord, or None if no record matches.
    """
    for record in load_all_records():
        if record.perturbation == gene and record.cell_model == model:
            return record
    return None


def list_genes() -> list[str]:
    """Return the full 31-gene knockdown panel, sorted for display.

    Returns:
        Sorted list of gene symbols.
    """
    return sorted(ALL_KD_GENES)
