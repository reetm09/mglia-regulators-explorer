"""Benchmark task definitions, train/test splits, and scoring functions."""

from __future__ import annotations

from typing import Any

import pandas as pd

from mglia.constants import TEST_SET_GENES, TRAIN_GENES

# ---------------------------------------------------------------------------
# Task definitions
# ---------------------------------------------------------------------------

BENCHMARK_TASKS: dict[str, dict[str, Any]] = {
    "perturbation_prediction": {
        "description": "Predict 6-state signature shifts for held-out knockdowns.",
        "train_genes": TRAIN_GENES,
        "test_genes": TEST_SET_GENES,
        "input_features": ["gene_name", "baseline_expression"],
        "prediction_targets": ["delta_pctl_per_state"],
        "metrics": ["pearson_r", "direction_accuracy"],
        "primary_metric": "pearson_r",
        "difficulty": "medium",
    },
    "cross_model_generalization": {
        "description": "Train on iTF-MG, evaluate on iMG.",
        "train_genes": TRAIN_GENES,
        "test_genes": TRAIN_GENES,  # same genes, different model
        "input_features": ["gene_name", "itfmg_signature_shifts"],
        "prediction_targets": ["img_signature_shifts"],
        "metrics": ["delta_pearson_r"],
        "primary_metric": "delta_pearson_r",
        "difficulty": "hard",
    },
    "dose_response": {
        "description": "Predict signature shifts from Mixscale score tiers.",
        "train_genes": TRAIN_GENES,
        "test_genes": TEST_SET_GENES,
        "input_features": ["gene_name", "mixscale_tier"],
        "prediction_targets": ["delta_pctl_per_state_per_tier"],
        "metrics": ["mse", "shape_classification_accuracy"],
        "primary_metric": "mse",
        "difficulty": "hard",
    },
    "multistate_combinatorial": {
        "description": "Predict the 6-state direction vector (up/down/no_change) for each KD.",
        "train_genes": TRAIN_GENES,
        "test_genes": TEST_SET_GENES,
        "input_features": ["gene_name"],
        "prediction_targets": ["direction_per_state"],
        "metrics": ["per_state_accuracy", "exact_match_accuracy"],
        "primary_metric": "per_state_accuracy",
        "difficulty": "medium",
    },
}


# ---------------------------------------------------------------------------
# Split and data loading
# ---------------------------------------------------------------------------


def get_split(task: str) -> dict[str, Any]:
    """Return the train/test split definition for a benchmark task.

    Args:
        task: Task name key in BENCHMARK_TASKS.

    Returns:
        Dict with keys: train_genes, test_genes, description, input_features,
        prediction_targets, metrics, primary_metric.

    Raises:
        KeyError: If task is not in BENCHMARK_TASKS.
    """
    raise NotImplementedError


def load_split_data(task: str, split: str) -> pd.DataFrame:
    """Load signature shift data for the train or test genes of a task.

    Args:
        task: Task name key in BENCHMARK_TASKS.
        split: One of "train" or "test".

    Returns:
        DataFrame with genes as rows and per-state delta_pctl as columns.

    Raises:
        FileNotFoundError: If data/perturbations.json does not exist.
        ValueError: If split is not "train" or "test".
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def score_predictions(predictions: pd.DataFrame, task: str) -> dict[str, float]:
    """Compute all metrics for a task given a predictions DataFrame.

    Args:
        predictions: DataFrame with the same shape as load_split_data output.
            Must include columns matching prediction_targets for the task.
        task: Task name key in BENCHMARK_TASKS.

    Returns:
        Dict with per-metric scores and an overall weighted score.
        Keys include each metric name plus "overall".

    Raises:
        ValueError: If predictions format does not match task spec.
    """
    raise NotImplementedError


def get_null_baseline(task: str) -> dict[str, float]:
    """Compute mean-predictor and random-permutation null baselines for a task.

    Results are cached after first computation.

    Args:
        task: Task name key in BENCHMARK_TASKS.

    Returns:
        Dict with keys: mean_predictor (dict of metric scores),
        random_permutation (dict of metric scores).
    """
    raise NotImplementedError


def generate_benchmark_splits_json(output_path: str = "data/benchmark_splits.json") -> None:
    """Write all task definitions to benchmark_splits.json.

    Args:
        output_path: Destination path for the JSON file.
    """
    raise NotImplementedError
