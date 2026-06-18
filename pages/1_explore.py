"""Perturbation explorer — main demo page."""

import streamlit as st

# ---------------------------------------------------------------------------
# Page controls
# ---------------------------------------------------------------------------

st.title("Perturbation Explorer")

col_left, col_right = st.columns([2, 1])

with col_left:
    gene = st.selectbox("Select gene", options=[], index=0)  # TODO: populate from constants

with col_right:
    model = st.radio("Cell model", options=["iTF-MG", "iMG"], horizontal=True)

# TODO: load record = loader.load_mdata(model) → compute or fetch from JSON

# ---------------------------------------------------------------------------
# Gene header card
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Gene overview")
# TODO: render_gene_header(record)

# ---------------------------------------------------------------------------
# Assumption audit panel  (must appear before figures)
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Assumption audit")

with st.expander("What are assumption audits?"):
    st.markdown(
        "Each perturbation record is tagged with flags for known methodological assumptions "
        "that may affect data interpretation. Flags are derived from cell count, knockdown efficiency, "
        "antibody validation status, and known model-specific effects."
    )

# TODO: render_assumption_flags(record.assumption_audit)

# ---------------------------------------------------------------------------
# Signature shift visualization
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Microglial state signature shifts")

cross_model = st.toggle("Show both models side-by-side")

# TODO: render_signature_bars(shifts, reliable_states)

# ---------------------------------------------------------------------------
# Top DEGs panel
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Top differentially expressed genes")

show_sig_only = st.toggle("Show only signature genes")

col_pos, col_neg = st.columns(2)

with col_pos:
    st.markdown("**Upregulated**")
    # TODO: st.dataframe(pos_degs, use_container_width=True, hide_index=True)

with col_neg:
    st.markdown("**Downregulated**")
    # TODO: st.dataframe(neg_degs, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# Functional readouts panel (4 featured KDs only)
# ---------------------------------------------------------------------------

FEATURED_KDS = ["ZNF532", "PRDM1", "STAT2", "DNMT1"]

if gene in FEATURED_KDS:
    st.markdown("---")
    st.subheader("Functional readouts")
    st.caption("Functional assays are population-level (bulk), not single-cell.")

    r1c1, r1c2, r2c1, r2c2 = st.columns(4)
    # TODO: render_functional_card("Phagocytosis (β-amyloid)", record.functional_readouts[...])
    # TODO: render_functional_card("Phagocytosis (synaptosomes)", ...)
    # TODO: render_functional_card("Lysosomal pH", ...)
    # TODO: render_functional_card("Cathepsin B activity", ...)

# ---------------------------------------------------------------------------
# Discordance callout
# ---------------------------------------------------------------------------

# TODO: if record.discordances: render_discordance_box(record.discordances)

# ---------------------------------------------------------------------------
# scHPF factors panel
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("scHPF factor activity")

with st.expander("What are scHPF factors?"):
    st.markdown(
        "scHPF (single-cell Hierarchical Poisson Factorization) decomposes gene expression into "
        "latent factors. Here we show which factors are most shifted by the knockdown vs NTC, "
        "and whether each factor has concordant signal in human microglia data."
    )

col_up, col_dn = st.columns(2)

with col_up:
    st.markdown("**Top increased factors**")
    # TODO: render top 5 increased factors

with col_dn:
    st.markdown("**Top decreased factors**")
    # TODO: render top 5 decreased factors

# ---------------------------------------------------------------------------
# Download section
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Downloads")

dl1, dl2 = st.columns(2)

with dl1:
    st.download_button(
        label="Download JSON record",
        data="{}",  # TODO: json.dumps(record.model_dump(), indent=2)
        file_name=f"{gene}_{model}_record.json",
        mime="application/json",
        disabled=True,
    )

with dl2:
    st.download_button(
        label="Download DEG CSV",
        data="gene,direction,log2fc\n",  # TODO: real CSV
        file_name=f"{gene}_{model}_degs.csv",
        mime="text/csv",
        disabled=True,
    )
