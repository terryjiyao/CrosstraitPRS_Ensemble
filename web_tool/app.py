import streamlit as st
import pandas as pd
import requests
from pathlib import Path

st.set_page_config(
    page_title="Cross-trait PRS performance seach engine",
    layout="wide"
)

DATA_URL = "https://github.com/terryjiyao/CrosstraitPRS_Ensemble/releases/download/v0.1-alpha/prs_cross_trait_ranking.parquet"
APP_DIR = Path(__file__).parent.resolve()
DATA_PATH = APP_DIR / "data" / "prs_cross_trait_ranking.parquet"

@st.cache_data
def load_data():
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not DATA_PATH.exists():
        r = requests.get(DATA_URL)
        r.raise_for_status()
        DATA_PATH.write_bytes(r.content)

    return pd.read_parquet(DATA_PATH)

df = load_data()

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
target_display = (
    df[["target_icd", "target_icd_description"]]
    .drop_duplicates()
    .set_index("target_icd")["target_icd_description"]
    .to_dict()
)

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
biobank_options = sorted(df["eval_biobank"].dropna().unique())
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
    ancestry_options = sorted(
        df.loc[df["eval_biobank"] == biobank, "eval_ancestry"]
        .dropna()
        .unique()
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
    target_icd_options = sorted(
        df.loc[
            (df["eval_biobank"] == biobank)
            & (df["eval_ancestry"] == ancestry),
            target_col,
        ]
        .dropna()
        .unique()
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