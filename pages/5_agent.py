"""Agent access page — MCP server reference and live JSON query interface."""

import json
from pathlib import Path

import streamlit as st
from mglia.constants import ALL_KD_GENES, CELL_MODELS
from mglia.ui_components import render_global_styles

render_global_styles()

APP_DIR = Path(__file__).resolve().parent.parent
IMG_DIR = APP_DIR / "data" / "static" / "reference"

st.title("Agentic Exploring")

st.markdown(
    """
    This page is designed for **AI agents** (Claude, GPT-4, etc.) connecting to the
    mglia dataset via the [Model Context Protocol (MCP)](https://modelcontextprotocol.io).
    The MCP server exposes structured, machine-readable access to all 62 perturbation records.
    """
)

# ---------------------------------------------------------------------------
# Connection instructions
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Connect via MCP")

#tab_local, tab_remote = st.tabs(["Local (Claude Desktop)", "Remote (streamable-HTTP)"])
tab_desktop, tab_code, tab_local = st.tabs(["Claude Desktop or Claude Web",
                                            "Claude Code",
                                            "Local"])

with tab_desktop:
    url_1 = "https://claude.ai"
    st.markdown("1. Open Claude Web [https://claude.ai](%s) or Claude Desktop" % (url_1))
    st.markdown("2. Navigate to `Add Connector` Button")
    st.image(str(IMG_DIR / "navigate_to_add_connector.png"),
             caption="Click `Add custom connector`",
             width="stretch")
    url_2 = "https://mglia-regulators-explorer.onrender.com/mcp"
    st.markdown("3. Choose any name and enter MCP Server Link: [https://mglia-regulators-explorer.onrender.com/mcp](%s)" % url_2)
    st.image(str(IMG_DIR / "add_custom_connector_details.png"),
                 caption="Click `Add` once finished with entering details",
                 width="stretch")
    st.markdown("4. Ask Away! It may ask for permissions when you start asking questions. You can click **Accept** when it asks for if it can use `get_perturbation` or `list_genes`")
 
with tab_code:
    st.markdown("1. Open Terminal before running `claude`")
    st.markdown("2. Run: ")
    st.code("claude mcp add --transport http mglia https://mglia-regulators-explorer.onrender.com/mcp")
    st.markdown("3. Use this to check if server is added Claude Code environment:")
    st.code("# List all configured servers\n"
            "claude mcp list\n"
            "# Get info about specific server\n"
            "claude mcp get mglia")
    st.code("# Check within Claude\n"
            "/mcp")
    st.markdown("4. Ask Away!")

with tab_local:
    st.markdown("1. Clone Github Repo")
    st.code("git clone https://github.com/reetm09/mglia-regulators-explorer.git \n" 
            "cd mglia-regulators-explorer", language="git")
    st.markdown("2. Start Virtual Environment")
    st.code("uv venv .mglia-env")
    st.code("source .mglia-env/bin/activate")
    st.markdown("3. Install dependencies from  `requirements.txt`")
    st.code("uv pip install -r requirements.txt")
    
    st.markdown("4. Installing MCP Server")
    
    #st.expander("4a. Option 1: Claude Desktop Configuration File")
    with st.expander("4a. Option 1: Claude Desktop Configuration File", expanded=True):
        st.markdown("Add this to your `claude_desktop_config.json`:")
        st.code(
            json.dumps(
                {
                    "mcpServers": {
                        "mglia": {
                            "command": "python",
                            "args": ["-m", "mglia.mcp_server"],
                            "cwd": "/path/to/mglia-regulators-explorer/",
                        }
                    }
                },
                indent=2,
            ),
            language="json",
        )
        st.caption(
            "Then restart Claude Desktop. The server will appear automatically."
        )
    
    #st.expander("4b. Option 2: Start the server over streamable-HTTP")
    with st.expander("4b. Option 2: Start the server over streamable-HTTP", expanded=True):
        st.markdown("Run:")
        st.code(
            "python -m mglia.mcp_server --transport streamable-http --port 8502",
            language="bash",
        )
        st.markdown("Then connect with the MCP Inspector to test manually:")
        st.code("npx @modelcontextprotocol/inspector", language="bash")
        st.caption(
            "In the Inspector UI: Transport = Streamable HTTP, "
            "URL = http://127.0.0.1:8502/mcp."
        )


# ---------------------------------------------------------------------------
# Example Questions
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Example Questions to Ask")
st.markdown("""
            - What are the Top DEGs in PRDM1 in iMG?
            - What states does STAT2 affect in iTF-MG?
            - Which perturbations regulate the interferon state?
            - Compare ZN532 to PRDM1
            - Which genes regulate phagocytosis?
            - Which genes have both transcriptomic and experimental evidence?
            - What are the high confidence perturbations?
            """)

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
                    "cell_model": "iMG",
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
            )
        except FileNotFoundError:
            st.error(
                "data/perturbations.json not found."
            ) 
        except KeyError as e:
            st.error(f"Record not found: {e}")
