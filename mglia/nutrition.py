"""Dataset nutrition label: compute, render, and export."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import streamlit as st


def compute_nutrition_label(records_path: str) -> dict:
    """Compute the dataset nutrition label from perturbations.json.

    Reads all records and aggregates:
      - Coverage: total KDs, cells per KD, states profiled, proteins measured/validated
      - Perturbation quality: KD efficiency, response types, orthogonal validation counts
      - Known limitations: low cell count, discordances, in_vitro_only flag
      - Benchmark readiness: split status, leakage risk, null baselines, task count

    Args:
        records_path: Path to perturbations.json.

    Returns:
        Dict matching the NutritionLabel schema.

    Raises:
        FileNotFoundError: If records_path does not exist.
    """
    raise NotImplementedError


def render_nutrition_label(label: dict) -> None:
    """Render the nutrition label as a Streamlit 2×2 grid of metric cards.

    Each metric is shown as a key-value row with a colored indicator:
    green (good), yellow (warning), red (limitation).

    Args:
        label: Dict from compute_nutrition_label or loaded from nutrition_label.json.
    """
    raise NotImplementedError


def export_nutrition_label(label: dict, path: str = "data/nutrition_label.json") -> None:
    """Write the nutrition label dict to a JSON file.

    Args:
        label: Dict from compute_nutrition_label.
        path: Output file path.
    """
    raise NotImplementedError
