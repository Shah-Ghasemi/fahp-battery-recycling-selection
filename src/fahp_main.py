import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re


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


CRITERION_MAP = {
    "Criterion1": "Cost",
    "Criterion2": "Enviromental",
    "Criterion3": "Industrial scale",
    "Criterion4": "Process complexity",
    "Criterion5": "Access to resources",
    "Criterion6": "Recycling purity",
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
                if phrase not in fuzzy_mapping:
                    raise KeyError(
                        f"Phrase '{phrase}' not found in fuzzy scale.")
                tfn_mat[i, j] = fuzzy_mapping[phrase]

    return row_names, tfn_mat


def aggregate_experts(sheet, fuzzy_mapping):

    names_ref = None
    mats = []

    for file in EXPERT_FILES:
        names, tfn_mat = read_tfn_matrix(file, sheet, fuzzy_mapping)
        if names_ref is None:
            names_ref = names
        else:
            if names != names_ref:
                raise ValueError(
                    f"Row names mismatch in {file}, sheet {sheet}")
        mats.append(tfn_mat)

    mats = np.array(mats)
    agg = np.prod(mats, axis=0) ** (1.0 / mats.shape[0])
    return names_ref, agg


def fuzzy_row_geometric_weights(fuzzy_mat):

    n = fuzzy_mat.shape[0]
    row_g = np.ones((n, 3), dtype=float)
    for i in range(n):
        row_g[i] = np.prod(fuzzy_mat[i, :, :], axis=0) ** (1.0 / n)
    sum_g = np.sum(row_g, axis=0)
    return row_g / sum_g


def defuzzify_centroid(fuzzy_w):

    l = fuzzy_w[:, 0]
    m = fuzzy_w[:, 1]
    h = fuzzy_w[:, 2]
    crisp = (l + 2.0 * m + h) / 4.0
    crisp = crisp / crisp.sum()
    return crisp


def run_fahp():
    fuzzy_mapping = load_fuzzy_scale(FUZZY_SCALE_FILE)

    crit_names, crit_fuzzy_mat = aggregate_experts(
        CRITERIA_SHEET, fuzzy_mapping)
    crit_fuzzy_w = fuzzy_row_geometric_weights(crit_fuzzy_mat)
    crit_weights = defuzzify_centroid(crit_fuzzy_w)   # طول 6

    crit_weight_dict = {
        clean_text(name): w for name, w in zip(crit_names, crit_weights)
    }

    df_crit = pd.DataFrame({
        "Criteria": crit_names,
        "Weight": crit_weights
    })
    df_crit.to_excel("FAHP_Criteria_Weights.xlsx", index=False)
    print("Saved: FAHP_Criteria_Weights.xlsx")

    alt_names_ref = None
    local_weights_dict = {}

    for sheet in CRITERION_SHEETS:
        crit_name_raw = CRITERION_MAP[sheet]
        crit_name = clean_text(crit_name_raw)

        names_alt, alt_fuzzy_mat = aggregate_experts(sheet, fuzzy_mapping)
        if alt_names_ref is None:
            alt_names_ref = names_alt
        else:
            if names_alt != alt_names_ref:
                raise ValueError(
                    f"Alternative names mismatch in sheet {sheet}")

        alt_fuzzy_w = fuzzy_row_geometric_weights(alt_fuzzy_mat)
        alt_crisp_w = defuzzify_centroid(alt_fuzzy_w)

        local_weights_dict[crit_name] = alt_crisp_w

    df_local = pd.DataFrame({"Alternative": alt_names_ref})
    for name in crit_names:
        c = clean_text(name)
        df_local[name] = local_weights_dict[c]

    df_local.to_excel("FAHP_Local_Alternative_Weights.xlsx", index=False)
    print("Saved: FAHP_Local_Alternative_Weights.xlsx")

    n_alt = len(alt_names_ref)
    global_w = np.zeros(n_alt, dtype=float)

    for name in crit_names:
        c = clean_text(name)
        w_c = crit_weight_dict[c]
        w_local = local_weights_dict[c]
        global_w += w_c * w_local

    global_w = global_w / global_w.sum()

    df_final = pd.DataFrame({
        "Alternative": alt_names_ref,
        "GlobalWeight": global_w
    }).sort_values(by="GlobalWeight", ascending=False).reset_index(drop=True)

    df_final.to_excel("FAHP_Final_Ranking.xlsx", index=False)
    print("Saved: FAHP_Final_Ranking.xlsx")

    plt.figure(figsize=(10, 6))
    plt.bar(df_final["Alternative"], df_final["GlobalWeight"])
    plt.xticks(rotation=90)
    plt.ylabel("Global Priority")
    plt.title("FAHP Final Ranking of Alternatives")
    plt.tight_layout()
    plt.savefig("FAHP_Final_Ranking.png", dpi=300)
    print("Saved: FAHP_Final_Ranking.png")

    print("\n✅ FAHP finished successfully.")


if __name__ == "__main__":
    run_fahp()
