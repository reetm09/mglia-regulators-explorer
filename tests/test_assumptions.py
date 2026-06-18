"""Tests for mglia.assumptions — assumption registry and audit logic."""

import pytest


def test_low_cell_count_triggers_warning():
    """audit_record with n_cells < 100 should set low_cell_count_warning=True."""
    pytest.skip("not implemented yet")


def test_sufficient_cell_count_no_warning():
    """audit_record with n_cells >= 100 should set low_cell_count_warning=False."""
    pytest.skip("not implemented yet")


def test_low_kd_efficiency_triggers_warning():
    """audit_record with kd_efficiency < 0.5 should set kd_efficiency_warning=True."""
    pytest.skip("not implemented yet")


def test_chemokine_reliability_always_low():
    """audit_record should always set chemokine_signature_reliability='low'."""
    pytest.skip("not implemented yet")


def test_get_all_flags_empty_for_clean_record():
    """get_all_flags should return an empty list for a record with no active flags."""
    pytest.skip("not implemented yet")


def test_get_assumption_explanation_raises_on_unknown_method():
    """get_assumption_explanation should raise KeyError for an unknown method."""
    pytest.skip("not implemented yet")


def test_model_divergent_gene_sets_model_specific_effects():
    """audit_record for SMAD3 or STAT2 should set model_specific_effects=True."""
    pytest.skip("not implemented yet")
