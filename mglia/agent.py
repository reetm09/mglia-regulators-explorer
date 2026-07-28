"""Agent-facing helper functions — thin wrappers used by both the MCP server and the agent Streamlit page."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from mglia.constants import ALL_KD_GENES, GLOSSARY_BLURBS, SCHPF_FACTOR_LABELS, STATES
from mglia.dataset_config import REPO_ROOT
from mglia.method_assumptions import ASSUMPTION_REGISTRY
from mglia.schema import validate_all_records

RECORDS_PATH = REPO_ROOT / "data" / "perturbations.json"


@lru_cache(maxsize=1)
def _load_records():
    """Load and validate every record in data/perturbations.json, once per process.

    Returns:
        List of validated PerturbationRecord instances.

    Raises:
        FileNotFoundError: If data/perturbations.json does not exist yet
            (run `python scripts/generate_records.py` first).
    """
    return validate_all_records(RECORDS_PATH)


def get_perturbation(gene: str, model: str | None = None) -> dict[str, Any]:
    """Return the full perturbation record for a knockdown gene in a cell model.

    Reads from data/perturbations.json. Does not load h5mu files.

    Args:
        gene: Target gene name (e.g. 'ZNF532'). Must be one of the 31 KD genes.
        model: Cell model name — 'iTF-MG' or 'iMG'. If omitted, or if it does not
            match any record for this gene, this returns a clarification dict
            instead of raising (see Returns).
    Returns:
        If `model` is a valid match: the full PerturbationRecord as a
        JSON-serializable dict including signature shifts, top DEGs, scHPF
        factors, functional readouts, and method assumption audit flags.

        If `model` is omitted or does not match any record for this gene: a
        clarification dict of the form
        `{"status": "needs_clarification", "question": str, "param": "model", "options": list[str]}`
        listing the cell models this gene actually has
        data for. Callers should surface `question` to the user and re-call
        with one of `options`.

    Raises:
        FileNotFoundError: If data/perturbations.json does not exist yet
            (run `python scripts/generate_records.py` first).
        KeyError: If `gene` has no records in any cell model.
    """
    matches = [record for record in _load_records() if record.perturbation == gene]
    if not matches:
        raise KeyError(f"No perturbation record found for gene={gene!r}")

    if model is not None:
        for record in matches:
            if record.cell_model == model:
                return record.model_dump()

    options = sorted({record.cell_model for record in matches})
    return {
        "status": "needs_clarification",
        "question": f"Which cell model should I use for {gene}?",
        "param": "model",
        "options": options,
    }


def list_genes() -> list[str]:
    """Return all knockdown gene names available in the dataset.

    Returns:
        Sorted list of all 31 KD gene names.
    """
    return sorted(ALL_KD_GENES)


def get_glossary() -> dict[str, Any]:
    """Return static reference definitions for dataset concepts.

    Consolidates definitions that are otherwise scattered across constants.py,
    method_assumptions.py, and the Streamlit UI copy, so both the MCP server and
    the Streamlit pages can read from a single source of truth.

    Returns:
        Dict with three keys:
        - "states": mglia.constants.STATES — per-state display name, marker,
          reliability, and reliability_note where applicable.
        - "schpf": {"description": str, "factor_labels": dict[str, str],
          "methodology": dict} — scHPF blurb, factor code -> label mapping, and
          the "schpf_projection" entry from ASSUMPTION_REGISTRY explaining how
          factor labels are derived and their known limitations.
        - "method_assumptions": {"description": str, "registry": dict} — method
          assumptions blurb plus the full ASSUMPTION_REGISTRY (assumptions,
          violation conditions, and severity per method).
        - "mixscale": {"descriotion": str} - explainer of how and why Mixscale
            was used to calculate differentially expressed genes (DEGs) and
            differentially abundant proteins (DAPs) in this paper.
        - "nutrition_label": {"description": str} - explainer of nutrition label
            in this dataset to improve transparency and why it was designed this way.
    """
    return {
        "states": STATES,
        "schpf": {
            "description": GLOSSARY_BLURBS["schpf_factors"],
            "factor_labels": SCHPF_FACTOR_LABELS,
            "methodology": ASSUMPTION_REGISTRY["schpf_projection"],
        },
        "method_assumptions": {
            "description": GLOSSARY_BLURBS["method_assumptions"],
            "registry": ASSUMPTION_REGISTRY,
        },
        "mixscale": {"description": GLOSSARY_BLURBS["mixscale_degs"]},
        "nutrition_label": {"description": GLOSSARY_BLURBS["nutrition_label"]},
    }


def list_tasks() -> list[str]:
    """Return all available benchmark task names.

    Returns:
        List of task name strings.
    """
    raise NotImplementedError
