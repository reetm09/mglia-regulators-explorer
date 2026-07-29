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

    This tool explores CRISPRi perturbation data from McQuade et al. 2026, covering 31
    transcription factor knockdowns across two human iPSC-derived microglia models
    (iTF-MG and iMG). Each perturbation record includes signature shifts across 6 microglial
    states, top differentially expressed genes, scHPF factor activity, functional assay
    readouts, and a per-record assumption audit.
    """
)

if Path(_MODEL_CARD_PATH).exists():
    st.image(_MODEL_CARD_PATH, caption="Dataset card", width=350)
else:
    st.caption(f"Dataset card image — drop file into `{_MODEL_CARD_PATH}`")

st.markdown(
    f"""
    ## Citation

    #### Full
    {CITATION["authors"]} ({CITATION["year"]}). 
    {CITATION["title"]}. *{CITATION["journal"]}* [{CITATION["doi_url"]}](https://doi.org/{CITATION["doi_url"]})


    #### Short
    {CITATION["short"]}, {CITATION["title"]}, *{CITATION["journal"]}* ({CITATION["year"]}), [{CITATION["doi_url"]}](https://doi.org/{CITATION["doi_url"]})
    
    #### Code
    [GitHub Link]({CITATION["github_url"]}) • Email {CITATION["contact_email"]} if you have any questions.
    """
)
