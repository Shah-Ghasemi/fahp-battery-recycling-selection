import pandas as pd
import numpy as np
import re

from math import isnan

FUZZY_SCALE_FILE = "FuzzyScale.xlsx"
EXPERT_FILES = ["Expert1.xlsx", "Expert2.xlsx", "Expert3.xlsx"]

CRITERIA_SHEET = "Criteria"
CRITERION_SHEETS = [
    "Criterion1",
    "Criterion2",
    "Criterion3",
    "Criterion4",
    "Criterion5",
    "Criterion6",
]

RI_TABLE = {
    1: 0.00,
    2: 0.00,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49
}


def clean_text(text):
    if isinstance(text, str):
        text = text.replace("\xa0", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    return text


def load_fuzzy_scale(path):
    df = pd.read_excel(path)
    mapping = {}
    for _, row in df.iterrows():
        phrase = clean_text(row["Phrase"])
        mapping[phrase] = (float(row["L"]), float(row["M"]), float(row["U"]))
    return mapping


def read_tfn_matrix(file, sheet, fuzzy_mapping):
    df = pd.read_excel(file, sheet_name=sheet, header=0)
    row_names = df.iloc[:, 0].apply(clean_text).tolist()
    phrase_mat = df.iloc[:, 1:].applymap(clean_text)

    n = len(row_names)
    tfn_mat = np.zeros((n, n, 3), dtype=float)
    for i in range(n):
        for j in range(n):
            phrase = phrase_mat.iat[i, j]
            if phrase in (None, "") or (isinstance(phrase, float) and np.isnan(phrase)):
                tfn_mat[i, j] = (1.0, 1.0, 1.0)
            else:
                tfn_mat[i, j] = fuzzy_mapping[phrase]
    return row_names, tfn_mat


def aggregate_experts(sheet, fuzzy_mapping):
    names_ref = None
    mats = []
    for file in EXPERT_FILES:
        names, tfn = read_tfn_matrix(file, sheet, fuzzy_mapping)
        if names_ref is None:
            names_ref = names
        else:
            if names != names_ref:
                raise ValueError(f"Row mismatch in {file}, sheet {sheet}")
        mats.append(tfn)
    mats = np.array(mats)
    agg = np.prod(mats, axis=0) ** (1.0 / mats.shape[0])
    return names_ref, agg


def defuzzify_matrix_centroid(fuzzy_mat):
    l = fuzzy_mat[:, :, 0]
    m = fuzzy_mat[:, :, 1]
    h = fuzzy_mat[:, :, 2]
    crisp = (l + 2.0 * m + h) / 4.0
    return crisp


def compute_cr(A):
    n = A.shape[0]
    eigvals, _ = np.linalg.eig(A)
    lambda_max = np.max(eigvals.real)
    CI = (lambda_max - n) / (n - 1) if n > 1 else 0.0
    RI = RI_TABLE.get(n, 1.49)
    CR = CI / RI if RI != 0 else 0.0
    return lambda_max, CI, CR


def run_consistency():
    fuzzy_mapping = load_fuzzy_scale(FUZZY_SCALE_FILE)

    print("=== Criteria matrix ===")
    names, fuzzy_mat = aggregate_experts(CRITERIA_SHEET, fuzzy_mapping)
    A = defuzzify_matrix_centroid(fuzzy_mat)
    lam, CI, CR = compute_cr(A)
    print(f"n = {len(names)}, lambda_max = {lam:.4f}, CI = {CI:.4f}, CR = {CR:.4f}")
    print("OK" if CR < 0.10 else "NOT OK", "\n")

    for sheet in CRITERION_SHEETS:
        print(f"=== {sheet} ===")
        names_alt, fuzzy_mat_alt = aggregate_experts(sheet, fuzzy_mapping)
        A_alt = defuzzify_matrix_centroid(fuzzy_mat_alt)
        lam, CI, CRv = compute_cr(A_alt)
        print(
            f"n = {len(names_alt)}, lambda_max = {lam:.4f}, CI = {CI:.4f}, CR = {CRv:.4f}")
        print("OK" if CRv < 0.10 else "NOT OK", "\n")


if __name__ == "__main__":
    run_consistency()
