import streamlit as st
import pandas as pd
import requests
from pathlib import Path
from utils import apply_custom_css

st.set_page_config(
    page_title="Cross-disease PRS performance seach engine",
    layout="wide"
)

apply_custom_css()

APP_DIR = Path(__file__).parent.resolve()
DATA_DIR = APP_DIR.parent / "data"                                  # web_tool/data, shared by all pages
RANKING_PATH = DATA_DIR / "prs_cross_disease_ranking.parquet"
ENSEMBLE_PATH = DATA_DIR / "prs_ensemble_performance.parquet"


@st.cache_resource(show_spinner=False)
def load_data():
    # cache_resource returns the same object instead of a copy on every rerun
    ranking = pd.read_parquet(RANKING_PATH)
    ensemble = pd.read_parquet(ENSEMBLE_PATH)

    # low-cardinality string columns as category: smaller memory and much faster filtering
    for c in ["eval_biobank", "eval_ancestry", "target_icd", "candidate_icd",
              "method", "gwas_source", "target_icd_chapter"]:
        if c in ranking.columns:
            ranking[c] = ranking[c].astype("category")

    # sort once and index by the three search keys so lookups are O(log n) slices
    ranking = ranking.sort_values(["eval_biobank", "eval_ancestry", "target_icd", "rank"])
    ranking = ranking.set_index(["eval_biobank", "eval_ancestry", "target_icd"])

    ensemble = ensemble.set_index("target_icd")

    return ranking, ensemble

@st.cache_resource(show_spinner=False)
def prepare_options(_df):
    # leading underscore tells Streamlit to skip hashing this argument
    keys = _df.index.to_frame(index=False).drop_duplicates()

    biobank_options = sorted(keys["eval_biobank"].unique())

    ancestry_options = {
        b: sorted(keys.loc[keys["eval_biobank"] == b, "eval_ancestry"].unique())
        for b in biobank_options
    }

    target_options = {
        (b, a): sorted(g["target_icd"].unique())
        for (b, a), g in keys.groupby(["eval_biobank", "eval_ancestry"], observed=True)
    }

    target_display = (
        _df[["target_icd_description"]]
        .reset_index()[["target_icd", "target_icd_description"]]
        .drop_duplicates()
        .set_index("target_icd")["target_icd_description"]
        .to_dict()
    )

    return biobank_options, ancestry_options, target_options, target_display

df, ensemble_df = load_data()

(
    biobank_options,
    ancestry_options_dict,
    target_options_dict,
    target_display,
) = prepare_options(df)

### page heading ###
st.title("Cross-disease PRS Performance Search Engine")

st.markdown(
"""
<div style="
    background-color:#f8f9fa;
    border:1px solid #e6e6e6;
    border-radius:10px;
    padding:18px;
    margin-bottom:20px;
    line-height:1.35;
">

<p style="margin:0 0 8px 0;">
This is a publicly available search engine for exploring the performance of
polygenic risk scores (PRSs) across disease traits, biobanks, and ancestries.
</p>

<p style="margin:0 0 8px 0;">
<b>Developed by:</b>
Jin Jin Lab, Department of Biostatistics, Epidemiology and Informatics,
Perelman School of Medicine, University of Pennsylvania.
</p>

<p style="margin:0 0 8px 0;">
<b>Please cite:</b>
Zhang J., <i>et al.</i>
<i>Cross-disease Polygenic Risk Score Transferability</i> (under review).
</p>

<p style="margin:0;">
<b>Link to our Github Repo:</b>
https://github.com/terryjiyao/CrosstraitPRS_Ensemble.
</p>

</div>
""",
unsafe_allow_html=True,
)

st.markdown(
    "**Search candidate PRS rankings by selecting evaluation biobank, ancestry, and target disease ICD-10.**"
)

### searching section ###
target_col = "target_icd"
rank_col = "rank"

# Display mapping
biobank_display = {
    "AOU": "All of Us",
    "UKB": "UK Biobank",
}

ancestry_display = {
    "EUR": "European",
    "AFR": "African",
}

col1, col2, col3 = st.columns(3)

# select biobank
with col1:
    biobank = st.selectbox(
        "Evaluation biobank",
        options=biobank_options,
        format_func=lambda x: biobank_display.get(x, x),
        index=None,
        placeholder="Select biobank..."
    )

# select ancestry
if biobank is not None:
    ancestry_options = ancestry_options_dict.get(
        biobank, []
    )
else:
    ancestry_options = []

with col2:
    ancestry = st.selectbox(
        "Ancestry",
        options=ancestry_options,
        format_func=lambda x: ancestry_display.get(x, x),
        index=None,
        placeholder="Select ancestry...",
        disabled=(biobank is None)
    )

# select target trait
if biobank is not None and ancestry is not None:
    target_icd_options = target_options_dict.get(
        (biobank, ancestry), []
    )
else:
    target_icd_options = []

with col3:
    target_icd = st.selectbox(
        "Target disease ICD-10",
        options=target_icd_options,
        format_func=lambda x: f"{x} ({target_display.get(x, 'Unknown')})",
        index=None,
        placeholder="Type to search ICD-10 disease...",
        disabled=(biobank is None or ancestry is None)
    )

if st.button("Search"):
    if target_icd is None or biobank is None or ancestry is None:
        st.warning("Please select biobank, ancestry, and target disease ICD-10.")
    else:
        try:
            result = df.loc[(biobank, ancestry, target_icd)].reset_index()
        except KeyError:
            result = pd.DataFrame()

        if len(result) == 0:
            st.warning("No evaluation records found.")
        else:
            ### Display compact header ####
            n_samples = int(result.loc[0, "eval_n_sample"])
            n_cases = int(result.loc[0, "eval_n_case"])
            n_candidate_traits = result["candidate_icd"].nunique()

            target_description = result.loc[0, "target_icd_description"]
            target_chapter = result.loc[0, "target_icd_chapter"]

            biobank_name = biobank_display.get(biobank, biobank)
            ancestry_label = ancestry_display.get(ancestry, ancestry)

            # generate ancestry label
            st.markdown(
                f"""
            ### `{target_icd}` | {target_description}

            **Disease chapter:** {target_chapter}

            **Evaluation biobank:** {biobank_name} | **Ancestry:** {ancestry_label} | **Sample size:** {n_samples:,} | **Cases:** {n_cases:,} | **Candidate diseases:** {n_candidate_traits:,} | **Candidate PRSs:** {len(result):,}
            """
            )

            st.caption(
                "Highlighted rows correspond to PRSs developed for the target disease. "
                "Validation adjusted AUCs are adjusted for age, sex, and the first 10 genetic principal components (PC1–PC10)."
            )

            ### ensemble PRS panel ###
            # target_icd is the index of the ensemble table, not a column
            if target_icd in ensemble_df.index:
                ens = ensemble_df.loc[[target_icd]].reset_index()
            else:
                ens = pd.DataFrame()

            if ancestry == "EUR" and len(ens) > 0:
                st.markdown("#### Ensemble PRS performance")

                ens = ens.sort_values("insample_ensemble_auc", ascending=False).reset_index(drop=True)

                ens_panel = pd.DataFrame({
                    "Method": ens["ensemble_method"],
                    "AUC (in-sample, AoU)": ens["insample_ensemble_auc"],
                    "Delta (in-sample, ensemble - best single)": ens["insample_delta_vs_single"],
                    "AUC (out-of-sample, UKB)": ens["outsample_ensemble_auc"],
                    "Delta (out-of-sample, ensemble - best single)": ens["outsample_delta_vs_single"],
                })

                # prepend the single-PRS baseline so the gain is readable in place
                ens_baseline = pd.DataFrame([{
                    "Method": "Best single candidate PRS",
                    "AUC (in-sample, AoU)": ens.loc[0, "insample_bestsingle_auc"],
                    "Delta (in-sample, ensemble - best single)": pd.NA,
                    "AUC (out-of-sample, UKB)": ens.loc[0, "outsample_bestsingle_auc"],
                    "Delta (out-of-sample, ensemble - best single)": pd.NA,
                }])
                ens_panel = pd.concat([ens_baseline, ens_panel], ignore_index=True)

                # format AUCs to 4 decimals and deltas with an explicit sign
                for c in ["AUC (in-sample, AoU)", "AUC (out-of-sample, UKB)"]:
                    ens_panel[c] = ens_panel[c].map(lambda x: f"{x:.4f}" if pd.notna(x) else "")
                for c in ["Delta (in-sample, ensemble - best single)",
                          "Delta (out-of-sample, ensemble - best single)"]:
                    ens_panel[c] = ens_panel[c].map(lambda x: f"{x:+.4f}" if pd.notna(x) else "—")

                # highlight the baseline row to separate it from the ensemble methods
                ens_baseline_mask = ens_panel["Method"] == "Best single candidate PRS"

                def highlight_ens_baseline(row):
                    if ens_baseline_mask.loc[row.name]:
                        return ["background-color: #f1f3f5; font-style: italic"] * len(row)
                    return [""] * len(row)

                styled_ens = (
                    ens_panel.style
                    .apply(highlight_ens_baseline, axis=1)
                    .set_properties(**{"text-align": "left"})
                )

                st.dataframe(styled_ens, use_container_width=True, hide_index=True)

                st.caption(
                    "Ensemble PRSs combine the top 10 candidate cross-disease PRSs for the target disease. "
                    "In-sample evaluation in All of Us (N = 70,000); out-of-sample evaluation in UK Biobank (N = 224,301). "
                    "Delta is the AUC difference against the best single cross-disease PRS in the same evaluation. "
                    "Available for European ancestry and for diseases evaluated in both biobanks."
                )

                st.markdown("#### Single candidate PRS ranking")

            ### display table ####
            display_cols = [
                "rank",
                "auc",
                "candidate_icd",
                "candidate_icd_description",
                "method",
                "gwas_source",
                "gwas_n_sample",
                "gwas_n_case",
                "pgs_download_link",
            ]

            display_df = result[display_cols].copy()

            # format values
            display_df["rank"] = display_df["rank"].astype(str)
            display_df["auc"] = display_df["auc"].map(lambda x: f"{x:.4f}")
            display_df["gwas_n_sample"] = display_df["gwas_n_sample"].map(lambda x: f"{int(x):,}" if pd.notna(x) else "")
            display_df["gwas_n_case"] = display_df["gwas_n_case"].map(lambda x: f"{int(x):,}" if pd.notna(x) else "")

            # display the C+T method with its conventional name
            display_df["method"] = display_df["method"].astype(str).replace({"C_T": "C+T"})

            # rename columns for display
            display_df = display_df.rename(columns={
                "rank": "Rank",
                "auc": "AUC",
                "candidate_icd": "Candidate disease ICD-10",
                "candidate_icd_description": "Candidate disease ontology",
                "method": "PRS method",
                "gwas_source": "GWAS source",
                "gwas_n_sample": "GWAS sample size",
                "gwas_n_case": "GWAS case size",
                "pgs_download_link": "PRS download link",
            })

            highlight_mask = display_df["Candidate disease ICD-10"] == target_icd

            def highlight_self_trait(row):
                if highlight_mask.loc[row.name]:
                    return ["background-color: #fff3cd; font-weight: 600"] * len(row)
                return [""] * len(row)

            styled_df = (
                display_df.style
                .apply(highlight_self_trait, axis=1)
                .set_properties(**{"text-align": "left"})
            )

            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True,
            )