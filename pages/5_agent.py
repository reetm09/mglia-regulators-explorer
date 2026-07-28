"""Agent access page — MCP server reference and live JSON query interface."""

import json

import streamlit as st
from mglia.constants import ALL_KD_GENES, CELL_MODELS
from mglia.ui_components import render_global_styles

render_global_styles()

st.title("Agentic Exploring")

st.markdown(
    """
    This page is designed for **AI agents** (Claude, GPT-4, etc.) connecting to the
    mglia dataset via the [Model Context Protocol (MCP)](https://modelcontextprotocol.io).
    The MCP server exposes structured, machine-readable access to all 62 perturbation records
    and benchmark tasks — no web scraping, no parsing HTML.
    """
)

# ---------------------------------------------------------------------------
# Connection instructions
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Connect via MCP")

tab_local, tab_remote = st.tabs(["Local (Claude Desktop)", "Remote (streamable-HTTP)"])

with tab_local:
    st.markdown("Add this to your `claude_desktop_config.json`:")
    st.code(
        json.dumps(
            {
                "mcpServers": {
                    "mglia": {
                        "command": "python",
                        "args": ["-m", "mglia.mcp_server"],
                        "cwd": "/path/to/mglia-regulators-dashboard",
                    }
                }
            },
            indent=2,
        ),
        language="json",
    )
    st.caption(
        "Replace `/path/to/mglia-regulators-dashboard` with the absolute path to this repo. "
        "Then restart Claude Desktop — the mglia tools will appear automatically."
    )

with tab_remote:
    st.markdown("Start the server over streamable-HTTP:")
    st.code(
        "python -m mglia.mcp_server --transport streamable-http --port 8502",
        language="bash",
    )
    st.markdown("Then connect with the MCP Inspector to test manually:")
    st.code("npx @modelcontextprotocol/inspector", language="bash")
    st.caption(
        "In the Inspector UI: Transport = Streamable HTTP, "
        "URL = http://127.0.0.1:8502/mcp. Local testing only — not hosted remotely."
    )

# ---------------------------------------------------------------------------
# Tool reference
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Available tools")

with st.expander("get_perturbation(gene, model)", expanded=True):
    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.markdown("**Description**")
        st.markdown(
            "Return the full perturbation record for a knockdown gene in a cell model. "
            "Includes signature shifts across 6 microglial states, top DEGs, scHPF factors, "
            "functional readouts, and method assumptions & caveats."
        )
        st.markdown("**Input schema**")
        st.code(
            json.dumps(
                {
                    "gene": "string — one of 31 KD genes, e.g. 'ZNF532'",
                    "model": "string — 'iTF-MG' or 'iMG'",
                },
                indent=2,
            ),
            language="json",
        )
    with col_r:
        st.markdown("**Example response (abbreviated)**")
        st.code(
            json.dumps(
                {
                    "perturbation": "ZNF532",
                    "cell_model": "iTF-MG",
                    "n_cells": 312,
                    "confidence": "high",
                    "signature_shifts": {
                        "disease_associated": {"delta_pctl": 14.2, "fdr": 0.001},
                        "homeostatic": {"delta_pctl": -8.7, "fdr": 0.003},
                    },
                    "method_assumptions": {"low_cell_count_warning": False, "flags": []},
                },
                indent=2,
            ),
            language="json",
        )

with st.expander("list_genes()"):
    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.markdown("**Description**")
        st.markdown("Return all knockdown gene names available in the dataset.")
        st.markdown("**Input schema**")
        st.code(json.dumps({}, indent=2), language="json")
    with col_r:
        st.markdown("**Example response**")
        genes = sorted(ALL_KD_GENES)
        example_genes = genes[:3] + ["..."] + genes[-3:]
        st.code(json.dumps(example_genes, indent=2), language="json")

# with st.expander("get_split(task) (not currently enabled)"):
#     col_l, col_r = st.columns([1, 1])
#     with col_l:
#         st.markdown("**Description**")
#         st.caption("This tool is disabled in mglia/mcp_server.py — kept for reference.")
#         st.markdown(
#             "Return the train/test split definition for a benchmark task, including "
#             "input feature specs, prediction targets, and metric descriptions."
#         )
#         st.markdown("**Input schema**")
#         st.code(
#             json.dumps(
#                 {
#                     "task": (
#                         "string — one of 'perturbation_prediction', "
#                         "'cross_model_generalization', 'dose_response', "
#                         "'multistate_combinatorial'"
#                     )
#                 },
#                 indent=2,
#             ),
#             language="json",
#         )
#     with col_r:
#         st.markdown("**Example response**")
#         st.code(
#             json.dumps(
#                 {
#                     "task_name": "perturbation_prediction",
#                     "train_genes": ["BHLHE40", "BRD4", "..."],
#                     "test_genes": ["ZNF532", "PRDM1", "STAT2", "DNMT1", "ZNF644", "ZNF783"],
#                     "primary_metric": "pearson_r",
#                     "metrics": ["pearson_r", "direction_accuracy"],
#                 },
#                 indent=2,
#             ),
#             language="json",
#         )

# with st.expander("evaluate_predictions(predictions, task) (not currently enabled)"):
#     col_l, col_r = st.columns([1, 1])
#     with col_l:
#         st.markdown("**Description**")
#         st.caption("This tool is disabled in mglia/mcp_server.py — kept for reference.")
#         st.markdown(
#             "Score model predictions against the held-out test set. "
#             "Returns per-metric scores and an overall weighted composite."
#         )
#         st.markdown("**Input schema**")
#         st.code(
#             json.dumps(
#                 {
#                     "predictions": {
#                         "ZNF532": {
#                             "homeostatic": -8.5,
#                             "disease_associated": 12.1,
#                             "lipid_rich": 3.2,
#                             "antigen_presenting": -5.0,
#                             "interferon_responsive": 0.8,
#                             "chemokine": 1.1,
#                         },
#                         "...": "...",
#                     },
#                     "task": "perturbation_prediction",
#                 },
#                 indent=2,
#             ),
#             language="json",
#         )
#     with col_r:
#         st.markdown("**Example response**")
#         st.code(
#             json.dumps(
#                 {
#                     "pearson_r": 0.42,
#                     "direction_accuracy": 0.71,
#                     "overall": 0.55,
#                 },
#                 indent=2,
#             ),
#             language="json",
#         )

# ---------------------------------------------------------------------------
# Resource reference
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Available resources")

with st.expander("mglia://glossary", expanded=True):
    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.markdown("**Description**")
        st.markdown(
            "Reference definitions for microglial states, scHPF factors, and "
            "nutrition label concepts used throughout the mglia dataset. "
            "Agents should fetch this resource before interpreting factor labels "
            "(e.g. 'gpnmb-high') or `method_assumptions` flags returned by "
            "`get_perturbation`."
        )
        st.caption(
            "The MCP server's system instructions require agents to read this "
            "resource before answering any question about the dataset to anchor responses."
        )
    with col_r:
        st.markdown("**Example response (abbreviated)**")
        st.code(
            json.dumps(
                {
                    "states": {
                        "disease_associated": {
                            "display": "Disease-associated (DAM)",
                            "marker": "CD9",
                            "reliable": True,
                        },
                        "chemokine": {
                            "display": "Chemokine",
                            "marker": "CCL13",
                            "reliable": False,
                            "reliability_note": (
                                "Across our larger FACS screen, TF knockdowns appear to "
                                "perturb the chemokine state less than other states..."
                            ),
                        },
                    },
                    "schpf": {
                        "description": "scHPF latent factor projections...",
                        "factor_labels": {"F26": "GPNMBhigh"},
                        "methodology": {"...": "..."},
                    },
                    "method_assumptions": {
                        "description": "Per-method assumptions and violation conditions...",
                        "registry": {"...": "..."},
                    },
                },
                indent=2,
            ),
            language="json",
        )

# ---------------------------------------------------------------------------
# Live JSON query
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Live JSON query")

st.caption(
    "Query a perturbation record directly. "
    "Requires data/perturbations.json to be generated."
)

q_col_a, q_col_b = st.columns([2, 1])

with q_col_a:
    query_gene = st.selectbox(
        "Gene",
        options=sorted(ALL_KD_GENES),
        index=sorted(ALL_KD_GENES).index("ZNF532"),
    )

with q_col_b:
    query_model = st.radio("Model", options=list(CELL_MODELS.keys()), horizontal=True)

if st.button("Fetch record"):
    with st.spinner("Loading record..."):
        try:
            from mglia.agent import get_perturbation

            record = get_perturbation(query_gene, query_model)
            st.json(record)
        except NotImplementedError:
            st.warning(
                "Record lookup is not implemented yet. "
                # "Run `make generate` after implementing `mglia/compute.py` and "
                # "`scripts/generate_records.py`."
            )
        except FileNotFoundError:
            st.error(
                "data/perturbations.json not found."
            )  # sRun `make generate` first.")
        except KeyError as e:
            st.error(f"Record not found: {e}")

# ---------------------------------------------------------------------------
# Downloads
# ---------------------------------------------------------------------------

# st.markdown("---")
# st.subheader("Downloads")

# dl1, dl2 = st.columns(2)

# with dl1:
#     st.download_button(
#         label="Download perturbations.json",
#         data="[]",  # TODO: real file
#         file_name="perturbations.json",
#         mime="application/json",
#         disabled=True,
#         help="Run `make generate` to produce this file first.",
#     )

# with dl2:
#     st.download_button(
#         label="Download benchmark_splits.json",
#         data="{}",  # TODO: real file
#         file_name="benchmark_splits.json",
#         mime="application/json",
#         disabled=True,
#         help="Run `make generate` to produce this file first.",
#     )
