"""Streamlit entrypoint for the Microglia State Regulator Explorer."""

import streamlit as st
from mglia.ui_components import _pill, render_global_styles

_TAG_HUMAN_COLOR = "#3D7AB3"
_TAG_AGENT_COLOR = "#8A5DBF"

st.set_page_config(
    layout="wide",
    page_title="mglia explorer",
    page_icon="🧠",
)

render_global_styles()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## microglia regulators explorer")
    # TODO: add lab logo image
    st.markdown("---")
    st.markdown("**Data version:** v0.1-dev")

# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------

st.title("Microglia State Regulator Explorer")

st.markdown(
    """
    This tool lets you explore CRISPRi perturbation data from McQuade et al. 2026,
    covering 31 transcription factor knockdowns across two human iPSC-derived microglia models
    (iTF-MG and iMG). Each perturbation record includes signature shifts across 6 microglial
    states, top differentially expressed genes, scHPF factor activity, functional assay readouts,
    and a per-record assumption audit. We also have a dataset 'nutrition' label to encourage accessibility
    and transparency of perturbation datasets. You can explore this dataset through the Explore, Compare,
    and Nutrition Pages, or have Claude do it directly by following the instructions on the Agent Page.
    """
)

# ---------------------------------------------------------------------------
# Page cards — 2x2 grid
# ---------------------------------------------------------------------------

row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

with row1_col1:
    st.markdown("### 🔬 Explore Perturbations")
    st.markdown(_pill("Human", _TAG_HUMAN_COLOR), unsafe_allow_html=True)
    st.markdown(
        "Explore how each transcription factor knockdown shifts microglial activation states across models. "
        "Inspect transcriptomic and experimental data highlighted in the paper including signature shifts, factor shifts, "
        "RNA and Protein volcano plots and more. You can also "
        "inspect functional readouts, and download DEG lists."
    )
    st.page_link("pages/2_explore.py", label="Open Explorer →")

with row1_col2:
    st.markdown("### ⚖️ Compare Perturbations")
    st.markdown(_pill("Human", _TAG_HUMAN_COLOR), unsafe_allow_html=True)
    st.markdown(
        "Put two knockdowns side by side: signature shifts, assumption audits, and functional "
        "readouts on the same scale, plus a full gene × state heatmap across all 31 knockdowns."
    )
    st.page_link("pages/3_compare.py", label="Open Compare →")

with row2_col1:
    st.markdown("### 📊 Dataset Nutrition")
    st.markdown(_pill("Human", _TAG_HUMAN_COLOR), unsafe_allow_html=True)
    st.markdown(
        "Inspect the dataset nutrition label: coverage, perturbation quality, known limitations, "
        "and specific confidence scoring of knockdowns across metrics, auto-generated from the perturbation records."
    )
    st.page_link("pages/4_nutrition_label.py", label="Open Nutrition Label →")

with row2_col2:
    st.markdown("### 🛠 Agentic Exploring")
    st.markdown(_pill("Agent", _TAG_AGENT_COLOR), unsafe_allow_html=True)
    st.markdown(
        "Connect Claude or another agent via MCP to query perturbation records "
        "programmatically in English, no web scraping required."
    )
    st.page_link("pages/5_agent.py", label="Open Agent Access →")
