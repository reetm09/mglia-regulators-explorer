"""Dataset nutrition label: compute label and export JSON."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Literal

from mglia import constants, nutrition_report
from mglia.dataset_config import REPO_ROOT
from mglia.schema import (
    NutritionLabel,
    NutritionLabelCoverage,
    NutritionLabelLimitations,
    NutritionLabelQuality,
    validate_all_records,
)

DEFAULT_NUTRITION_LABEL_PATH = REPO_ROOT / "data" / "nutrition_label.json"

# allowing for partial validation by validate_records
_SECTION_MODELS = {
    "coverage": NutritionLabelCoverage,
    "perturbation_quality": NutritionLabelQuality,
    "known_limitations": NutritionLabelLimitations,
}

if TYPE_CHECKING:
    from pathlib import Path


def compute_nutrition_label(
    records_path: str,
    sections_to_include: list[str] | Literal["all"] = "all",
) -> dict:
    """Compute the dataset nutrition label from perturbations.json.

    Reads all records and aggregates:
      - Coverage: total KDs, cells per KD, states profiled, proteins measured
      - Perturbation quality: KD efficiency, response types, orthogonal characterization counts,
        confidence tier counts (high/moderate/low), low cell count

    Args:
        records_path: Path to perturbations.json.
        sections_to_include: "all" (default) to return every section, or a list
            of section names ("coverage", "perturbation_quality") to return only those.
            A filtered result should not be passed to `render_nutrition_label`
            or `export_nutrition_label` since both expect all sections present.

    Returns:
        Dict matching the NutritionLabel schema (or a subset of its top-level
        keys, if sections_to_include is a list).

    Raises:
        FileNotFoundError: If records_path does not exist.
    """
    records = validate_all_records(records_path)
    df = nutrition_report.build_qc_dataframe(records)

    coverage = {
        "total_kds": len({r.perturbation for r in records}),
        "median_cells_per_kd": float(df["n_cells"].median()),
        "min_cells_per_kd": int(df["n_cells"].min()),
        "states_profiled": len(constants.STATES),
        "reliable_states": sum(1 for s in constants.STATES.values() if s["reliable"]),
        "proteins_measured": constants.CITE_SEQ_PROTEIN_PANEL_SIZE,
        "proteins_validated": 180,
    }

    percent_knockdowns = df["percent_knockdown"].dropna()
    perturbation_quality = {
        "median_percent_knockdown": (
            float(percent_knockdowns.median()) if not percent_knockdowns.empty else None
        ),
        "n_efficiency_below_threshold": sum(
            1 for r in records if r.method_assumptions.percent_knockdown_warning
        ),
        "n_low_cell_count": sum(
            1 for r in records if r.method_assumptions.low_cell_count_warning
        ),
        "n_binary_response": int((df["mixscale_response"] == "binary").sum()),
        "n_graded_response": int((df["mixscale_response"] == "graded").sum()),
        "n_with_orthogonal_characterization": sum(
            1 for r in records if r.orthogonal_characterizations
        ),
        "n_high_confidence": int((df["confidence"] == "high").sum()),
        "n_moderate_confidence": int((df["confidence"] == "moderate").sum()),
        "n_low_confidence": int((df["confidence"] == "low").sum()),
    }

    known_limitations = {
        "n_discordances": sum(len(v) for r in records for v in r.discordances.values()),
        "n_discordances_resolved": 0,
        "in_vitro_only": True,
        "human_anchor_available": constants.HUMAN_ANCHOR_AVAILABLE,
    }

    all_sections = {
        "coverage": coverage,
        "perturbation_quality": perturbation_quality,
        "known_limitations": known_limitations,
    }

    label = NutritionLabel.model_validate(all_sections)
    full_label = label.model_dump()

    if sections_to_include == "all":
        return full_label
    return {k: v for k, v in full_label.items() if k in sections_to_include}


def export_nutrition_label(
    label: dict, path: "str | Path" = DEFAULT_NUTRITION_LABEL_PATH
) -> None:
    """Write the nutrition label dict to a JSON file.

    Validates whatever sections are present in `label` against their
    corresponding sub-model (see `_SECTION_MODELS`) rather than the full
    `NutritionLabel` model, so a filtered label (from
    `compute_nutrition_label(..., sections_to_include=[...])`) can be exported
    with only its included sections — no missing sections are added or
    padded with `null`.

    Args:
        label: Dict from compute_nutrition_label (full or filtered).
        path: Output file path.
    """
    for key, value in label.items():
        if key in _SECTION_MODELS:
            _SECTION_MODELS[key].model_validate(value)
    with open(path, "w") as f:
        json.dump(label, f, indent=2)


def load_nutrition_label(path: "str | Path" = DEFAULT_NUTRITION_LABEL_PATH) -> dict:
    """Load a previously exported nutrition_label.json.

    Args:
        path: Input file path.

    Returns:
        The nutrition label dict.

    Raises:
        FileNotFoundError: If path does not exist.
    """
    with open(path) as f:
        return json.load(f)
