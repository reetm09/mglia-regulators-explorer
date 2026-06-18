"""Tests for mglia.benchmark — splits, scoring, and null baselines."""

import pytest

from mglia.constants import TEST_SET_GENES, TRAIN_GENES


def test_get_split_returns_correct_train_genes():
    """get_split('perturbation_prediction') should return TRAIN_GENES as train set."""
    pytest.skip("not implemented yet")


def test_get_split_returns_correct_test_genes():
    """get_split('perturbation_prediction') should return TEST_SET_GENES as test set."""
    pytest.skip("not implemented yet")


def test_test_genes_never_in_train():
    """No TEST_SET_GENES gene should appear in any task's train_genes list."""
    from mglia.benchmark import BENCHMARK_TASKS
    for task_name, task in BENCHMARK_TASKS.items():
        overlap = set(task["train_genes"]) & set(TEST_SET_GENES)
        assert not overlap, (
            f"Task {task_name!r} has test genes in train set: {overlap}"
        )


def test_get_split_raises_on_unknown_task():
    """get_split should raise KeyError for an unknown task name."""
    pytest.skip("not implemented yet")


def test_score_predictions_returns_expected_keys():
    """score_predictions should return a dict with metric keys + 'overall'."""
    pytest.skip("not implemented yet")


def test_get_null_baseline_produces_valid_dict():
    """get_null_baseline should return a dict with mean_predictor and random_permutation."""
    pytest.skip("not implemented yet")
