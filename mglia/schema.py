"""Pydantic v2 models for all perturbation records and related data structures."""

from typing import Any, Optional

from pydantic import BaseModel, field_validator


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class SignatureShift(BaseModel):
    """Per-state UCell score shift for a knockdown vs NTC."""

    delta_pctl: float
    fdr: float
    reliable: bool
    note: Optional[str] = None


class DEGList(BaseModel):
    """Top differentially expressed genes from Mixscale-weighted analysis."""

    top_positive: list[str]
    top_negative: list[str]
    n_positive: int
    n_negative: int
    assumption_flags: list[str]


class FunctionalReadout(BaseModel):
    """Single functional assay result for a featured KD."""

    assay_name: str
    direction: str  # "up" | "down" | "no_change" | "not_measured"
    validated: bool
    n_wells: Optional[int] = None

    @field_validator("direction")
    @classmethod
    def _valid_direction(cls, v: str) -> str:
        allowed = {"up", "down", "no_change", "not_measured"}
        if v not in allowed:
            raise ValueError(f"direction must be one of {allowed}, got {v!r}")
        return v


class Discordance(BaseModel):
    """mRNA / protein direction discordance for a gene."""

    gene: str
    mrna_direction: str
    protein_direction: str
    validated: bool
    likely_cause: str


class AssumptionAudit(BaseModel):
    """Per-record methodological assumption flags."""

    low_cell_count_warning: bool
    kd_efficiency_warning: bool
    antibody_validation_incomplete: bool
    model_specific_effects: bool
    chemokine_signature_reliability: str  # always "low"
    flags: list[str]


# ---------------------------------------------------------------------------
# Top-level record
# ---------------------------------------------------------------------------


class PerturbationRecord(BaseModel):
    """Full data record for a single knockdown × cell model combination."""

    perturbation: str
    cell_model: str  # "iTF-MG" | "iMG"
    n_cells: int
    confidence: str  # "high" | "moderate" | "low"
    kd_efficiency: Optional[float] = None
    mixscale_response: str  # "binary" | "graded" | "unknown"
    prediction_targets: dict[str, Any]  # deg, signature_shift, schpf_factors
    discordances: dict[str, list[Any]]
    functional_readouts: dict[str, FunctionalReadout]
    assumption_audit: AssumptionAudit
    benchmark_split: str  # "train" | "test"
    orthogonal_validations: list[str]
    paper_figures: list[str]

    @field_validator("cell_model")
    @classmethod
    def _valid_model(cls, v: str) -> str:
        allowed = {"iTF-MG", "iMG"}
        if v not in allowed:
            raise ValueError(f"cell_model must be one of {allowed}, got {v!r}")
        return v

    @field_validator("confidence")
    @classmethod
    def _valid_confidence(cls, v: str) -> str:
        allowed = {"high", "moderate", "low"}
        if v not in allowed:
            raise ValueError(f"confidence must be one of {allowed}, got {v!r}")
        return v

    @field_validator("benchmark_split")
    @classmethod
    def _valid_split(cls, v: str) -> str:
        allowed = {"train", "test"}
        if v not in allowed:
            raise ValueError(f"benchmark_split must be one of {allowed}, got {v!r}")
        return v


# ---------------------------------------------------------------------------
# Benchmark and nutrition label models
# ---------------------------------------------------------------------------


class BenchmarkSplit(BaseModel):
    """Definition of a single benchmark task."""

    task_name: str
    train_genes: list[str]
    test_genes: list[str]
    metric: str
    description: str
    input_features: list[str]
    prediction_targets: list[str]


class NutritionLabelCoverage(BaseModel):
    total_kds: int
    median_cells_per_kd: float
    min_cells_per_kd: int
    states_profiled: int
    reliable_states: int
    proteins_measured: int
    proteins_validated: int


class NutritionLabelQuality(BaseModel):
    median_kd_efficiency: Optional[float]
    n_efficiency_below_threshold: int
    n_binary_response: int
    n_graded_response: int
    n_with_orthogonal_validation: int


class NutritionLabelLimitations(BaseModel):
    n_low_cell_count: int
    n_discordances: int
    n_discordances_resolved: int
    in_vitro_only: bool
    human_anchor_available: bool


class NutritionLabelBenchmark(BaseModel):
    split_defined: bool
    leakage_risk: str
    null_baseline_computed: bool
    n_tasks_with_metrics: int
    cross_model_test: bool
    assumption_audit_per_record: bool


class NutritionLabel(BaseModel):
    coverage: NutritionLabelCoverage
    perturbation_quality: NutritionLabelQuality
    known_limitations: NutritionLabelLimitations
    benchmark_readiness: NutritionLabelBenchmark


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def validate_record(record: dict[str, Any]) -> PerturbationRecord:
    """Parse a raw dict into a PerturbationRecord, raising on schema violation.

    Args:
        record: Raw dict loaded from perturbations.json.

    Returns:
        Validated PerturbationRecord instance.

    Raises:
        pydantic.ValidationError: If any field is missing or has an invalid value.
    """
    raise NotImplementedError


def validate_all_records(path: str) -> list[PerturbationRecord]:
    """Load and validate every record in perturbations.json.

    Args:
        path: Path to perturbations.json.

    Returns:
        List of validated PerturbationRecord instances.

    Raises:
        pydantic.ValidationError: On first invalid record encountered.
    """
    raise NotImplementedError
