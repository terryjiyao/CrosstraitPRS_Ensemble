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
    "Search candidate PRS rankings by selecting target trait ICD-10 endpoints and evaluation dataset."
)

### searching section ###
target_col = "target_icd"
dataset_col = "eval_dataset"
rank_col = "rank"

# target trait options and dataset options
target_icd_options = sorted(df[target_col].dropna().unique())
dataset_options = sorted(df[dataset_col].dropna().unique())

target_display = (
    df[["target_icd", "target_icd_description"]]
    .drop_duplicates()
    .set_index("target_icd")["target_icd_description"]
    .to_dict()
)

dataset_display = {
    "AOU_EUR": "All of Us / European",
    "AOU_AFR": "All of Us / African",
    "UKB_EUR": "UK Biobank / European",
}

col1, col2 = st.columns(2)

with col1:
    target_icd = st.selectbox(
        "Target trait ICD-10",
        options=target_icd_options,
        format_func=lambda x: f"{x} ({target_display.get(x, 'Unknown')})",
        index=None,
        placeholder="Type to search ICD-10 trait..."
    )

with col2:
    dataset = st.selectbox(
        "Evaluation biobank / Ancestry",
        options=dataset_options,
        format_func=lambda x: dataset_display.get(x, x),
        index=None,
        placeholder="Select evaluation dataset..."
    )

if st.button("Search"):
    result = (
        df[(df[target_col] == target_icd) & (df[dataset_col] == dataset)]
        .sort_values(rank_col)
        .reset_index(drop=True)
    )

    if len(result) > 0:

        ### Display compact header ####
        n_samples = int(result.loc[0, "eval_n_sample"])
        n_cases = int(result.loc[0, "eval_n_case"])
        n_candidate_traits = result["candidate_icd"].nunique()

        target_description = result.loc[0, "target_icd_description"]
        target_chapter = result.loc[0, "target_icd_chapter"]
        dataset_label = dataset_display.get(dataset, dataset)
        biobank_name = dataset_label.split(" / ")[0]

        # generate ancestry label
        ancestry_label = {
            "EUR": "European",
            "AFR": "African",
            "AMR": "Admixed American",
            "EAS": "East Asian",
        }.get(str(dataset).split("_")[-1], str(dataset).split("_")[-1])

        st.markdown(
            f"""
        ### `{target_icd}` | {target_description}

        **Disease chapter:** {target_chapter}

        **Evaluation biobank:** {biobank_name} | **Ancestry:** {ancestry_label} | **Sample size:** {n_samples:,} | **Cases:** {n_cases:,} | **Candidate traits:** {n_candidate_traits:,} | **Candidate PRSs:** {len(result):,}
        """
        )

        st.caption(
            "Highlighted rows correspond to PRSs developed for the target trait. "
            "AUCs are adjusted for age, sex, and genetic principal components (PC1-PC10)."
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
            "pgs_dowload_link",
        ]

        display_df = result[display_cols].copy()

        # format values
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
            "pgs_dowload_link": "PRS download link",
        })

        highlight_mask = display_df["Candidate trait ICD-10"] == target_icd

        def highlight_self_trait(row):
            if highlight_mask.loc[row.name]:
                return ["background-color: #fff3cd; font-weight: 600"] * len(row)
            return [""] * len(row)

        st.dataframe(
            display_df.style.apply(highlight_self_trait, axis=1),
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.warning("No Evaluation records found.")