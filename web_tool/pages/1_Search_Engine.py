import streamlit as st
import pandas as pd
import requests
from pathlib import Path
from utils import apply_custom_css

st.set_page_config(
    page_title="Cross-trait PRS performance seach engine",
    layout="wide"
)

apply_custom_css()

APP_DIR = Path(__file__).parent.resolve()
DATA_DIR = APP_DIR.parent / "data"                                  # web_tool/data, shared by all pages
RANKING_PATH = DATA_DIR / "prs_cross_trait_ranking.parquet"
ENSEMBLE_PATH = DATA_DIR / "prs_ensemble_performance.parquet"


@st.cache_data(show_spinner=False)
def load_data():
    # both tables ship with the repo, no download needed
    return pd.read_parquet(RANKING_PATH), pd.read_parquet(ENSEMBLE_PATH)

@st.cache_resource(show_spinner=False)
def prepare_options(df):
    biobank_options = sorted(
        df["eval_biobank"].dropna().unique()
    )

    ancestry_options = {
        biobank: sorted(
            df.loc[
                df["eval_biobank"] == biobank,
                "eval_ancestry"
            ]
            .dropna()
            .unique()
        )
        for biobank in biobank_options
    }

    target_options = {
        (biobank, ancestry): sorted(
            group["target_icd"]
            .dropna()
            .unique()
        )
        for (biobank, ancestry), group in df.groupby(
            ["eval_biobank", "eval_ancestry"]
        )
    }

    target_display = (
        df[
            ["target_icd", "target_icd_description"]
        ]
        .drop_duplicates()
        .set_index("target_icd")[
            "target_icd_description"
        ]
        .to_dict()
    )

    return (
        biobank_options,
        ancestry_options,
        target_options,
        target_display,
    )


df, ensemble_df = load_data()

(
    biobank_options,
    ancestry_options_dict,
    target_options_dict,
    target_display,
) = prepare_options(df)

### page heading ###
st.title("Cross-trait PRS Performance Search Engine")

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
<i>Cross-trait Polygenic Risk Score Transferability</i> (under review).
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
    "**Search candidate PRS rankings by selecting evaluation biobank, ancestry, and target trait ICD-10.**"
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
        "Target trait ICD-10",
        options=target_icd_options,
        format_func=lambda x: f"{x} ({target_display.get(x, 'Unknown')})",
        index=None,
        placeholder="Type to search ICD-10 trait...",
        disabled=(biobank is None or ancestry is None)
    )

if st.button("Search"):
    if target_icd is None or biobank is None or ancestry is None:
        st.warning("Please select biobank, ancestry, and target trait ICD-10.")
    else:
        result = (
            df[
                (df["target_icd"] == target_icd)
                & (df["eval_biobank"] == biobank)
                & (df["eval_ancestry"] == ancestry)
            ]
            .sort_values("rank")
            .reset_index(drop=True)
        )

    if len(result) > 0:

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

        **Evaluation biobank:** {biobank_name} | **Ancestry:** {ancestry_label} | **Sample size:** {n_samples:,} | **Cases:** {n_cases:,} | **Candidate traits:** {n_candidate_traits:,} | **Candidate PRSs:** {len(result):,}
        """
        )

        st.caption(
            "Highlighted rows correspond to PRSs developed for the target trait. "
            "Validation adjusted AUCs are adjusted for age, sex, and the first 10 genetic principal components (PC1–PC10)."
        )

        ### ensemble PRS panel ###
        # the ensemble table is EUR-only, one row per (target trait, ensemble method),
        # with AoU as in-sample and UKB as out-of-sample evaluation
        ens = ensemble_df[ensemble_df["target_icd"] == target_icd].copy()

        if ancestry == "EUR" and len(ens) > 0:
            st.markdown("#### Ensemble PRS performance")

            ens = ens.sort_values("insample_ensemble_auc", ascending=False).reset_index(drop=True)

            ens_panel = pd.DataFrame({
                "Method": ens["ensemble_method"],
                "AUC (in-sample, AoU)": ens["insample_ensemble_auc"],
                "Delta (in-sample)": ens["insample_delta_vs_single"],
                "AUC (out-of-sample, UKB)": ens["outsample_ensemble_auc"],
                "Delta (out-of-sample)": ens["outsample_delta_vs_single"],
            })

            # prepend the single-PRS baseline so the gain is readable in place
            ens_baseline = pd.DataFrame([{
                "Method": "Best single cross-trait PRS",
                "AUC (in-sample, AoU)": ens.loc[0, "insample_bestsingle_auc"],
                "Delta (in-sample)": pd.NA,
                "AUC (out-of-sample, UKB)": ens.loc[0, "outsample_bestsingle_auc"],
                "Delta (out-of-sample)": pd.NA,
            }])
            ens_panel = pd.concat([ens_baseline, ens_panel], ignore_index=True)

            # format AUCs to 4 decimals and deltas with an explicit sign
            for c in ["AUC (in-sample, AoU)", "AUC (out-of-sample, UKB)"]:
                ens_panel[c] = ens_panel[c].map(lambda x: f"{x:.4f}" if pd.notna(x) else "")
            for c in ["Delta (in-sample)", "Delta (out-of-sample)"]:
                ens_panel[c] = ens_panel[c].map(lambda x: f"{x:+.4f}" if pd.notna(x) else "—")

            # highlight the baseline row to separate it from the ensemble methods
            ens_baseline_mask = ens_panel["Method"] == "Best single cross-trait PRS"

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
                "Ensemble PRSs combine the top 10 candidate cross-trait PRSs for the target trait. "
                "In-sample evaluation in All of Us (N = 70,000); out-of-sample evaluation in UK Biobank (N = 224,301). "
                "Delta is the AUC difference against the best single cross-trait PRS in the same evaluation. "
                "Available for European ancestry and for traits evaluated in both biobanks."
            )

            st.markdown("#### Candidate single PRS ranking")

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

        # rename columns for display
        display_df = display_df.rename(columns={
            "rank": "Rank",
            "auc": "AUC",
            "candidate_icd": "Candidate trait ICD-10",
            "candidate_icd_description": "Candidate trait ontology",
            "method": "PRS method",
            "gwas_source": "GWAS source",
            "gwas_n_sample": "GWAS sample size",
            "gwas_n_case": "GWAS case size",
            "pgs_download_link": "PRS download link",
        })

        highlight_mask = display_df["Candidate trait ICD-10"] == target_icd

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

    else:
        st.warning("No Evaluation records found.")