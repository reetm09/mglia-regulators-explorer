"""Generate synthetic test MuData files for development.

Produces data/raw/itfmg.h5mu and data/raw/img.h5mu with the exact
obs/var/layer/uns/obsm structure of the real data, but with random values
and ~30 cells per perturbation (~960 cells total, ~200 genes, 20 proteins).

Usage:
    python scripts/create_test_h5mu.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import anndata as ad
import mudata as md
import numpy as np
import pandas as pd
import scipy.sparse as sp

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from mglia.constants import ALL_KD_GENES, SCHPF_FACTORS  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

N_CELLS_PER_GROUP = 30
N_GENES = 200
N_PROTEINS = 20
N_PCA_DIMS = 50
RNG = np.random.default_rng(42)


# ---------------------------------------------------------------------------
# Gene and protein names
# ---------------------------------------------------------------------------

def _make_gene_names(n: int) -> list[str]:
    """Generate synthetic gene names."""
    prefixes = ["GENE", "MT-GENE", "RIBO-GENE", "HB-GENE"]
    names = []
    for i in range(n):
        prefix = prefixes[i % len(prefixes)]
        names.append(f"{prefix}{i + 1:04d}")
    return names


def _make_protein_names(n: int) -> list[str]:
    """Generate synthetic protein names matching the prot modality."""
    return [f"PROT{i + 1:03d}" for i in range(n)]


# ---------------------------------------------------------------------------
# Build one MuData object
# ---------------------------------------------------------------------------

def _build_mdata(model_name: str) -> md.MuData:
    """Construct a synthetic MuData object matching the real data schema.

    Args:
        model_name: One of "itfmg" or "img".

    Returns:
        MuData with 'rna' and 'prot' modalities.
    """
    groups = ALL_KD_GENES + ["NTC"]
    n_obs = len(groups) * N_CELLS_PER_GROUP

    gene_names = _make_gene_names(N_GENES)
    protein_names = _make_protein_names(N_PROTEINS)

    # ------------------------------------------------------------------
    # Build obs DataFrame for RNA modality
    # ------------------------------------------------------------------

    perturbed_genes = []
    guides = []
    for g in groups:
        guide = f"{g}_sg1" if g != "NTC" else "NTC"
        perturbed_genes.extend([g] * N_CELLS_PER_GROUP)
        guides.extend([guide] * N_CELLS_PER_GROUP)

    obs = pd.DataFrame(index=[f"cell_{i:05d}" for i in range(n_obs)])
    obs["guide"] = guides
    obs["perturbed_guide"] = guides
    obs["perturbed_gene"] = perturbed_genes
    obs["mt_outlier"] = False

    # QC metrics
    obs["n_genes_by_counts"] = RNG.integers(500, 3000, n_obs).astype(float)
    obs["log1p_n_genes_by_counts"] = np.log1p(obs["n_genes_by_counts"])
    obs["total_counts"] = RNG.integers(1000, 20000, n_obs).astype(float)
    obs["log1p_total_counts"] = np.log1p(obs["total_counts"])
    for pct_col in ["pct_counts_in_top_50_genes", "pct_counts_in_top_100_genes",
                    "pct_counts_in_top_200_genes", "pct_counts_in_top_500_genes"]:
        obs[pct_col] = RNG.uniform(0.1, 0.9, n_obs)
    obs["total_counts_mt"] = RNG.integers(10, 200, n_obs).astype(float)
    obs["log1p_total_counts_mt"] = np.log1p(obs["total_counts_mt"])
    obs["pct_counts_mt"] = obs["total_counts_mt"] / obs["total_counts"] * 100
    obs["total_counts_ribo"] = RNG.integers(50, 500, n_obs).astype(float)
    obs["log1p_total_counts_ribo"] = np.log1p(obs["total_counts_ribo"])
    obs["pct_counts_ribo"] = obs["total_counts_ribo"] / obs["total_counts"] * 100
    obs["total_counts_hb"] = RNG.integers(0, 10, n_obs).astype(float)
    obs["log1p_total_counts_hb"] = np.log1p(obs["total_counts_hb"])
    obs["pct_counts_hb"] = obs["total_counts_hb"] / obs["total_counts"] * 100

    # Leiden clusters
    n_leiden_clusters = {"leiden_0.5": 5, "leiden_0.8": 8, "leiden_1.0": 10}
    for col, n_clust in n_leiden_clusters.items():
        obs[col] = pd.Categorical(
            RNG.integers(0, n_clust, n_obs).astype(str)
        )

    # Mixscale score
    obs["mixscale_score"] = RNG.uniform(0.0, 1.0, n_obs)

    # scHPF factors — f6, f12, f13 deliberately absent (matches real data)
    for f in SCHPF_FACTORS:
        obs[f] = RNG.uniform(0.0, 1.0, n_obs)

    # UCell scores
    ucell_cols = [
        "interferon_score_ucell",
        "chemokine_score_ucell",
        "homeostatic_score_ucell",
        "proliferative_score_ucell",
        "dam_score_ucell",
        "antigen_presenting_score_ucell",
        "lipid_dam_score_ucell",
        "dam_unique_score_ucell",
        "lipid_dam_unique_score_ucell",
        "dam_extra_score_ucell",
        "dam_extra_unique_score_ucell",
    ]
    for col in ucell_cols:
        obs[col] = RNG.uniform(0.0, 1.0, n_obs)

    # ------------------------------------------------------------------
    # Build var DataFrame for RNA modality
    # ------------------------------------------------------------------

    n_mt = N_GENES // 10
    n_ribo = N_GENES // 10
    n_hb = 3
    var_rna = pd.DataFrame(index=gene_names)
    var_rna["mt"] = [i < n_mt for i in range(N_GENES)]
    var_rna["ribo"] = [(n_mt <= i < n_mt + n_ribo) for i in range(N_GENES)]
    var_rna["hb"] = [(n_mt + n_ribo <= i < n_mt + n_ribo + n_hb) for i in range(N_GENES)]
    var_rna["n_cells_by_counts"] = RNG.integers(100, n_obs, N_GENES).astype(float)
    var_rna["mean_counts"] = RNG.uniform(0.1, 10.0, N_GENES)
    var_rna["log1p_mean_counts"] = np.log1p(var_rna["mean_counts"])
    var_rna["pct_dropout_by_counts"] = RNG.uniform(0.0, 1.0, N_GENES)
    var_rna["total_counts"] = RNG.integers(1000, 100000, N_GENES).astype(float)
    var_rna["log1p_total_counts"] = np.log1p(var_rna["total_counts"])
    var_rna["highly_variable"] = RNG.random(N_GENES) > 0.7
    var_rna["means"] = var_rna["mean_counts"]
    var_rna["dispersions"] = RNG.uniform(0.5, 5.0, N_GENES)
    var_rna["dispersions_norm"] = RNG.uniform(-2.0, 2.0, N_GENES)

    # ------------------------------------------------------------------
    # Build expression matrices
    # ------------------------------------------------------------------

    raw_counts = sp.random(n_obs, N_GENES, density=0.1, format="csr", random_state=42)
    raw_counts.data = RNG.integers(1, 50, raw_counts.nnz).astype(np.float32)

    log1p_data = raw_counts.copy()
    log1p_data.data = np.log1p(log1p_data.data)

    # ------------------------------------------------------------------
    # Build RNA AnnData
    # ------------------------------------------------------------------

    adata_rna = ad.AnnData(
        X=log1p_data,
        obs=obs,
        var=var_rna,
    )
    adata_rna.layers["raw_counts"] = raw_counts
    adata_rna.layers["log1p"] = log1p_data

    # obsm
    adata_rna.obsm["X_pca"] = RNG.standard_normal((n_obs, N_PCA_DIMS)).astype(np.float32)
    adata_rna.obsm["X_umap"] = RNG.standard_normal((n_obs, 2)).astype(np.float32)

    # varm
    adata_rna.varm["PCs"] = RNG.standard_normal((N_GENES, N_PCA_DIMS)).astype(np.float32)

    # uns
    adata_rna.uns["name"] = model_name
    adata_rna.uns["log1p"] = {"base": None}
    adata_rna.uns["pca"] = {"variance_ratio": RNG.random(N_PCA_DIMS).tolist()}
    adata_rna.uns["umap"] = {"params": {}}
    adata_rna.uns["leiden_1.0_cluster"] = {
        str(i): f"cluster_{i}" for i in range(10)
    }
    # Minimal guide_colors and leiden_colors
    adata_rna.uns["guide_colors"] = {}
    adata_rna.uns["leiden_1.0_colors"] = [
        f"#{RNG.integers(0, 0xFFFFFF):06x}" for _ in range(10)
    ]
    # Minimal neighbors uns entry
    adata_rna.uns["neighbors"] = {"connectivities_key": "connectivities"}

    # obsp — sparse connectivity and distance matrices
    import scipy.sparse as _sp
    conn = _sp.eye(n_obs, format="csr") * 0.5
    adata_rna.obsp["connectivities"] = conn
    adata_rna.obsp["distances"] = conn.copy()

    # ------------------------------------------------------------------
    # Build protein AnnData
    # ------------------------------------------------------------------

    var_prot = pd.DataFrame(index=protein_names)
    var_prot["gene_ids"] = [f"ENSP{i:011d}" for i in range(N_PROTEINS)]
    var_prot["feature_types"] = "Antibody Capture"
    var_prot["genome"] = "GRCh38"
    var_prot["old_gene_ids"] = var_prot["gene_ids"]

    prot_counts = RNG.integers(0, 500, (n_obs, N_PROTEINS)).astype(np.float32)
    prot_lognorm = np.log1p(prot_counts / prot_counts.sum(axis=1, keepdims=True) * 1e4)

    obs_prot = obs[[]].copy()  # same cell index, no extra columns

    adata_prot = ad.AnnData(
        X=sp.csr_matrix(prot_lognorm),
        obs=obs_prot,
        var=var_prot,
    )
    adata_prot.layers["counts"] = sp.csr_matrix(prot_counts)
    adata_prot.layers["log1pnorm"] = sp.csr_matrix(prot_lognorm)
    adata_prot.uns["log1p"] = {"base": None}

    # ------------------------------------------------------------------
    # Assemble MuData
    # ------------------------------------------------------------------

    mdata = md.MuData({"rna": adata_rna, "prot": adata_prot})
    return mdata


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Generate both test h5mu files."""
    out_dir = ROOT / "data" / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    for model_name, filename in [("itfmg", "itfmg"), ("img", "img")]:
        print(f"Building {filename}.h5mu ...", end=" ", flush=True)
        mdata = _build_mdata(model_name)
        out_path = out_dir / f"{filename}.h5mu"
        mdata.write_h5mu(out_path)
        print(f"saved ({mdata.n_obs} cells × {mdata.n_vars} vars) → {out_path}")


if __name__ == "__main__":
    main()
