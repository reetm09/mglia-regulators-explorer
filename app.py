"""Streamlit entrypoint for the Microglia State Regulator Explorer."""

import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="mglia explorer",
    page_icon="🧠",
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## mglia explorer")
    # TODO: add lab logo image
    st.markdown("---")
    st.markdown(
        "**McQuade et al. 2025**  \n"
        "Transcriptional regulation of disease-relevant microglial activation programs  \n"
        "[DOI: TODO](#)"
    )
    st.markdown("[GitHub](#) · [Preprint](#) · reet.mishra@berkeley.edu")
    st.markdown("---")
    # TODO: show st.warning if data/raw/*.h5mu files are missing
    st.markdown("**Data version:** v0.1-dev")

# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------

st.title("Microglia State Regulator Explorer")

st.markdown(
    """
    This tool lets you explore CRISPRi perturbation data from McQuade et al. 2025,
    covering 31 transcription factor knockdowns across two human iPSC-derived microglia models
    (iTF-MG and iMG). Each perturbation record includes signature shifts across 6 microglial
    states, top differentially expressed genes, scHPF factor activity, functional assay readouts,
    and a per-record assumption audit.
    """
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### 🔬 Wet-lab biologist")
    st.markdown(
        "Explore how each transcription factor knockdown shifts microglial activation states. "
        "Compare ZNF532 vs PRDM1, inspect functional readouts, and download DEG lists."
    )
    st.page_link("pages/1_explore.py", label="Open Explorer →")

with col2:
    st.markdown("### 🤖 ML / virtual cell researcher")
    st.markdown(
        "Access structured benchmark splits, null baselines, and scoring functions. "
        "Upload your model's predictions and get per-metric scores back instantly."
    )
    st.page_link("pages/3_benchmark.py", label="Open Benchmark →")

with col3:
    st.markdown("### 📊 Data quality")
    st.markdown(
        "Inspect the dataset nutrition label: coverage, perturbation quality, known limitations, "
        "and benchmark readiness — auto-generated from the perturbation records."
    )
    st.page_link("pages/4_nutrition_label.py", label="Open Nutrition Label →")

with col4:
    st.markdown("### 🛠 AI agent")
    st.markdown(
        "Connect Claude or another agent via MCP to query perturbation records, "
        "retrieve benchmark splits, and evaluate predictions programmatically — "
        "no web scraping required."
    )
    st.page_link("pages/5_agent.py", label="Open Agent Access →")
