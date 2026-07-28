"""Global constants: state definitions, gene lists, model metadata."""

import csv
from pathlib import Path
from typing import Any

import pandas as pd

from mglia.dataset_config import MGLIA_DEFAULT_CONFIG, REPO_ROOT

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
        "reliability_note": (
            "Across our screens in this paper, TF knockdowns appear to perturb the "
            "chemokine state less than other states (relatively few knockdowns "
            "shifted this signature). Additionally, chemokine is a less-characterized"
            "state compared to other ones assessed based on current literature. While "
            "transcriptomic signature scoring didn't alter as much across knockdowns, "
            "interestingly chemokine-related perturbations were "
            "identified via orthogonal secretome data also included in our paper, "
            "highlighting the benefit of multi-omic readouts "
            "for understanding knockdown effect on microglia states."
        ),
    },
}

# Mapping Ucell_column name to states
UCELL_SCORE_COLUMNS: dict[str, str] = {
    state: meta["ucell_col"] for state, meta in STATES.items()
}

# ---------------------------------------------------------------------------
# scHPF factor definitions
# f6, f12, f13 are excluded as describedin Methods
# ---------------------------------------------------------------------------

SCHPF_FACTORS: list[str] = [
    "f1",
    "f2",
    "f3",
    "f4",
    "f5",
    "f7",
    "f8",
    "f9",
    "f10",
    "f11",
    "f14",
    "f15",
    "f16",
    "f17",
    "f18",
    "f19",
    "f20",
    "f21",
    "f22",
    "f23",
    "f24",
    "f25",
    "f26",
]


SCHPF_FACTOR_LABELS: dict[str, str] = {
    "f1": "il/ifn-γ signaling",
    "f2": "glycolysis",
    "f3": "ciita-high",
    "f4": "npy1r-high",
    "f5": "chemokine",
    "f7": "tlr/mapk signaling",
    "f8": "oxphos-1",
    "f9": "motility/adhesion",
    "f10": "grid2-high",
    "f11": "apoe-high",
    "f14": "stress",
    "f15": "hla-high/apc",
    "f16": "cx3cr1-high",
    "f17": "c1q-high/phagocytic",
    "f18": "oxphos-2",
    "f19": "senescence",
    "f20": "ifn-i response",
    "f21": "oxphos-3",
    "f22": "plcg2-high",
    "f23": "s100/tlr signaling",
    "f24": "actin folding",
    "f25": "immunoregulatory",
    "f26": "gpnmb-high",
}


# USE THIS before Human Concordance is established per perturbation
# change this to see if in-vivo data then even better but if not is there
# any anchoring to human data
HUMAN_ANCHOR_AVAILABLE: bool = True

# Human concordance per factor — TODO: fill from paper Table S3
SCHPF_HUMAN_CONCORDANCE: dict[str, bool] = {f: False for f in SCHPF_FACTORS}

# TODO: impelement human concordance with disease datasets overlap i.e from Sun et al as done in paper for all perturbations.

# ---------------------------------------------------------------------------
# MCP Resources / Glossary & Explainer across dashboard
# Larger explanatory burbs also read in for agents via MCP Resources before answering questions
# ---------------------------------------------------------------------------
GLOSSARY_BLURBS: dict[str, str] = {
    "method_assumptions": (
        "Every computed statistic in this dataset rests on methodological "
        "assumptions that are normally buried in a paper's Methods section. This "
        "panel surfaces those assumptions and known caveats directly on each "
        "perturbation record — for cell count, knockdown efficiency, "
        "model-specific effects, and signature reliability — so that both human "
        "readers and AI agents interpreting the data can see what's behind the numbers."
    ),
    "schpf_factors": (
        "Single-cell Hierarchical Poisson Factorization (scHPF), decomposes gene "
        "expression into latent factors as described in Levitin et al. Mol Syst Biol, 2019, https://doi.org/10.15252/msb.20188557. "
        "\n\nHere we show which factors are most shifted "
        "by the knockdown vs NTC by median percentile shift. This is calculated by "
        "projecting our iPSC-derived microglia data onto human microglia factors as described in "
        "the paper, 'A factor-based analysis of individual human microglia uncovers regulators of an Alzheimer-related transcriptional signature' "
        "(Marshe et al, bioRxiv, 2025, https://doi.org/10.1101/2025.03.27.641500) "
        "by our collaborators in the De Jager lab. "
        "Figure 1B in the paper also provides further insight into the top genes used for factor names."
    ),
    "nutrition_label": (
        "Like food nutrition labels that summarize the contents of packaged foods, "
        "a dataset nutrition label provides an accessible overview of dataset-wide "
        "content and quality. \n\nEspecially in a world where both human researchers and AI agents "
        "are constantly evaluating and downloading perturbation transcriptomics datasets, "
        "this label allows users to identify potential quality issues, biases, and "
        "experimenter-derived metadata conditions, helping both humans and AI agents, make "
        "informed decisions about the overview and each perturbation in the dataset. \n\n"
        "This nutrition label is auto-generated from the perturbation records and metadata, along with "
        "highlighting low (red), moderate (yellow), and high (green) confident perturbations across characteristics."
        "\n\nInspired by the Dataset Nutrition Label Project (https://datanutrition.org/)"
    ),
    "mixscale_degs": (
        "As described in our paper, one feature of targeting regulators with CRISPR "
        "interference rather than CRISPR knockout "
        "is that individual cells in the knockdown population may produce different levels "
        "of knockdown. The presence of cells "
        "with different extends of knockdown enables us to investigate the dose-response "
        "relationship between the knockdown of a "
        "transcription factors and the resulting effects on specific signatures. "
        "Specifically, we performed weighted differential expression "
        "using Mixscale (Jiang et al. 2025, Nat Cell Bio, "
        "https://doi.org/10.1038/s41556-025-01622-z) to identify minimally, moderately, "
        "and highly perturbed cells."
    ),
}

# ---------------------------------------------------------------------------
# Citation
# run python scripts/sync_citation.py` after editing to re-sync the static copies there.
# ---------------------------------------------------------------------------

CITATION: dict[str, str] = {
    "authors": "McQuade et al. 2026",
    "title": "Transcriptional regulation of disease-relevant microglial activation programs",
    "journal_or_preprint": "Neuron",
    "year": "2026",
    "doi_url": "#",
    "github_url": "https://github.com/reetm09/mglia_regulators_paper",
    "preprint_url": "#",
    "contact_email": "reet.mishra@ucsf.edu",
}

# ---------------------------------------------------------------------------
# Cell model metadata
# ---------------------------------------------------------------------------

CELL_MODELS: dict[str, dict[str, Any]] = {
    "iTF-MG": {
        "display": "iTF-MG",
        "filename": "itfmg",
        "protocol": "Transcription-factor-driven differentiation",
        "differentiation_days": 14,
        "baseline_state_bias": "interferon, chemokine",
    },
    "iMG": {
        "display": "iMG",
        "filename": "img",
        "protocol": "Cytokine-driven differentiation",
        "differentiation_days": 25,
        "baseline_state_bias": "homeostatic, disease-associated",
    },
}

# ---------------------------------------------------------------------------
# Knockdown gene library
# Real 31-gene panel: both modalities cover the same 31 genes across both cell models).
# ---------------------------------------------------------------------------
ALL_KD_GENES: list[str] = [
    "ARID2",
    "ARID5B",
    "ATMIN",
    "BHLHE40",
    "BHLHE41",
    "BPTF",
    "CEBPD",
    "CNOT10",
    "DEAF1",
    "FOXK1",
    "IRF9",
    "MAF",
    "MEF2C",
    "MEF2D",
    "MITF",
    "POU5F1",
    "RELA",
    "RUNX1",
    "SALL4",
    "SPI1",
    "SREBF1",
    "STAT1",
    "TCF4",
    "ZNF148",
    "ZNF783",
    "ZNF532",
    "PRDM1",
    "STAT2",
    "DNMT1",
    "ZNF644",
    "SMAD3",
]

# Genes with any found model-divergent effects, essentially
# significant signature shifts in different directions for any state
# highlights genes which should be looked at within context of whichever model is better for that state
MODEL_DIVERGENT_GENES: list[str] = [
    "ARID2",
    "ATMIN",
    "DNMT1",
    "MAF",
    "MEF2C",
    "POU5F1",
    "PRDM1",
    "SMAD3",
    "STAT2",
    "TCF4",
    "ZNF532",
    "ZNF644",
]

# ---------------------------------------------------------------------------
# UCell signature gene sets (Table S2)
# ---------------------------------------------------------------------------

_SIGNATURE_GENE_SET_CSV = (
    REPO_ROOT / "data" / "static" / "reference" / "signature_gene_sets.csv"
)


def _load_signature_gene_sets(path: Path) -> dict[str, list[str]]:
    """Load per-state signature gene lists from the wide-format reference CSV.

    Each CSV column is one state's gene list (column names match STATES keys directly);
    blanks/NaNs are dropped per column.

    Args:
        path: Path to signature_gene_sets.csv.

    Returns:
        Dict keyed by STATES key -> list of gene symbols. Empty lists for any state
        not present in the CSV, or for every state if the file doesn't exist yet.
    """
    gene_sets: dict[str, list[str]] = {state: [] for state in STATES}
    if not path.exists():
        return gene_sets
    df = pd.read_csv(path)
    for state in STATES:
        if state in df.columns:
            gene_sets[state] = df[state].dropna().astype(str).str.strip().tolist()
    return gene_sets


SIGNATURE_GENE_SETS: dict[str, list[str]] = _load_signature_gene_sets(
    _SIGNATURE_GENE_SET_CSV
)

# ---------------------------------------------------------------------------
# Functional assays for featured KDs (hard-coded from paper figures)
# ---------------------------------------------------------------------------

FUNCTIONAL_ASSAY_NAMES = {
    "phagocytosis_amyloid": "Phagocytosis (β-amyloid)",
    "phagocytosis_synaptosomes": "Phagocytosis (human synaptosomes)",
    "cathepsin_b": "Cathepsin B activity",
    "lysosomal_ph": "LysoTracker signal (lysosomal pH)",
    "secreted_ifnb_response": "Secreted protein response IFNb",
    "dq_bsa_uptake": "DQ-BSA uptake and cleavage",
}


# Raw CSV direction tokens -> schema-valid FunctionalReadout.direction values.
_DIRECTION_NORMALIZATION = {
    "not measured": "not_measured",
    "no change": "no_change",
}


def _load_functional_assays(
    path: Path,
) -> dict[str, dict[str, dict[str, dict[str, Any]]]]:
    """Load per-gene, per-model functional assay readouts from the reference CSV.

    Each CSV row is one gene/cell-model combination; each remaining column is one
    assay's direction (e.g. "up", "down", "no change", "not measured").

    Args:
        path: Path to functional_readouts.csv.

    Returns:
        Dict keyed by gene -> cell_model -> assay_id -> dict with keys direction
        (str, underscored to match FunctionalReadout.direction), validated (bool),
        n_wells (None), assay_name (str). Empty dict if the file doesn't exist yet.
    """
    results: dict[str, dict[str, dict[str, dict[str, Any]]]] = {}
    if not path.exists():
        return results

    with open(path, newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            model = row.pop("model").strip()
            gene = row.pop("perturbation").strip()

            results.setdefault(gene, {})[model] = {
                assay_id: {
                    "direction": _DIRECTION_NORMALIZATION.get(
                        direction.strip(), direction.strip()
                    ),
                    "validated": direction.strip() != "not measured",
                    "n_wells": None,
                    "assay_name": FUNCTIONAL_ASSAY_NAMES[assay_id],
                }
                for assay_id, direction in row.items()
            }

    return results


FUNCTIONAL_ASSAYS = _load_functional_assays(
    MGLIA_DEFAULT_CONFIG.functional_readouts_path()
)

# ---------------------------------------------------------------------------
# Mixscale response type per gene - to overwrite
# ---------------------------------------------------------------------------

MIXSCALE_RESPONSE_TYPE: dict[str, str] = {
    # "binary" | "graded"
    # e.g. "ZNF532": "binary", "PRDM1": "graded", ...
}

# ---------------------------------------------------------------------------
# Knockdown efficiency from RT-qPCR
# ---------------------------------------------------------------------------

# Fraction remaining mRNA (0.0 = complete KD, 1.0 = no KD), keyed by gene then by
# the cell model it was actually measured in (average of both
# guides). A gene measured in only one model has no entry for the other model —
# use compute.get_percent_knockdown(gene, cell_model, config) to look up a value,
# which converts this fraction to the percent_knockdown scale via
# `100 * (1 - fraction)` and takes priority over the transcriptomic
# knockdown-efficiency tables (data/static/kd_efficiency_tables/). A gene with
# neither an RT-qPCR value here nor a usable transcriptomic value is reported as
# not measured (percent_knockdown=None, source="not_measured").

KD_EFFICIENCY: dict[str, dict[str, float]] = {
    # Measured in iTF-MG
    "STAT2": {"iTF-MG": 0.06},  # g1 0.05, g2 0.08 — both near-complete KD
    "DNMT1": {"iTF-MG": 0.50},  # g1 0.50, g2 0.50
    "IRF9": {"iTF-MG": 0.50},  # g1 0.25, g2 0.75
    "SMAD3": {"iTF-MG": 0.48},  # g1 0.45, g2 0.50
    "CNOT10": {"iTF-MG": 0.58},  # g1 0.35, g2 0.80
    # Measured in iMG
    "PRDM1": {"iMG": 0.28},  # g1 0.35, g2 0.20
    "MEF2C": {"iMG": 0.30},  # g1 0.05, g2 0.55
    "MEF2D": {"iMG": 0.60},  # g1 0.60, g2 0.60 (weak/inconsistent KD, P=0.22 for g2)
    "ZNF644": {"iMG": 0.09},  # g1 0.10, g2 0.08 — strong KD
    "FOXK1": {"iMG": 0.58},  # g1 0.25, g2 0.90 (g2 essentially no KD, P=0.8)
    "ARID2": {"iMG": 0.78},  # g1 0.70, g2 0.85 — weak/no significant KD (P=0.37, 0.83)
    "ZNF532": {"iMG": 0.27},  # g1 0.08, g2 0.45
    "MAF": {"iMG": 0.48},  # g1 0.85, g2 0.10 — highly guide-dependent
}

# ---------------------------------------------------------------------------
# CITE-seq protein panel
# ---------------------------------------------------------------------------

# The antibody panel size (including isotype controls). Used by the nutrition
# label's coverage.proteins_measured field.
CITE_SEQ_PROTEIN_PANEL_SIZE: int = 180

# ---------------------------------------------------------------------------
# App metadata
# ---------------------------------------------------------------------------

DATA_VERSION: str = "v0.1-dev"

# ---------------------------------------------------------------------------
# UI colors
# ---------------------------------------------------------------------------

COLOR_UP: str = "#D93025"  # direction: up-regulated / increased
COLOR_DOWN: str = "#1A73E8"  # direction: down-regulated / decreased
COLOR_NEUTRAL: str = "#888888"  # direction: no change / axis lines
COLOR_MUTED: str = "#BBBBBB"  # unreliable-state bars (greyed out)
COLOR_NOT_MEASURED: str = "#999999"  # "not measured" functional readout text
COLOR_RESPONSE_BADGE: str = "#5F6368"  # neutral badge (mixscale response type)

COLOR_SUCCESS: str = "#1E8E3E"  # high confidence / validated / no warnings
COLOR_WARNING: str = "#E8A33D"  # moderate confidence / mild severity
COLOR_DANGER: str = "#D93025"  # low confidence / strong severity
COLOR_MODERATE_SEVERITY: str = "#E8752C"

CONFIDENCE_COLORS: dict[str, str] = {
    "high": COLOR_SUCCESS,
    "moderate": COLOR_WARNING,
    "low": COLOR_DANGER,
}
SEVERITY_COLORS: dict[str, str] = {
    "info": COLOR_DOWN,  # neutral/informational
    "mild": COLOR_WARNING,
    "moderate": COLOR_MODERATE_SEVERITY,
    "strong": COLOR_DANGER,
}

CHART_FONT_COLOR: str = "#333333"  # Plotly font color

# Compare page: distinguishes Gene A vs Gene B across the signature bars and the
# multistate heatmap highlight (row text color + box outline).
GENE_A_COLOR: str = "#7B3FF2"
GENE_B_COLOR: str = "#FF8C1A"

# Volcano plot colors
RNA_VOLCANO_COLORS: dict[str, str] = {
    "homeostatic": "#107B35",
    "disease_associated": "#BF0063",
    "lipid_rich": "#E76333",
    "antigen_presenting": "#FDAC10",
    "interferon_responsive": "#5FADAF",
    "chemokine": "#A335C2",
}

# Protein volcano plots states to color with same colors as RNA_VOLCANO_COLORS
PROT_VOLCANO_STATES: list[str] = [
    "disease_associated",
    "chemokine",
    "antigen_presenting",
    "interferon_responsive",
]
