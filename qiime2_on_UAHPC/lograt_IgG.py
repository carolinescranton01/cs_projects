#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 20 11:23:04 2025

@author: carolinescranton
"""

import numpy as np
import pandas as pd

df = pd.read_csv('16S_Illumina_taxonomy_IgG.csv')

# Keep only positive + negative
df = df[(df['fraction'] == 'positive') | (df['fraction'] == 'negative')]

# Sort for prettier output
df = df.sort_values(by=[
    'kitid', 'kingdom', 'phylum', 'class', 'order', 'family',
    'genus', 'species'
])


# ---------------------------------------------------------
# Function 1: FULL TAXONOMIC RESOLUTION
# ---------------------------------------------------------
def calculate_log_ratio(df):
    """Calculate log10(positive/negative) for each OTU for each participant."""

    pivot_df = df.pivot_table(
        index=[
            'kingdom', 'phylum', 'class', 'order', 'family',
            'genus', 'species', 'kitid'
        ],
        columns='fraction',
        values='abundance',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    pivot_df['log_ratio'] = np.log10(pivot_df['positive'] / pivot_df['negative'])

    result_df = pivot_df[['kingdom', 'phylum', 'class', 'order', 'family',
                          'genus', 'species', 'kitid',
                          'positive', 'negative', 'log_ratio']]

    # Handle +inf
    inf_mask = result_df['log_ratio'] == np.inf
    result_df['log_ratio'] = result_df['log_ratio'].astype(object)
    result_df.loc[inf_mask, 'log_ratio'] = (
        np.log10(result_df.loc[inf_mask, 'positive']).astype(str) + '_inf'
    )

    # Remove -inf and NaN
    result_df = result_df[result_df['log_ratio'] != -np.inf]
    result_df = result_df.dropna()

    return result_df



# ---------------------------------------------------------
# Function 2: family-ONLY RESOLUTION
# ---------------------------------------------------------
def calculate_log_ratio_family(df):
    """Collapse abundances to family level per participant, then calculate log10 ratio."""

    # Collapse to family level
    df_family = df.groupby(
        ['kitid', 'kingdom', 'phylum', 'class', 'order', 'family', 'fraction'],
        as_index=False
    )['abundance'].sum()

    pivot_df = df_family.pivot_table(
        index=['kingdom', 'phylum', 'class', 'order', 'family', 'kitid'],
        columns='fraction',
        values='abundance',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    pivot_df['log_ratio'] = np.log10(pivot_df['positive'] / pivot_df['negative'])

    result_df = pivot_df[['kingdom', 'phylum', 'class', 'order', 'family',
                          'kitid', 'positive', 'negative', 'log_ratio']]

    # Handle +inf
    inf_mask = result_df['log_ratio'] == np.inf
    result_df['log_ratio'] = result_df['log_ratio'].astype(object)
    result_df.loc[inf_mask, 'log_ratio'] = (
        np.log10(result_df.loc[inf_mask, 'positive']).astype(str) + '_inf'
    )

    # Remove -inf and NaN
    result_df = result_df[result_df['log_ratio'] != -np.inf]
    result_df = result_df.dropna()

    return result_df



# ---------------------------------------------------------
# Function 3: Genus-ONLY RESOLUTION
# ---------------------------------------------------------
def calculate_log_ratio_genus(df):
    """Collapse abundances to genus level per participant, then calculate log10 ratio."""

    # Collapse to genus level
    df_genus = df.groupby(
        ['kitid', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'fraction'],
        as_index=False
    )['abundance'].sum()

    pivot_df = df_genus.pivot_table(
        index=['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'kitid'],
        columns='fraction',
        values='abundance',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    pivot_df['log_ratio'] = np.log10(pivot_df['positive'] / pivot_df['negative'])

    result_df = pivot_df[['kingdom', 'phylum', 'class', 'order', 'family', 'genus',
                          'kitid', 'positive', 'negative', 'log_ratio']]

    # Handle +inf
    inf_mask = result_df['log_ratio'] == np.inf
    result_df['log_ratio'] = result_df['log_ratio'].astype(object)
    result_df.loc[inf_mask, 'log_ratio'] = (
        np.log10(result_df.loc[inf_mask, 'positive']).astype(str) + '_inf'
    )

    # Remove -inf and NaN
    result_df = result_df[result_df['log_ratio'] != -np.inf]
    result_df = result_df.dropna()

    return result_df


# ---------------------------------------------------------
# Run both + write outputs
# ---------------------------------------------------------
if __name__ == "__main__":

    # Full taxonomy
    result_all = calculate_log_ratio(df)
    result_all.to_csv('out_all_IgG.csv', index=False)
    print("Wrote out_all_IgG.csv")

    # family-only
    result_family = calculate_log_ratio_family(df)
    result_family.to_csv('out_family_IgG.csv', index=False)
    print("Wrote out_family_IgG.csv")

    # genus-only
    result_genus = calculate_log_ratio_genus(df)
    result_genus.to_csv('out_genus_IgG.csv', index=False)
    print("Wrote out_genus_IgG.csv")
