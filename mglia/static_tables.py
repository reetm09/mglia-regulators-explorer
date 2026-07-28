"""Readers for precomputed static tables (DEG/DAP/shift CSVs) and processed h5mu.

These are the primary data source for record generation — `generate_records.py`
builds `PerturbationRecord`s from these tables directly, without needing to compute
anything from single-cell data itself.
"""

from __future__ import annotations

import functools
import re
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from mglia.dataset_config import DatasetConfig

if TYPE_CHECKING:
    pass


def discover_genes(config: DatasetConfig, cell_model: str) -> list[str]:
    """Discover the gene panel from DEG table filenames for a cell model.

    Args:
        config: Dataset configuration.
        cell_model: Cell model key (e.g. "iTF-MG" or "iMG").

    Returns:
        Sorted list of gene names. If config.gene_list is set, returns that list
        directly instead of globbing DEG table filenames.
    """
    if config.gene_list is not None:
        return sorted(config.gene_list)

    token = config.model_token("deg_table", cell_model)
    deg_dir = (config.static_dir / config.deg_table_template).parent
    pattern = re.compile(rf"^{re.escape(token)}_degs_(.+)_rna\.csv$")
    genes = []
    for path in deg_dir.glob(f"{token}_degs_*_rna.csv"):
        m = pattern.match(path.name)
        if m:
            genes.append(m.group(1))
    return sorted(genes)


def read_deg_table(config: DatasetConfig, cell_model: str, gene: str) -> pd.DataFrame:
    """Load the DEG table CSV for a gene/model.

    Args:
        config: Dataset configuration.
        cell_model: Cell model key.
        gene: Target gene name.

    Returns:
        DataFrame with columns config.gene_col, config.log2fc_col, config.fdr_col
        (plus any others present in the file).

    Raises:
        FileNotFoundError: If the DEG table does not exist.
    """
    path = config.deg_table_path(cell_model, gene)
    return pd.read_csv(path, index_col=0)


def read_dap_table(config: DatasetConfig, cell_model: str, gene: str) -> pd.DataFrame:
    """Load the DAP (differential protein abundance) table CSV for a gene/model.

    Args:
        config: Dataset configuration.
        cell_model: Cell model key.
        gene: Target gene name.

    Returns:
        DataFrame with the same column shape as the DEG table.

    Raises:
        FileNotFoundError: If the DAP table does not exist.
    """
    path = config.dap_table_path(cell_model, gene)
    return pd.read_csv(path, index_col=0)


@functools.lru_cache(maxsize=None)
def _read_shift_table_cached(path_str: str) -> pd.DataFrame:
    return pd.read_csv(path_str, index_col=0)


def read_signature_shift_table(config: DatasetConfig, cell_model: str) -> pd.DataFrame:
    """Load the whole-model UCell signature percentile-shift table.

    Args:
        config: Dataset configuration.
        cell_model: Cell model key.

    Returns:
        DataFrame with one row per (perturbed_guide, Factor) combination, columns
        including perturbed_gene, Factor, PctShift, qval.

    Raises:
        FileNotFoundError: If the table does not exist.
    """
    path = config.signature_shift_path(cell_model)
    return _read_shift_table_cached(str(path))


def read_factor_shift_table(config: DatasetConfig, cell_model: str) -> pd.DataFrame:
    """Load the whole-model scHPF factor percentile-shift table.

    Args:
        config: Dataset configuration.
        cell_model: Cell model key.

    Returns:
        DataFrame with the same shape as the signature shift table, but Factor is
        a descriptive scHPF factor label instead of a UCell score column name.

    Raises:
        FileNotFoundError: If the table does not exist.
    """
    path = config.factor_shift_path(cell_model)
    return _read_shift_table_cached(str(path))


@functools.lru_cache(maxsize=None)
def _read_kd_table_cached(path_str: str) -> pd.DataFrame:
    return pd.read_csv(path_str, index_col=0)


def read_kd_efficiency_table(config: DatasetConfig, cell_model: str) -> pd.DataFrame:
    """Load the whole-model transcriptomic knockdown-efficiency table.

    Args:
        config: Dataset configuration.
        cell_model: Cell model key.

    Returns:
        DataFrame with one row per gene, columns including config.kd_gene_col,
        config.kd_transcriptomic_ratio, config.kd_ntc_mean_expr,
        config.kd_ntc_frac_expr, config.kd_num_guides.

    Raises:
        FileNotFoundError: If the table does not exist.
    """
    path = config.kd_table_path(cell_model)
    return _read_kd_table_cached(str(path))


@functools.lru_cache(maxsize=None)
def _read_rna_obs_cached(path_str: str) -> pd.DataFrame:
    """Load only the rna modality's obs DataFrame from an h5mu file (no X)."""
    import mudata as md

    mdata = md.read_h5mu(path_str, backed="r")
    return mdata["rna"].obs.copy()


def _rna_obs(config: DatasetConfig, cell_model: str) -> pd.DataFrame:
    path = config.processed_rna_path(cell_model)
    return _read_rna_obs_cached(str(path))


def read_cell_counts(config: DatasetConfig, cell_model: str) -> pd.Series:
    """Return per-gene cell counts from the processed h5mu file for a cell model.

    Args:
        config: Dataset configuration.
        cell_model: Cell model key.

    Returns:
        Series indexed by perturbed_gene (including "NTC"), values are cell counts.

    Raises:
        FileNotFoundError: If the processed h5mu file does not exist.
    """
    obs = _rna_obs(config, cell_model)
    return obs["perturbed_gene"].value_counts()


def get_volcano_plot_path(
    config: DatasetConfig, cell_model: str, gene: str, modality: str
) -> Path | None:
    """Path to a per-gene volcano plot SVG, or None if it doesn't exist on disk.

    Args:
        config: Dataset configuration.
        cell_model: Cell model key.
        gene: Target gene name.
        modality: "rna" or "prot".

    Returns:
        Path to the SVG, or None if the file is missing.
    """
    path = config.volcano_plot_path(cell_model, gene, modality)
    return path if path.exists() else None


def get_signature_shift_image_path(
    config: DatasetConfig, cell_model: str, gene: str
) -> Path | None:
    """Path to the per-gene signature point-plot JPEG, or None if missing.

    Args:
        config: Dataset configuration.
        cell_model: Cell model key.
        gene: Target gene name.

    Returns:
        Path to the JPEG, or None if the file is missing.
    """
    path = config.signature_shift_image_path(cell_model, gene)
    return path if path.exists() else None


def get_factor_shift_image_path(
    config: DatasetConfig, cell_model: str, gene: str
) -> Path | None:
    """Path to the per-gene scHPF factor point-plot JPEG, or None if missing.

    Args:
        config: Dataset configuration.
        cell_model: Cell model key.
        gene: Target gene name.

    Returns:
        Path to the JPEG, or None if the file is missing.
    """
    path = config.factor_shift_image_path(cell_model, gene)
    return path if path.exists() else None


def read_mixscale_scores(
    config: DatasetConfig, cell_model: str, gene: str
) -> pd.Series:
    """Return per-cell Mixscale scores for a gene's knockdown cells.

    Args:
        config: Dataset configuration.
        cell_model: Cell model key.
        gene: Target gene name.

    Returns:
        Series of Mixscale scores for cells where perturbed_gene == gene.

    Raises:
        FileNotFoundError: If the processed h5mu file does not exist.
    """
    obs = _rna_obs(config, cell_model)
    return obs.loc[obs["perturbed_gene"] == gene, "mixscale_score"]
