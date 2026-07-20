import streamlit as st
from pathlib import Path
from utils import apply_custom_css

APP_DIR = Path(__file__).parent.resolve()
LOGO_PATH1 = APP_DIR / "assets" / "UniversityofPennsylvania_FullLogo_RGB.png"
LOGO_PATH2 = APP_DIR / "assets" / "DBEI_logo.png"

st.set_page_config(
    page_title="Cross-trait PRS Database",
    page_icon="🧬",
    layout="wide"
)

apply_custom_css()

# Main layout: title on the left, logos on the right
col1, col2 = st.columns([5, 2], vertical_alignment="top")

with col1:
    st.title("Cross-trait Polygenic Risk Score Database")

with col2:
    logo_col1, logo_col2 = st.columns(2)

    with logo_col1:
        st.image(LOGO_PATH1, width=500)

    with logo_col2:
        st.image(LOGO_PATH2, width=160)


st.markdown(
    """
This site provides public access to summary-level results from our systematic
evaluation of **cross-trait polygenic risk score (PRS) performance and transferability** across
diseases, biobanks, and ancestry groups.

We constructed a comprehensive PRS library from publicly available 
genome-wide association study (GWAS) summary statistics from **FinnGen** and 
**Million Veteran Program (MVP)** using the pseudo-training framework implemented in **PennPRS**.
We then systematically evaluated the predictive performance of these PRSs across a broad range of target diseases in the
**All of Us Research Program (AoU)** and the **UK Biobank (UKB)**.

Researchers can use this resource to:

- Explore and rank candidate PRSs for individual target diseases.
- Compare cross-trait PRS performance across biobanks and ancestries.
- Identify potentially informative PRSs developed for genetically or
  phenotypically related traits.
- Access metadata and download links for individual PRS models.
- Download the complete cross-trait PRS ranking database for downstream
  analyses and development of multi-trait PRS ensemble models.

Use the **Search Engine** page to interactively explore PRS rankings by
evaluation biobank, ancestry, and target disease.

Use the **Download** page to access the complete cross-trait PRS ranking
database and associated resources.
"""
)

st.divider()

st.subheader("Study")

st.markdown(
    """
For details of the study, please see:

**Zhang J., et al. _Cross-trait Polygenic Risk Score Transferability and
Ensemble Risk Prediction._**  
*Manuscript under review.*

For raw code and analysis, please see our [Github Repo](https://github.com/terryjiyao/CrosstraitPRS_Ensemble)
"""
)

st.divider()

st.subheader("Maintained by")

st.markdown(
    """
**Jiyao Zhang (jiyaoz@sas.upenn.edu)**

**[Jin Jin Lab](https://jin93.github.io/)**  
Department of Biostatistics, Epidemiology and Informatics  
Perelman School of Medicine  
University of Pennsylvania
"""
)

st.markdown(
    """
For questions regarding the methods, results, database, or website,
please contact the study authors.
"""
)

st.divider()

st.subheader("Resources")

st.markdown(
    """
- [GitHub Repository](https://github.com/terryjiyao/CrosstraitPRS_Ensemble)
- [All of Us Research Program](https://www.researchallofus.org/data-tools/workbench/)
- [UK Biobank](https://www.ukbiobank.ac.uk/)
- [FinnGen](https://site.fingenious.fi/en/)
- [Million Veteran Program (MVP)](https://www.mvp.va.gov/pwa/)
- [PheWAS Catalog](https://phewascatalog.org/)
- [PennPRS](https://pennprs.org/)
"""
)

st.divider()

st.subheader("Update Log")

st.markdown(
    """
**July 2026**
- Initial release of the Cross-trait PRS Database.
- Added interactive PRS ranking search across biobanks and ancestries.
- Released the complete cross-trait PRS ranking database.
"""
)