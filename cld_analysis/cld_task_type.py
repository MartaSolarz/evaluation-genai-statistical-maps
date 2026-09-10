"""
Compact Letter Display (CLD) analysis for task types.
Based on Dunn's post-hoc test (after Kruskal-Wallis) with Benjamini-Hochberg FDR correction.

Input: data/cleaned_data/data_batch_only.csv
Output: results/cld_task_type_dunn_fdr_bh.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import kruskal
from scikit_posthocs import posthoc_dunn
from itertools import combinations
from string import ascii_lowercase

REPO_ROOT = Path(__file__).resolve().parent.parent

ALPHA = 0.05
DATA_PATH = REPO_ROOT / "data" / "cleaned_data" / "data_batch_only.csv"
OUTPUT_PATH = REPO_ROOT / "results" / "cld_task_type_dunn_fdr_bh.csv"


def is_clique(subset, not_sig_mat):
    """Check if all pairs in subset are not significantly different."""
    for i, j in combinations(subset, 2):
        if not not_sig_mat.loc[i, j]:
            return False
    return True


def find_maximal_cliques(groups, not_sig):
    """Find all maximal cliques of non-significantly different groups."""
    maximal_cliques = []

    for start in groups:
        clique = [start]
        for g in groups:
            if g == start:
                continue
            if is_clique(clique + [g], not_sig):
                clique.append(g)

        clique_set = frozenset(clique)
        is_subset = any(clique_set.issubset(frozenset(c)) for c in maximal_cliques)

        if not is_subset:
            maximal_cliques = [c for c in maximal_cliques if not frozenset(c).issubset(clique_set)]
            maximal_cliques.append(clique)

    return maximal_cliques


def greedy_set_cover(groups, maximal_cliques, not_sig_pairs):
    """Assign letters to groups using greedy set cover of non-significant pairs."""
    assigned_letters = {g: set() for g in groups}
    remaining_pairs = not_sig_pairs.copy()
    letter_idx = 0

    maximal_cliques.sort(key=len, reverse=True)

    while remaining_pairs:
        best_clique = None
        best_coverage = 0
        for clique in maximal_cliques:
            coverage = sum(1 for p in remaining_pairs if p[0] in clique and p[1] in clique)
            if coverage > best_coverage:
                best_coverage = coverage
                best_clique = clique

        if best_clique is None or best_coverage == 0:
            break

        letter = ascii_lowercase[letter_idx]
        letter_idx += 1
        for g in best_clique:
            assigned_letters[g].add(letter)

        remaining_pairs = {
            p for p in remaining_pairs
            if not (p[0] in best_clique and p[1] in best_clique)
        }

    # Assign unique letter to any group without letters (different from all)
    for g in groups:
        if not assigned_letters[g]:
            assigned_letters[g].add(ascii_lowercase[letter_idx])
            letter_idx += 1

    return assigned_letters


def compute_cld(posthoc, groups, alpha=0.05):
    """Compute Compact Letter Display from a post-hoc p-value matrix."""
    n = len(groups)

    # Boolean matrix: True if NOT significantly different
    not_sig = pd.DataFrame(True, index=groups, columns=groups)
    for i in range(n):
        for j in range(i + 1, n):
            g1, g2 = groups[i], groups[j]
            if posthoc.loc[g1, g2] < alpha:
                not_sig.loc[g1, g2] = False
                not_sig.loc[g2, g1] = False

    # Collect all non-significant pairs
    not_sig_pairs = set()
    for i in range(n):
        for j in range(i + 1, n):
            if not_sig.loc[groups[i], groups[j]]:
                not_sig_pairs.add((groups[i], groups[j]))

    maximal_cliques = find_maximal_cliques(groups, not_sig)
    assigned_letters = greedy_set_cover(groups, maximal_cliques, not_sig_pairs)

    return {g: "".join(sorted(v)) for g, v in assigned_letters.items()}


def verify_cld(cld, posthoc, groups, alpha=0.05):
    """Verify CLD: sig pairs share no letter, non-sig pairs share at least one."""
    n = len(groups)
    errors = []
    for i in range(n):
        for j in range(i + 1, n):
            g1, g2 = groups[i], groups[j]
            shared = set(cld[g1]) & set(cld[g2])
            if posthoc.loc[g1, g2] < alpha and shared:
                errors.append(f"{g1} vs {g2}: significant but share letter(s) {shared}")
            if posthoc.loc[g1, g2] >= alpha and not shared:
                errors.append(f"{g1} vs {g2}: not significant but share no letter")
    return errors


def main():
    df = pd.read_csv(DATA_PATH)

    # Kruskal-Wallis test
    groups_sorted = df.groupby("task_type")["score"].mean().sort_values(ascending=False).index.tolist()
    group_data = [df[df["task_type"] == g]["score"].values for g in groups_sorted]
    h_stat, p_val = kruskal(*group_data)

    n_obs = len(df)
    k = len(group_data)
    epsilon_sq = (h_stat - k + 1) / (n_obs - k)

    print(f"Kruskal-Wallis: H = {h_stat:.3f}, p = {p_val:.6f}, ε² = {epsilon_sq:.3f}")
    print(f"Significant: {'YES' if p_val < ALPHA else 'NO'}")
    print()

    if p_val >= ALPHA:
        print("Kruskal-Wallis not significant — no post-hoc test needed.")
        return

    # Dunn's post-hoc test with FDR BH correction
    posthoc = posthoc_dunn(df, val_col="score", group_col="task_type", p_adjust="fdr_bh")

    # Compute CLD
    cld = compute_cld(posthoc, groups_sorted, alpha=ALPHA)

    # Verify
    errors = verify_cld(cld, posthoc, groups_sorted, alpha=ALPHA)
    if errors:
        print("CLD verification FAILED:")
        for e in errors:
            print(f"  {e}")
        return
    print("CLD verification passed!")
    print()

    # Build and display results
    means = df.groupby("task_type")["score"].mean()
    medians = df.groupby("task_type")["score"].median()

    result = pd.DataFrame({
        "task_type": groups_sorted,
        "mean": [means[g] for g in groups_sorted],
        "median": [medians[g] for g in groups_sorted],
        "CLD": [cld[g] for g in groups_sorted],
    })

    print(f"{'Task type':<20} {'Mean':>8} {'Median':>8}  CLD")
    print("-" * 60)
    for _, row in result.iterrows():
        print(f"{row['task_type']:<20} {row['mean']:8.3f} {row['median']:8.3f}  {row['CLD']}")

    result.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
