"""About page — dataset background, model card, and citation."""

from pathlib import Path

import streamlit as st

from mglia.constants import CITATION
from mglia.ui_components import render_global_styles

render_global_styles()

st.title("About")

_MODEL_CARD_PATH = "data/static/reference/model_card.png"

st.markdown(
    """
    ## Dataset

    This tool explores CRISPRi perturbation data from McQuade et al. 2025, covering 31
    transcription factor knockdowns across two human iPSC-derived microglia models
    (iTF-MG and iMG). Each perturbation record includes signature shifts across 6 microglial
    states, top differentially expressed genes, scHPF factor activity, functional assay
    readouts, and a per-record assumption audit.
    """
)

if Path(_MODEL_CARD_PATH).exists():
    st.image(_MODEL_CARD_PATH, caption="Model card", width=350)
else:
    st.caption(f"Model card image — drop file into `{_MODEL_CARD_PATH}`")

st.markdown(
    f"""
    ## Citation

    **{CITATION["authors"]}**
    {CITATION["title"]}
    [DOI: {CITATION["journal_or_preprint"]}]({CITATION["doi_url"]})

    [GitHub]({CITATION["github_url"]}) · [Preprint]({CITATION["preprint_url"]}) · {CITATION["contact_email"]}
    """
)
