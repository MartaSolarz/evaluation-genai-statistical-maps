"""
Sensitivity Analysis of Weighting Schemes for Response Quality Index (RQI).

Compares 4 weighting schemes and evaluates ranking stability using Spearman's rho.
"""

import pandas as pd
import numpy as np
from scipy.stats import spearmanr

# --- Load data ---
df = pd.read_csv("pure_data/results.csv")
df_batch = df[df["test_mode"] == "batch"].copy()

assert len(df_batch) == 1728, f"Expected 1728 batch rows, got {len(df_batch)}"

# --- Define sub-criteria groups ---
A_cols = ["A1", "A2", "A3"]
B_cols = ["B1", "B2", "B3"]
C_cols = ["C1", "C2", "C3", "C4"]
D_cols = ["D1", "D2", "D3", "D4"]

# Compute group sums
df_batch["sum_A"] = df_batch[A_cols].sum(axis=1)
df_batch["sum_B"] = df_batch[B_cols].sum(axis=1)
df_batch["sum_C"] = df_batch[C_cols].sum(axis=1)
df_batch["sum_D"] = df_batch[D_cols].sum(axis=1)

# --- Weighting schemes ---
schemes = {
    "S0": {"A": 0.50, "B": 0.10, "C": 0.20, "D": 0.20},  # original
    "S1": {"A": 0.25, "B": 0.25, "C": 0.25, "D": 0.25},  # equal
    "S2": {"A": 0.70, "B": 0.05, "C": 0.125, "D": 0.125},  # accuracy-focused
    "S3": {"A": 0.40, "B": 0.10, "C": 0.25, "D": 0.25},  # balanced
}

# --- Compute RQI for each scheme (with conditional zero rule) ---
for name, weights in schemes.items():
    rqi = (
        weights["A"] * df_batch["sum_A"]
        + weights["B"] * df_batch["sum_B"]
        + weights["C"] * df_batch["sum_C"]
        + weights["D"] * df_batch["sum_D"]
    )
    # Conditional zero rule: if A1 == 0, entire score = 0
    rqi = rqi.where(df_batch["A1"] != 0, 0)
    df_batch[f"RQI_{name}"] = rqi

# --- Mean per model and rankings ---
models = df_batch.groupby("model_name")

results = []
for name, weights in schemes.items():
    means = models[f"RQI_{name}"].mean()
    means = means.rename(f"Mean_{name}")
    results.append(means)

result_df = pd.concat(results, axis=1)

# Add ranks (1 = best = highest score)
for name in schemes:
    result_df[f"Rank_{name}"] = result_df[f"Mean_{name}"].rank(ascending=False, method="min").astype(int)

# Reorder columns
cols = []
for name in schemes:
    cols.extend([f"Mean_{name}", f"Rank_{name}"])
result_df = result_df[cols]
result_df.index.name = "Model"
result_df = result_df.sort_values("Rank_S0")

# Round means
for name in schemes:
    result_df[f"Mean_{name}"] = result_df[f"Mean_{name}"].round(4)

# --- Save CSV ---
result_df.to_csv("sensitivity_analysis_results.csv")
print("=== Sensitivity Analysis Results ===\n")
print(result_df.to_string())

# --- Spearman's rho ---
print("\n\n=== Spearman's Rank Correlations (S0 vs alternatives) ===\n")

spearman_results = []
for name in ["S1", "S2", "S3"]:
    rho, pval = spearmanr(result_df[f"Rank_S0"], result_df[f"Rank_{name}"])
    spearman_results.append({"Comparison": f"S0 vs {name}", "rho": round(rho, 4), "p_value": round(pval, 6)})
    print(f"S0 vs {name}: rho = {rho:.4f}, p = {pval:.6f}")

# --- Summary ---
summary_lines = [
    "Sensitivity Analysis of RQI Weighting Schemes",
    "=" * 50,
    "",
    "Weighting Schemes:",
    "  S0 (original):        A=50%, B=10%, C=20%, D=20%",
    "  S1 (equal):           A=25%, B=25%, C=25%, D=25%",
    "  S2 (accuracy-focused): A=70%, B=5%, C=12.5%, D=12.5%",
    "  S3 (balanced):        A=40%, B=10%, C=25%, D=25%",
    "",
    "Conditional zero rule: if A1=0, entire RQI score = 0",
    f"Data: {len(df_batch)} batch responses (12 models x 16 maps x 9 questions)",
    "",
    "Spearman's Rank Correlations (S0 vs alternatives):",
    "-" * 50,
]

stability_assessment = []
for sr in spearman_results:
    rho = sr["rho"]
    pval = sr["p_value"]
    if rho > 0.9:
        stability = "very stable"
    elif rho >= 0.8:
        stability = "stable"
    else:
        stability = "UNSTABLE - requires comment"
    summary_lines.append(f"  {sr['Comparison']}: rho = {rho:.4f}, p = {pval:.6f} -> {stability}")
    stability_assessment.append((sr["Comparison"], rho, stability))

summary_lines.append("")
summary_lines.append("Overall Assessment:")
summary_lines.append("-" * 50)

all_rhos = [sr["rho"] for sr in spearman_results]
min_rho = min(all_rhos)

if min_rho > 0.9:
    summary_lines.append(
        f"All correlations are very high (min rho = {min_rho:.4f}). "
        "Model rankings are VERY STABLE across all weighting schemes. "
        "The choice of weights does not substantially affect the relative ordering of models."
    )
elif min_rho >= 0.8:
    summary_lines.append(
        f"All correlations are high (min rho = {min_rho:.4f}). "
        "Model rankings are STABLE across weighting schemes. "
        "Minor rank changes exist but overall ordering is preserved."
    )
else:
    unstable = [s for s in stability_assessment if s[2].startswith("UNSTABLE")]
    summary_lines.append(
        f"Some correlations are below 0.8 (min rho = {min_rho:.4f}). "
        "Rankings show SENSITIVITY to the weighting scheme. "
        f"Unstable comparisons: {', '.join(u[0] for u in unstable)}. "
        "The choice of weights materially affects model rankings — "
        "results should be interpreted with caution."
    )

summary_lines.append("")
summary_lines.append("Model Rankings by Scheme:")
summary_lines.append("-" * 50)
for _, row in result_df.iterrows():
    model = row.name
    ranks = [str(int(row[f"Rank_{s}"])) for s in schemes]
    summary_lines.append(f"  {model:<25s} S0={ranks[0]:>2s}  S1={ranks[1]:>2s}  S2={ranks[2]:>2s}  S3={ranks[3]:>2s}")

summary_text = "\n".join(summary_lines)

with open("sensitivity_analysis_summary.txt", "w") as f:
    f.write(summary_text)

print(f"\n\n{summary_text}")
print("\n\nFiles saved:")
print("  - sensitivity_analysis_results.csv")
print("  - sensitivity_analysis_summary.txt")
