"""Dataset configuration: path templates and column mappings for a perturbation dataset.

Keeps generate_records.py and static_tables.py free of hard-coded paths, so a new
dataset can be supported by writing a new DatasetConfig instead of new
parsing code.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


@dataclass(frozen=True)
class DatasetConfig:
    """Describes where a perturbation dataset's files live and how they're named.

    Different file categories in the same dataset may use different tokens for the
    same cell model (e.g. "iTF-MG" in DEG/DAP tables, "iTF" in shift tables and
    processed h5mu filenames) — `model_tokens` captures that per-category mapping.
    """

    name: str
    static_dir: Path
    processed_dir: Path

    # cell_model key (e.g. "iTF-MG") -> token used in each path category's filenames
    model_tokens: dict[str, dict[str, str]]

    # path templates, relative to static_dir / processed_dir, using {model} and {gene}
    deg_table_template: str
    dap_table_template: str
    signature_shift_template: str
    factor_shift_template: str
    processed_rna_template: str  # relative to processed_dir; {model} only
    volcano_plot_template: str  # {model_dir}, {model}, {gene}, {modality}, {suffix}
    signature_shift_image_template: str  # {model_dir}, {gene}
    factor_shift_image_template: str  # {model_dir}, {gene}
    kd_eff_table_template: str  # {model} only
    functional_readouts_template: str  # single file, no placeholders

    # column names used within the deg/dap tables
    gene_col: str = "Gene"
    log2fc_col: str = "log2FC"
    fdr_col: str = "FDR"

    # column names used within the signature/factor shift tables
    shift_gene_col: str = "perturbed_gene"
    shift_factor_col: str = "Factor"
    shift_pctshift_col: str = "PctShift"
    shift_qval_col: str = "qval"

    # column names used within knockdown efficiency tables
    kd_gene_col: str = "perturbation"
    kd_transcriptomic_ratio: str = "expression_ratio"
    kd_percent_knockdown_col: str = "percent_knockdown"
    kd_ntc_mean_expr: str = "ntc_mean_expression"
    kd_ntc_frac_expr: str = "ntc_fraction_expressing"
    kd_num_guides: str = "num_guides"

    # Overriding Gene List if provided directly or useful for subset of genes
    gene_list: list[str] | None = None

    def model_token(self, category: str, cell_model: str) -> str:
        """Look up the filename token for a cell model within a path category.

        Args:
            category: One of the keys in `model_tokens` (e.g. "deg_table").
            cell_model: Cell model key (e.g. "iTF-MG" or "iMG").

        Returns:
            The filename token used for that model within that file category.

        Raises:
            KeyError: If category or cell_model is not configured.
        """
        return self.model_tokens[category][cell_model]

    def deg_table_path(self, cell_model: str, gene: str) -> Path:
        """Path to the RNA DEG (differentially expressed gene) table CSV for a gene/model."""
        token = self.model_token("deg_table", cell_model)
        return self.static_dir / self.deg_table_template.format(model=token, gene=gene)

    def dap_table_path(self, cell_model: str, gene: str) -> Path:
        """Path to the Protein DAP (differential protein abundance) table CSV for a gene/model."""
        token = self.model_token("dap_table", cell_model)
        return self.static_dir / self.dap_table_template.format(model=token, gene=gene)

    def kd_table_path(self, cell_model: str) -> Path:
        """Path to the knockdown efficiency table CSV for a model."""
        token = self.model_token("kd_efficiency", cell_model)
        return self.static_dir / self.kd_eff_table_template.format(model=token)

    def signature_shift_path(self, cell_model: str) -> Path:
        """Path to the UCell signature percentile-shift table for a model."""
        token = self.model_token("signature_shift", cell_model)
        return self.static_dir / self.signature_shift_template.format(model=token)

    def factor_shift_path(self, cell_model: str) -> Path:
        """Path to the scHPF factor percentile-shift table for a model."""
        token = self.model_token("factor_shift", cell_model)
        return self.static_dir / self.factor_shift_template.format(model=token)

    def functional_readouts_path(self) -> Path:
        """Path to the functional assay readouts reference CSV."""
        return self.static_dir / self.functional_readouts_template

    def processed_rna_path(self, cell_model: str) -> Path:
        """Path to the processed MuData/h5mu file for a cell model."""
        token = self.model_token("processed_rna", cell_model)
        return self.processed_dir / self.processed_rna_template.format(model=token)

    def volcano_plot_path(self, cell_model: str, gene: str, modality: str) -> Path:
        """Path to a per-gene volcano plot PNG.

        Args:
            cell_model: Cell model key.
            gene: Target gene name.
            modality: "rna" or "prot".

        Raises:
            ValueError: If modality is not "rna" or "prot".
        """
        if modality not in ("rna", "prot"):
            raise ValueError(f'modality must be "rna" or "prot", got {modality!r}')
        token = self.model_token("volcano_plot", cell_model)
        suffix = "_corr" if modality == "prot" else ""
        return self.static_dir / self.volcano_plot_template.format(
            model_dir=cell_model,
            model=token,
            gene=gene,
            modality=modality,
            suffix=suffix,
        )

    def signature_shift_image_path(self, cell_model: str, gene: str) -> Path:
        """Path to the per-gene signature percentile-shift point-plot JPEG."""
        return self.static_dir / self.signature_shift_image_template.format(
            model_dir=cell_model, gene=gene
        )

    def factor_shift_image_path(self, cell_model: str, gene: str) -> Path:
        """Path to the per-gene scHPF factor percentile-shift point-plot JPEG."""
        return self.static_dir / self.factor_shift_image_template.format(
            model_dir=cell_model, gene=gene
        )


MGLIA_DEFAULT_CONFIG = DatasetConfig(
    name="mglia-regulators-mcquade-2026",
    static_dir=REPO_ROOT / "data" / "static",
    processed_dir=REPO_ROOT / "data" / "processed",
    model_tokens={
        "deg_table": {"iTF-MG": "iTF-MG", "iMG": "iMG"},
        "dap_table": {"iTF-MG": "iTF-MG", "iMG": "iMG"},
        "signature_shift": {"iTF-MG": "iTF", "iMG": "iMG"},
        "factor_shift": {"iTF-MG": "iTF", "iMG": "iMG"},
        "processed_rna": {"iTF-MG": "iTF", "iMG": "iMG"},
        "volcano_plot": {"iTF-MG": "iTF", "iMG": "iMG"},
        "kd_efficiency": {"iTF-MG": "iTF", "iMG": "iMG"},
    },
    deg_table_template="deg_tables/{model}_degs_{gene}_rna.csv",
    dap_table_template="dap_tables/{model}_daps_{gene}_protein.csv",
    signature_shift_template="shift_source_tables/percentile_df_figA_{model}_signatures.csv",
    factor_shift_template="shift_source_tables/percentile_df_figA_{model}_factors.csv",
    processed_rna_template="{model}_processed_cite_crop.h5mu",
    volcano_plot_template="volcano_plots/{model_dir}/png/{gene}_{modality}_volcano_{model}_labelled{suffix}.png",
    signature_shift_image_template="signature_shifts/{model_dir}/{gene}_s_percentile_shift_figA.jpeg",
    factor_shift_image_template="factor_shifts/{model_dir}/{gene}_f_percentile_shift_figA.jpeg",
    kd_eff_table_template="kd_efficiency_tables/knockdown_efficiency_{model}.csv",
    functional_readouts_template="reference/functional_readouts.csv",
)
