"""Tests for mglia.schema — Pydantic v2 model validation."""

import pytest
from pydantic import ValidationError


def test_valid_record_passes_validation():
    """A fully populated valid dict should parse without error."""
    pytest.skip("not implemented yet")


def test_missing_required_field_raises():
    """Omitting a required field should raise ValidationError."""
    pytest.skip("not implemented yet")


def test_invalid_confidence_raises():
    """An invalid confidence value (e.g. 'medium') should raise ValidationError."""
    pytest.skip("not implemented yet")


def test_invalid_cell_model_raises():
    """An invalid cell_model value should raise ValidationError."""
    pytest.skip("not implemented yet")


def test_invalid_benchmark_split_raises():
    """An invalid benchmark_split value should raise ValidationError."""
    pytest.skip("not implemented yet")


def test_all_records_pass_validation():
    """Every record in data/perturbations.json should pass schema validation."""
    pytest.skip("not implemented yet — requires generated perturbations.json")
