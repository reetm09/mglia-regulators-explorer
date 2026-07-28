"""Perturbation Explorer"""

import json

import streamlit as st
from mglia import records, static_tables
from mglia.constants import (
    FUNCTIONAL_ASSAY_NAMES,
    GLOSSARY_BLURBS,
    PROT_VOLCANO_STATES,
    RNA_VOLCANO_COLORS,
    SIGNATURE_GENE_SETS,
    STATES,
)
from mglia.dataset_config import MGLIA_DEFAULT_CONFIG
from mglia.ui_components import (
    render_discordance_box,
    render_factor_bars,
    render_functional_card,
    render_gene_header,
    render_global_styles,
    render_method_assumptions,
    render_signature_bars,
    render_static_image,
    render_volcano_legend,
)

render_global_styles()

config = MGLIA_DEFAULT_CONFIG

# ---------------------------------------------------------------------------
# Page controls
# ---------------------------------------------------------------------------

st.title("Explore Perturbations")

genes = records.list_genes()
default_gene = st.session_state.pop("explore_gene", "ZNF532")
default_index = genes.index(default_gene) if default_gene in genes else 0

col_left, col_right = st.columns([2, 1])

with col_left:
    gene = st.selectbox("Select gene", options=genes, index=default_index)

with col_right:
    model = st.radio("Cell model", options=["iTF-MG", "iMG"], horizontal=True)

record = records.get_record(gene, model)
if record is None:
    st.error(f"No record found for {gene} in {model}.")
    st.stop()

# disabled: benchmark/train-test feature removed from active use
# if gene in TEST_SET_GENES:
#     st.warning("This gene is in the held-out test set. Do not use it to train models.")

# ---------------------------------------------------------------------------
# Gene header card
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Gene overview")
render_gene_header(record)

# ---------------------------------------------------------------------------
# Method assumptions & caveats panel (must appear before figures)
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Method assumptions & caveats")

with st.expander("What are method assumptions & caveats?"):
    st.markdown(GLOSSARY_BLURBS["method_assumptions"])

render_method_assumptions(record)

# ---------------------------------------------------------------------------
# Signature shift visualization
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Microglial state signature shifts")

cross_model = st.toggle("Show both models side-by-side")
shifts = record.prediction_targets["signature_shift"]
reliable_states = [k for k, meta in STATES.items() if meta["reliable"]]

if cross_model:
    other_model = "iMG" if model == "iTF-MG" else "iTF-MG"
    other_record = records.get_record(gene, other_model)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**{model}**")
        fig = render_signature_bars(shifts, reliable_states)
        st.plotly_chart(fig, config={"displaylogo": False}, width="stretch", theme=None)
        render_static_image(
            static_tables.get_signature_shift_image_path(config, model, gene),
            "Signature point-plot",
            height=fig.layout.height,
        )
    with col_b:
        st.markdown(f"**{other_model}**")
        if other_record is None:
            st.info(f"No record for {gene} in {other_model}.")
        else:
            other_shifts = other_record.prediction_targets["signature_shift"]
            fig = render_signature_bars(other_shifts, reliable_states)
            st.plotly_chart(
                fig, config={"displaylogo": False}, width="stretch", theme=None
            )
            render_static_image(
                static_tables.get_signature_shift_image_path(config, other_model, gene),
                "Signature point-plot",
                height=fig.layout.height,
            )
else:
    col_chart, col_image = st.columns(2)
    with col_chart:
        fig = render_signature_bars(shifts, reliable_states)
        st.plotly_chart(fig, config={"displaylogo": False}, width="stretch", theme=None)
    with col_image:
        render_static_image(
            static_tables.get_signature_shift_image_path(config, model, gene),
            "Signature point-plot",
            height=fig.layout.height,
        )

# ---------------------------------------------------------------------------
# Top DEGs panel
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Top 50 Mixscale-weighted differentially expressed genes")
with st.expander("What are Mixscale-weighted DEGs?"):
    st.markdown(GLOSSARY_BLURBS["mixscale_degs"])

show_sig_only = st.toggle("Show only signature genes")
deg = record.prediction_targets["deg"]
signature_genes = {g for genelist in SIGNATURE_GENE_SETS.values() for g in genelist}


def _filtered(gene_list: list[str]) -> list[str]:
    if show_sig_only and signature_genes:
        return [g for g in gene_list if g in signature_genes]
    return gene_list


col_pos, col_neg = st.columns(2)

with col_pos:
    st.markdown("**Upregulated**")
    st.dataframe(
        {"gene": _filtered(deg["top_positive"])[:15]},
        width="stretch",
        hide_index=True,
    )

with col_neg:
    st.markdown("**Downregulated**")
    st.dataframe(
        {"gene": _filtered(deg["top_negative"])[:15]},
        width="stretch",
        hide_index=True,
    )

if show_sig_only and not signature_genes:
    st.caption("Signature gene sets are not yet populated, this filter has no effect.")

st.subheader(f"{gene} Volcano Plot in {model}")
tab_rna, tab_prot = st.tabs(["RNA volcano", "Protein volcano"])
with tab_rna:
    render_volcano_legend(list(RNA_VOLCANO_COLORS.keys()))
    render_static_image(
        static_tables.get_volcano_plot_path(config, model, gene, "rna"),
        f"{gene} RNA volcano "
        "\n\n Note: y-axis shows adjusted p-values after Benjamini-Hochberg multiple-hypothesis correction",
        to_crop=True,
    )
with tab_prot:
    render_volcano_legend(PROT_VOLCANO_STATES, protein=True)
    render_static_image(
        static_tables.get_volcano_plot_path(config, model, gene, "prot"),
        f"{gene} protein volcano",
        to_crop=True,
    )

# ---------------------------------------------------------------------------
# Functional readouts panel
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Functional readouts")
st.caption("Functional assays are population-level (bulk), not single-cell.")

readouts = record.functional_readouts
row1 = st.columns(3)
row2 = st.columns(3)
for col, (assay_id, assay_name) in zip(row1 + row2, FUNCTIONAL_ASSAY_NAMES.items()):
    with col:
        render_functional_card(assay_name, readouts.get(assay_id))

# ---------------------------------------------------------------------------
# Discordance callout
# ---------------------------------------------------------------------------

discordances = record.discordances.get(gene, []) if record.discordances else []
if discordances:
    render_discordance_box(discordances)

# ---------------------------------------------------------------------------
# scHPF factors panel
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Microglia State scHPF Factor Shifts")

with st.expander("What are scHPF factors?"):
    st.markdown(GLOSSARY_BLURBS["schpf_factors"])

factors = record.prediction_targets.get("schpf_factors", {})

col_chart, col_image = st.columns(2)
with col_chart:
    factor_fig = render_factor_bars(factors)
    st.plotly_chart(
        factor_fig, config={"displaylogo": False}, width="stretch", theme=None
    )
with col_image:
    render_static_image(
        static_tables.get_factor_shift_image_path(config, model, gene),
        "Factor point-plot",
        height=factor_fig.layout.height,
    )

# ---------------------------------------------------------------------------
# Download section
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Downloads")

dl1, dl2 = st.columns(2)

with dl1:
    st.download_button(
        label="Download JSON record",
        data=json.dumps(record.model_dump(), indent=2),
        file_name=f"{gene}_{model}_record.json",
        mime="application/json",
    )

with dl2:
    deg_lines = ["gene,direction"]
    deg_lines += [f"{g},up" for g in deg["top_positive"]]
    deg_lines += [f"{g},down" for g in deg["top_negative"]]
    st.download_button(
        label="Download DEG CSV",
        data="\n".join(deg_lines),
        file_name=f"{gene}_{model}_degs.csv",
        mime="text/csv",
    )
    st.caption(
        "For values of differentially expressed genes, refer to Supplementary "
        "Table 2, Tab 7 (iTF-MG DEGs) and Tab 8 (iMG DEGs)."
    )
