"""Agent-facing helper functions — thin wrappers used by both the MCP server and the agent Streamlit page."""

from __future__ import annotations

from typing import Any


def get_perturbation(gene: str, model: str) -> dict[str, Any]:
    """Return the full perturbation record for a knockdown gene in a cell model.

    Reads from data/perturbations.json (pre-generated). Does not load h5mu files.

    Args:
        gene: Target gene name (e.g. 'ZNF532'). Must be one of the 31 KD genes.
        model: Cell model name — 'iTF-MG' or 'iMG'.

    Returns:
        Full PerturbationRecord as a JSON-serializable dict including signature shifts,
        top DEGs, scHPF factors, functional readouts, and assumption audit flags.

    Raises:
        FileNotFoundError: If data/perturbations.json does not exist yet
            (run `make generate` first).
        KeyError: If the gene + model combination is not found.
    """
    raise NotImplementedError


def list_genes() -> list[str]:
    """Return all knockdown gene names available in the dataset.

    Returns:
        Sorted list of all 31 KD gene names.
    """
    raise NotImplementedError


def list_tasks() -> list[str]:
    """Return all available benchmark task names.

    Returns:
        List of task name strings.
    """
    raise NotImplementedError
