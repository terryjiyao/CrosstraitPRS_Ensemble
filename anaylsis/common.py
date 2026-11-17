import pandas as pd
import os
import re
import numpy as np
import seaborn as sns

ROOT_PATH = "../"

# ICD chapter ranges
icd_chapters = {
    "A00-B99": "Infectious diseases",
    "C00-D49": "Neoplasms",
    "D50-D89": "Blood and immune disorders",
    "E00-E89": "Metabolic diseases",
    "F01-F99": "Mental disorders",
    "G00-G99": "Nervous system diseases",
    "H00-H59": "Eye diseases",
    "H60-H95": "Ear diseases",
    "I00-I99": "Circulatory diseases",
    "J00-J99": "Respiratory diseases",
    "K00-K95": "Digestive diseases",
    "L00-L99": "Skin diseases",
    "M00-M99": "Musculoskeletal diseases",
    "N00-N99": "Genitourinary diseases",
    "O00-O99": "Pregnancy and childbirth",
    "P00-P96": "Perinatal period conditions",
    "Q00-Q99": "Congenital disorder",
    "R00-R99": "Symptoms and abnormal findings",
    "S00-T88": "Injury and external causes",
    "V00-Y99": "External causes of morbidity",
    "Z00-Z99": "Health factors",
    "U00-U85": "Special purposes",
}
# Roman numerals aligned with the 22 official ICD-10 chapter numbers (I .. XXII)
roman_numerals = [
    "I", "II", "III", "IV", "V",
    "VI", "VII", "VIII", "IX", "X",
    "XI", "XII", "XIII", "XIV", 
    "XV", "XVI", "XVII", "XVIII","XIX", "XX",
    "XXI", "XXII",
]
chapter2roman_map = {v: r for v, r in zip(icd_chapters.values(), roman_numerals)}
roman2chapter_map = {v: k for k, v in chapter2roman_map.items()}

# color palette
colors = sns.color_palette("tab20", len(roman_numerals))
roman2color_map = dict(zip(roman_numerals, colors))
chapter2color_map = dict(zip(icd_chapters.values(), colors))

### map icd to icd chapters ###

def parse_code(code):
    m = re.match(r"([A-Z]+)(\d+)", str(code))
    if not m:
        return None, None
    letter, number = m.groups()
    number = number[:2]
    return letter, int(number)

def in_range(code, start, end):
    start_l, start_n = parse_code(start)
    end_l, end_n = parse_code(end)
    code_l, code_n = parse_code(code)
    if start_l > code_l:
        return False
    if end_l < code_l:
        return False
    else:
        if start_l < code_l < end_l:
            return True
        if start_l == code_l and end_l == code_l and code_n >= start_n and code_n <= end_n:
            return True
        if start_l == code_l and end_l != code_l and code_n >= start_n:
            return True
        if start_l < code_l and end_l == code_l and code_n <= end_n:
            return True
    return False

def assign_chapter(icd_code):
    # Non-ICD endpoints (e.g. DEATH) have no numeric part; handle them before range matching
    if parse_code(icd_code)[0] is None:
        return "Death" if str(icd_code).upper() == "DEATH" else "Unknown"
    for rng, name in icd_chapters.items():
        start, end = rng.split("-")
        if in_range(icd_code, start, end):
            return name
    return "Unknown"

# generate map between phecode and icd
phecode2icd = pd.read_csv(os.path.join(ROOT_PATH, "reference_data", "european_icd_phenocode_pairs.csv"))
phecode2icd_map = dict(zip(phecode2icd["phenocode"], phecode2icd["icd"]))
icd2phecode_map = {v: k for k, v in phecode2icd_map.items()}