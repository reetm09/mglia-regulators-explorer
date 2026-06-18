"""Tests for mglia.loader — MuData loading and cell subsetting."""

import pytest


def test_check_mdata_schema_with_missing_columns():
    """check_mdata_schema should report missing columns on a stripped AnnData."""
    pytest.skip("not implemented yet")


def test_get_perturbation_cells_returns_correct_count():
    """get_perturbation_cells should return exactly N_CELLS_PER_GROUP cells."""
    pytest.skip("not implemented yet")


def test_get_ntc_cells_returns_only_ntc():
    """get_ntc_cells should return only cells where perturbed_gene == 'NTC'."""
    pytest.skip("not implemented yet")


def test_load_mdata_raises_file_not_found():
    """load_mdata should raise FileNotFoundError with download instructions
    if the .h5mu file does not exist."""
    pytest.skip("not implemented yet")


def test_load_mdata_raises_on_invalid_model():
    """load_mdata should raise ValueError for an unrecognised model name."""
    pytest.skip("not implemented yet")


def test_get_signature_scores_returns_correct_columns():
    """get_signature_scores should return a DataFrame with all 6 state columns."""
    pytest.skip("not implemented yet")


def test_get_schpf_factors_returns_correct_columns():
    """get_schpf_factors should return a DataFrame with columns matching SCHPF_FACTORS."""
    pytest.skip("not implemented yet")
