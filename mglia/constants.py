"""Global constants: state definitions, gene lists, model metadata."""

from typing import Any

# ---------------------------------------------------------------------------
# Microglial state definitions
# ---------------------------------------------------------------------------

STATES: dict[str, dict[str, Any]] = {
    "homeostatic": {
        "display": "Homeostatic",
        "marker": "P2RY12",
        "ucell_col": "homeostatic_score_ucell",
        "reliable": True,
    },
    "disease_associated": {
        "display": "Disease-associated (DAM)",
        "marker": "CD9",
        "ucell_col": "dam_score_ucell",
        "reliable": True,
    },
    "lipid_rich": {
        "display": "Lipid-rich",
        "marker": "BODIPY",
        "ucell_col": "lipid_dam_score_ucell",
        "reliable": True,
    },
    "antigen_presenting": {
        "display": "Antigen-presenting",
        "marker": "HLA-DMB",
        "ucell_col": "antigen_presenting_score_ucell",
        "reliable": True,
    },
    "interferon_responsive": {
        "display": "Interferon-responsive",
        "marker": "IFIT1",
        "ucell_col": "interferon_score_ucell",
        "reliable": True,
    },
    "chemokine": {
        "display": "Chemokine",
        "marker": "CCL13",
        "ucell_col": "chemokine_score_ucell",
        "reliable": False,
        "reliability_note": "Only 4 FACS hits; signature likely incomplete",
    },
}

# Convenience mapping: state key → obs column name in rna modality
UCELL_SCORE_COLUMNS: dict[str, str] = {
    state: meta["ucell_col"] for state, meta in STATES.items()
}

# ---------------------------------------------------------------------------
# scHPF factor definitions
# f6, f12, f13 are absent from the data (excluded during factorization QC)
# ---------------------------------------------------------------------------

SCHPF_FACTORS: list[str] = [
    "f1", "f2", "f3", "f4", "f5",
    "f7", "f8", "f9", "f10", "f11",
    "f14", "f15", "f16", "f17", "f18", "f19", "f20",
    "f21", "f22", "f23", "f24", "f25", "f26",
]

# Human concordance per factor — TODO: fill from paper Table S3
SCHPF_HUMAN_CONCORDANCE: dict[str, bool] = {f: False for f in SCHPF_FACTORS}

# ---------------------------------------------------------------------------
# Cell model metadata
# ---------------------------------------------------------------------------

CELL_MODELS: dict[str, dict[str, Any]] = {
    "iTF-MG": {
        "display": "iTF-MG",
        "filename": "itfmg",
        "protocol": "Transcription-factor-driven differentiation",
        "differentiation_days": 14,
        "baseline_state_bias": "homeostatic",
        "benchmark_role": "train",
    },
    "iMG": {
        "display": "iMG",
        "filename": "img",
        "protocol": "Cytokine-driven differentiation",
        "differentiation_days": 25,
        "baseline_state_bias": "homeostatic",
        "benchmark_role": "test",
    },
}

# ---------------------------------------------------------------------------
# Knockdown gene library
# ---------------------------------------------------------------------------

# Held-out test set — do not add to train set; do not change without versioning.
TEST_SET_GENES: list[str] = ["ZNF532", "PRDM1", "STAT2", "DNMT1", "ZNF644", "ZNF783"]

ALL_KD_GENES: list[str] = [
    # Train (25)
    "BHLHE40", "BRD4", "CHD4", "EGR1", "EZH2",
    "HDAC1", "IRF1", "IRF3", "IRF8", "KLF4",
    "MED12", "MEF2A", "MEIS1", "NFKB1", "NR4A1",
    "PPARG", "RUNX1", "SMAD3", "SP1", "SPI1",
    "TET2", "TRIM28", "ZEB1", "ZNF148", "ZNF281",
    # Test (6) — held out
    "ZNF532", "PRDM1", "STAT2", "DNMT1", "ZNF644", "ZNF783",
]

TRAIN_GENES: list[str] = [g for g in ALL_KD_GENES if g not in TEST_SET_GENES]

# Genes with known model-divergent effects — used in assumption audit
MODEL_DIVERGENT_GENES: list[str] = ["SMAD3", "STAT2"]

# ---------------------------------------------------------------------------
# UCell signature gene sets (Table S2) — TODO: fill with real gene lists
# ---------------------------------------------------------------------------

SIGNATURE_GENE_SETS: dict[str, list[str]] = {
    "homeostatic": [],           # e.g. P2RY12, CX3CR1, TMEM119, ...
    "disease_associated": [],    # e.g. CD9, TREM2, LPL, ...
    "lipid_rich": [],            # e.g. FABP5, GPNMB, ...
    "antigen_presenting": [],    # e.g. HLA-DMB, HLA-DRA, CD74, ...
    "interferon_responsive": [], # e.g. IFIT1, IFIT2, MX1, ...
    "chemokine": [],             # e.g. CCL13, CCL2, ...
}

# ---------------------------------------------------------------------------
# Functional assays for featured KDs (hard-coded from paper figures)
# ---------------------------------------------------------------------------

FUNCTIONAL_ASSAYS: dict[str, dict[str, Any]] = {
    "ZNF532": {
        "phagocytosis_amyloid": {"direction": "up", "validated": True, "n_wells": None, "assay_name": "Phagocytosis (β-amyloid)"},
        "phagocytosis_synaptosomes": {"direction": "up", "validated": True, "n_wells": None, "assay_name": "Phagocytosis (synaptosomes)"},
        "lysosomal_ph": {"direction": "down", "validated": True, "n_wells": None, "assay_name": "Lysosomal pH"},
        "cathepsin_b": {"direction": "up", "validated": True, "n_wells": None, "assay_name": "Cathepsin B activity"},
    },
    "PRDM1": {
        "phagocytosis_amyloid": {"direction": "up", "validated": True, "n_wells": None, "assay_name": "Phagocytosis (β-amyloid)"},
        "phagocytosis_synaptosomes": {"direction": "up", "validated": True, "n_wells": None, "assay_name": "Phagocytosis (synaptosomes)"},
        "lysosomal_ph": {"direction": "not_measured", "validated": False, "n_wells": None, "assay_name": "Lysosomal pH"},
        "cathepsin_b": {"direction": "not_measured", "validated": False, "n_wells": None, "assay_name": "Cathepsin B activity"},
    },
    "STAT2": {
        "phagocytosis_amyloid": {"direction": "no_change", "validated": True, "n_wells": None, "assay_name": "Phagocytosis (β-amyloid)"},
        "phagocytosis_synaptosomes": {"direction": "not_measured", "validated": False, "n_wells": None, "assay_name": "Phagocytosis (synaptosomes)"},
        "lysosomal_ph": {"direction": "not_measured", "validated": False, "n_wells": None, "assay_name": "Lysosomal pH"},
        "cathepsin_b": {"direction": "not_measured", "validated": False, "n_wells": None, "assay_name": "Cathepsin B activity"},
    },
    "DNMT1": {
        "phagocytosis_amyloid": {"direction": "up", "validated": True, "n_wells": None, "assay_name": "Phagocytosis (β-amyloid)"},
        "phagocytosis_synaptosomes": {"direction": "not_measured", "validated": False, "n_wells": None, "assay_name": "Phagocytosis (synaptosomes)"},
        "lysosomal_ph": {"direction": "not_measured", "validated": False, "n_wells": None, "assay_name": "Lysosomal pH"},
        "cathepsin_b": {"direction": "not_measured", "validated": False, "n_wells": None, "assay_name": "Cathepsin B activity"},
    },
}

# ---------------------------------------------------------------------------
# Mixscale response type per gene (Fig S7) — TODO: fill from paper
# ---------------------------------------------------------------------------

MIXSCALE_RESPONSE_TYPE: dict[str, str] = {
    # "binary" | "graded"
    # e.g. "ZNF532": "binary", "PRDM1": "graded", ...
}

# ---------------------------------------------------------------------------
# Knockdown efficiency from RT-qPCR (Fig S2) — TODO: fill from paper
# ---------------------------------------------------------------------------

KD_EFFICIENCY: dict[str, float] = {
    # gene: fraction remaining mRNA (0.0 = complete KD, 1.0 = no KD)
    # e.g. "ZNF532": 0.15, ...
}

# ---------------------------------------------------------------------------
# App metadata
# ---------------------------------------------------------------------------

DATA_VERSION: str = "v0.1-dev"
