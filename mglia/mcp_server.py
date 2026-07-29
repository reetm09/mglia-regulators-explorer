"""MCP server exposing the mglia dataset to AI agents.

Provides two tools:
  - get_perturbation: full record for a KD × model combination
  - list_genes: all 31 knockdown gene names in the dataset

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

Usage (remote transport, for manual testing e.g. via the MCP Inspector):
    python -m mglia.mcp_server --transport streamable-http --port 8502
    # then, in another terminal:
    npx @modelcontextprotocol/inspector
    # Inspector UI: Transport = Streamable HTTP, URL = http://127.0.0.1:8502/mcp
"""

from __future__ import annotations

import argparse
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

mcp = FastMCP(
    name="mglia-regulators-explorer",
    instructions=(
        "You have access to the mglia dataset: CRISPRi perturbation data from "
        "McQuade et al. 2026 covering 31 transcription factor knockdowns "
        "in two human iPSC-derived microglia models (iTF-MG and iMG). "
        "Use get_perturbation to retrieve a full knockdown record, and list_genes "
        "to see all available knockdown gene names."
        "Before explaining any questions about the dataset, always call ReadMcpResourceTool"
        "on mglia://glossary first. Answer with exact text from glossary tool first."
    ),
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "mglia-regulators-explorer.onrender.com",
            "localhost:*",
            "127.0.0.1:*",
        ],
        allowed_origins=[
            "https://mglia-regulators-explorer.onrender.com",
            "http://localhost:*",
        ],
    ),
)


@mcp.tool()
def get_perturbation(gene: str, model: str | None = None) -> dict[str, Any]:
    """Return the full perturbation record for a knockdown gene in a cell model.

    Args:
        gene: Target gene name (e.g. 'ZNF532'). Must be one of the 31 KD genes:
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
                "SMAD3"
        model: Cell model — 'iTF-MG' (transcription-factor driven, 14-day protocol)
            or 'iMG' (cytokine driven, 25-day protocol). IMPORTANT: model is scoped to THIS query
            only. Do not infer or reuse a model that was specified for a different gene
            earlier in the same conversation. Each new gene request needs its own explicit
            model, stated for that gene. If the user's current message doesn't name a
            model for this gene, omit the param even if an earlier turn named one
            for a different gene.

    Returns:
        If `model` is given and matches a record: the full PerturbationRecord
        dict including:
        - n_cells, confidence, percent_knockdown, mixscale_response
        - signature_shifts: per-state delta_pctl and FDR (6 states)
        - top_degs: top 50 upregulated and downregulated genes
        - schpf_factors: top increased/decreased latent factors
        - functional_readouts: phagocytosis, lysosomal pH, cathepsin B (4 KDs only)
        - method_assumptions: methodological assumptions, flags, and caveats
        - discordances: mRNA/protein direction mismatches

        If `model` is omitted, or doesn't match any record for this gene: a
        dict with the following fields and shape:
        {"status": "needs_clarification",
        "gene": <gene>,
        "valid_models": ["iTF-MG", "iMG"],
        "message": "Ask the user which cell model they mean, then call "
        "get_perturbation again with model set to their answer. Do not "
        "guess or reuse a model from a different gene's query.",
        }
    """
    from mglia.agent import get_perturbation as _get

    return _get(gene, model)


@mcp.tool()
def list_genes() -> list[str]:
    """Return all knockdown gene names available in the dataset.

    Returns:
        Sorted list of all 31 KD gene names.
    """
    from mglia.agent import list_genes as _list

    return _list()


@mcp.resource("mglia://glossary")
def glossary() -> dict[str, Any]:
    """Reference definitions for microglial states, scHPF factors, nutrition label, mixscale,
    and method-assumptions methodology used throughout the mglia dataset. Fetch this before
    interpreting factor labels (e.g. 'gpnmb-high') or method_assumptions flags returned by
    get_perturbation or explanations that involve mixscale-derived DEGs and the dataset nutrition label.
    """
    from mglia.agent import get_glossary as _get

    return _get()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the microglia regulator MCP server."
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport to serve over. Defaults to stdio (for Claude Desktop). "
        "The promoted remote option is streamable-http.",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to for sse/streamable-http transports (ignored for stdio).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8502,
        help="Port to bind to for sse/streamable-http transports (ignored for stdio).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    mcp.settings.host = args.host
    mcp.settings.port = args.port
    mcp.run(transport=args.transport)
