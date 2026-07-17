# Cross-Trait PRS Database and Ensemble PRS

This repository contains code for constructing, evaluating, and integrating cross-trait polygenic risk scores (PRSs) across multiple diseases, biobanks, and ancestry groups. The framework systematically evaluates the predictive performance of PRSs across target diseases and integrates complementary cross-trait PRSs using ensemble learning approaches.

The analyses were conducted using data from the [**All of Us Research Program (AoU)**](https://www.researchallofus.org/) and the [**UK Biobank (UKB)**](https://www.ukbiobank.ac.uk/). Individual-level genotype and electronic health record data are available through controlled access via the [All of Us Researcher Workbench](https://www.researchallofus.org/data-tools/workbench/) and the [UKB-RAP](https://www.ukbiobank.ac.uk/use-our-data/research-analysis-platform/), respectively.

PRS models were constructed using genome-wide association study (GWAS) summary statistics from [**FinnGen**](https://www.finngen.fi/en) for European-ancestry analyses and the [**Million Veteran Program (MVP)**](https://www.research.va.gov/mvp/) for African-ancestry analyses. The ICD-10-to-Phecode mappings used to harmonize disease phenotypes are based on resources available through the [PheWAS Catalog](https://phewascatalog.org/).

## Overview

The analysis consists of four major steps:

1. **PRS library construction**  
   A trait-agnostic PRS library is constructed from GWAS summary statistics using multiple PRS methods, including **C+T**, **LDpred2**, and **lassosum2**.

2. **Cross-trait PRS evaluation and ranking**  
   Each PRS in the library is evaluated against multiple target diseases. Candidate PRSs are ranked according to their predictive performance for each target disease.

3. **Cross-trait PRS ensemble modeling**  
   The top-ranked PRSs for each target disease are integrated using multiple ensemble frameworks, including:
   - Generalized Linear Model (GLM)
   - SuperLearner
   - AutoGluon
   - TabPFN
   - UNSemblePRS

4. **Cross-biobank and cross-ancestry evaluation**  
   Cross-trait PRS selection patterns and ensemble performance are evaluated across independent biobanks and ancestry groups to assess reproducibility and transferability.

## Repository Structure

The project is organized into three components: the public code repository, the cross-trait PRS ranking database, and restricted individual-level biobank data.

### GitHub Repository

The GitHub repository contains the analysis code, publicly shareable reference data, and source code for the web-based ranking browser.

```text
CrosstraitPRS_Ensemble/
├── analysis/      # Analysis and figure-generation scripts
├── results/       # Summary-level results for analyses and figures
├── reference/     # Phenotype mappings and other reference files
├── web-tool/      # Source code for the Cross-Trait PRS Ranking Browser
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── README.md
└── LICENSE
```

## Cross-Trait PRS Ranking Database

As part of this study, we generated a comprehensive **cross-trait PRS ranking database** that records the predictive performance and ranking of candidate PRSs across target diseases. The complete database is released through the **GitHub Releases** section of this repository.

A web-based interface for interactively exploring the cross-trait PRS rankings is available: 

**[URL to Web-tool](URL_TO_WEB_TOOL)**

The database can be downloaded from the **GitHub Releases** section of this repository:

**[Download the Cross-Trait PRS Ranking Database](URL_TO_GITHUB_RELEASE)**

The database contains the following fields:

| Field | Description |
|---|---|
| `target_icd` | ICD-10 code of the target disease |
| `target_icd_description` | Description of the target disease |
| `target_icd_chapter` | ICD-10 chapter of the target disease |
| `candidate_icd` | ICD-10 code of the candidate PRS trait |
| `candidate_icd_description` | Description of the candidate PRS trait |
| `candidate_icd_chapter` | ICD-10 chapter of the candidate PRS trait |
| `rank` | Rank of the candidate PRS for the target disease |
| `auc` | Predictive performance measured by AUC |
| `method` | PRS construction method |
| `eval_biobank` | Biobank used for PRS evaluation |
| `eval_ancestry` | Ancestry group of the evaluation cohort |
| `eval_n_sample` | Number of participants in the evaluation cohort |
| `eval_n_case` | Number of cases for the target disease |
| `gwas_source` | Source of the GWAS summary statistics |
| `gwas_n_sample` | GWAS sample size |
| `gwas_n_case` | Number of cases in the GWAS |
| `pgs_download_link` | Download link for the corresponding PRS model |

## Requirements

The analyses were primarily performed using **Python** and **R** in cloud-based computing environments associated with the **All of Us Researcher Workbench** and **Google Cloud Platform**.

Major Python packages used in the analyses include:

- `numpy`
- `pandas`
- `scipy`
- `scikit-learn`
- `matplotlib`
- `seaborn`
- `statsmodels`
- `pyarrow`

Additional dependencies are required for individual ensemble frameworks, including:

- `autogluon`
- `tabpfn`
- `SuperLearner`

A complete environment specification is provided in `requirements.txt` or the corresponding environment configuration files.

To install the Python dependencies, run:

    pip install -r requirements.txt

## Citation

If you use the code or cross-trait PRS ranking database from this repository, please cite:

> Zhang J, et al. *[Manuscript title]*. [Journal / Preprint]. [Year].

Citation information will be updated upon publication.

## Contact

For questions regarding the code or cross-trait PRS ranking database, please open an issue in this repository.