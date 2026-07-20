import streamlit as st
from utils import apply_custom_css

st.set_page_config(
    page_title="Download | Cross-trait PRS Database",
    page_icon="🧬",
    layout="wide"
)

apply_custom_css()

st.title("Download")

st.markdown(
    """
We provide the complete cross-trait polygenic risk score (PRS) ranking
database generated in this study.

The database contains the systematic evaluation and ranking of candidate
PRSs for target diseases across the evaluated biobanks and ancestry groups.
Each record corresponds to the performance of a candidate PRS for a given
target disease in a specific evaluation cohort.
"""
)

st.divider()

st.subheader("Cross-trait PRS Ranking Database")

st.markdown(
    """
The database includes:

- Evaluation biobank and ancestry
- Evaluation sample size and number of cases
- Target disease ICD-10 code and disease description
- Candidate PRS trait ICD-10 code and disease description
- Candidate PRS rank
- Adjusted AUC
- PRS construction method
- GWAS source
- GWAS sample size and number of cases
- Link to the corresponding PRS model, when publicly available

Adjusted AUCs account for **age, sex, and the first 10 genetic principal
components (PC1–PC10)**.

The database is distributed in **Apache Parquet format**, which provides
efficient storage and enables direct analysis using Python, R, and other
data-analysis frameworks.
"""
)

st.divider()

st.subheader("Download complete database")

st.markdown(
    """
[**Download Cross-trait PRS Ranking Database (Apache Parquet)**](https://github.com/terryjiyao/CrosstraitPRS_Ensemble/releases/download/v0.1-alpha/prs_cross_trait_ranking.parquet)
"""
)

st.divider()

st.subheader("PRS Models")

st.markdown(
    """
Individual PRS models were constructed from publicly available GWAS summary
statistics. Links to available PRS models are provided directly in the
**PRS download link** column of the ranking database and in the interactive
**Search Engine**.

Availability of individual PRS models depends on the data-sharing policies
of the corresponding GWAS resources.
"""
)

st.divider()

st.subheader("Citation")

st.markdown(
    """
For details of the study and recommended citation, please see:

**Zhang J., et al. _Cross-trait Polygenic Risk Score Transferability and
Ensemble Risk Prediction._**  
*Manuscript under review.*
"""
)