from __future__ import annotations

import pandas as pd
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class ComparisonResult:
    added_rows: int
    removed_rows: int
    changed_cells: int
    structure_diff: Dict[str, List[str]]
    stats_diff: pd.DataFrame
    diff_sample: pd.DataFrame

class ComparisonService:
    def compare(self, df1: pd.DataFrame, df2: pd.DataFrame, key_col: str | None = None) -> ComparisonResult:
        # 1. Structure Diff
        added_cols = [c for c in df2.columns if c not in df1.columns]
        removed_cols = [c for c in df1.columns if c not in df2.columns]
        common_cols = [c for c in df1.columns if c in df2.columns]

        # 2. Row changes (basic if no key)
        if key_col and key_col in df1.columns and key_col in df2.columns:
            # Set index for comparison
            d1 = df1.set_index(key_col)
            d2 = df2.set_index(key_col)
            
            added_indices = d2.index.difference(d1.index)
            removed_indices = d1.index.difference(d2.index)
            common_indices = d1.index.intersection(d2.index)
            
            added_rows = len(added_indices)
            removed_rows = len(removed_indices)
            
            # Cell changes in common rows/cols
            changed_cells = 0
            if not common_indices.empty and common_cols:
                # Align dataframes
                sub1 = d1.loc[common_indices, [c for c in common_cols if c != key_col]]
                sub2 = d2.loc[common_indices, [c for c in common_cols if c != key_col]]
                
                # Check for changes (simplified)
                # Note: this is expensive for 100k+ rows, we use vectorized comparison
                diff_mask = (sub1 != sub2) & ~(sub1.isna() & sub2.isna())
                changed_cells = diff_mask.sum().sum()
                
                # Create a sample of differences
                diff_sample = sub2[diff_mask.any(axis=1)].head(10)
            else:
                diff_sample = pd.DataFrame()
        else:
            # Fallback if no key column
            added_rows = max(0, len(df2) - len(df1))
            removed_rows = max(0, len(df1) - len(df2))
            changed_cells = 0 # Cannot accurately track without key
            diff_sample = pd.DataFrame()

        # 3. Stats Diff
        stats1 = df1.describe().T
        stats2 = df2.describe().T
        stats_diff = stats2 - stats1

        return ComparisonResult(
            added_rows=added_rows,
            removed_rows=removed_rows,
            changed_cells=int(changed_cells),
            structure_diff={
                "added": added_cols,
                "removed": removed_cols
            },
            stats_diff=stats_diff,
            diff_sample=diff_sample
        )
