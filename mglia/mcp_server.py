"""MCP server exposing the mglia dataset to AI agents.

Provides three tools:
  - get_perturbation: full record for a KD × model combination
  - get_split: benchmark task split definition
  - evaluate_predictions: score model predictions against held-out test set

Usage (stdio, for Claude Desktop):
    python -m mglia.mcp_server
    # or:
    python mglia/mcp_server.py

Claude Desktop config (~/.config/claude/claude_desktop_config.json):
    {
      "mcpServers": {
        "mglia": {
          "command": "python",
          "args": ["-m", "mglia.mcp_server"],
          "cwd": "/path/to/mglia-regulators-dashboard"
        }
      }
    }
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="mglia-explorer",
    instructions=(
        "You have access to the mglia dataset: CRISPRi perturbation data from "
        "McQuade, Mishra et al. 2025 covering 31 transcription factor knockdowns "
        "in two human iPSC-derived microglia models (iTF-MG and iMG). "
        "Use get_perturbation to retrieve a full knockdown record, get_split to "
        "inspect benchmark task definitions, and evaluate_predictions to score "
        "model predictions against the held-out test set."
    ),
)


@mcp.tool()
def get_perturbation(gene: str, model: str) -> dict[str, Any]:
    """Return the full perturbation record for a knockdown gene in a cell model.

    Args:
        gene: Target gene name (e.g. 'ZNF532'). Must be one of the 31 KD genes:
            BHLHE40, BRD4, CHD4, EGR1, EZH2, HDAC1, IRF1, IRF3, IRF8, KLF4,
            MED12, MEF2A, MEIS1, NFKB1, NR4A1, PPARG, RUNX1, SMAD3, SP1, SPI1,
            TET2, TRIM28, ZEB1, ZNF148, ZNF281 (train) and
            ZNF532, PRDM1, STAT2, DNMT1, ZNF644, ZNF783 (test — held out).
        model: Cell model — 'iTF-MG' (transcription-factor driven, 14-day protocol)
            or 'iMG' (cytokine driven, 25-day protocol).

    Returns:
        Full PerturbationRecord dict including:
        - n_cells, confidence, kd_efficiency, mixscale_response, benchmark_split
        - signature_shifts: per-state delta_pctl and FDR (6 states)
        - top_degs: top 50 upregulated and downregulated genes
        - schpf_factors: top increased/decreased latent factors
        - functional_readouts: phagocytosis, lysosomal pH, cathepsin B (4 KDs only)
        - assumption_audit: methodological flags and warnings
        - discordances: mRNA/protein direction mismatches
    """
    from mglia.agent import get_perturbation as _get
    return _get(gene, model)


@mcp.tool()
def get_split(task: str) -> dict[str, Any]:
    """Return the benchmark split definition for a task.

    Args:
        task: One of:
            'perturbation_prediction' — predict 6-state shifts for held-out KDs
            'cross_model_generalization' — train on iTF-MG, evaluate on iMG
            'dose_response' — predict per-Mixscale-tier signature shifts
            'multistate_combinatorial' — predict 6-state direction vector

    Returns:
        Dict with:
        - train_genes: list of gene names used for training
        - test_genes: list of held-out gene names
        - description: plain-language task description
        - input_features: list of input feature names
        - prediction_targets: list of output target names
        - metrics: list of evaluation metric names
        - primary_metric: the headline metric name
    """
    from mglia.benchmark import get_split as _get
    return _get(task)


@mcp.tool()
def evaluate_predictions(predictions: dict[str, Any], task: str) -> dict[str, float]:
    """Score model predictions against the held-out test set.

    Args:
        predictions: Dict mapping test gene names to predicted state shift vectors.
            Format depends on task:
            - perturbation_prediction / multistate_combinatorial:
                { "ZNF532": { "homeostatic": -12.5, "disease_associated": 8.3, ... }, ... }
            - dose_response:
                { "ZNF532": { "bottom": {...}, "middle": {...}, "top": {...} }, ... }
            - cross_model_generalization:
                Same as perturbation_prediction but evaluated on iMG genes.
        task: Task name (same options as get_split).

    Returns:
        Dict with per-metric scores and an 'overall' weighted composite score.
        Example: { "pearson_r": 0.42, "direction_accuracy": 0.71, "overall": 0.55 }
    """
    from mglia.benchmark import score_predictions as _score
    import pandas as pd
    pred_df = pd.DataFrame(predictions).T
    return _score(pred_df, task)


if __name__ == "__main__":
    mcp.run()
