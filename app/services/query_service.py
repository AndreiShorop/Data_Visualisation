from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from app.models.state import FilterState, SortSpec


class QueryService:
    def apply_filters_and_sorts(
        self,
        source_df: pd.DataFrame,
        filters: FilterState,
        sorts: Sequence[SortSpec],
    ) -> pd.DataFrame:
        df = source_df.copy()

        df = self._apply_text_filter(df, filters.text_query)
        df = self._apply_categorical_filter(df, filters.categorical_column, filters.categorical_value)
        df = self._apply_numeric_range(df, filters.numeric_column, filters.min_value, filters.max_value)
        df = self._apply_sorts(df, sorts)
        return df

    def _apply_text_filter(self, df: pd.DataFrame, query: str) -> pd.DataFrame:
        search = query.strip().lower()
        if not search:
            return df

        mask = pd.Series(False, index=df.index)
        for column in df.columns:
            as_text = df[column].astype(str).str.lower()
            mask = mask | as_text.str.contains(search, na=False)
        return df[mask]

    def _apply_categorical_filter(self, df: pd.DataFrame, column: str, value: str) -> pd.DataFrame:
        if not column or not value or column not in df.columns:
            return df

        series = df[column].astype(str)
        exact = df[series == value]
        if not exact.empty:
            return exact

        # Support token-based filtering for comma-separated categorical fields.
        token_mask = series.str.split(",").apply(lambda tokens: value in [token.strip() for token in tokens])
        return df[token_mask]

    def _apply_numeric_range(self, df: pd.DataFrame, column: str, min_value: str, max_value: str) -> pd.DataFrame:
        if not column or column not in df.columns:
            return df

        numeric = pd.to_numeric(df[column], errors="coerce")
        result = df.copy()
        result["__num__"] = numeric

        if min_value.strip():
            try:
                minimum = float(min_value)
                result = result[result["__num__"] >= minimum]
            except ValueError:
                pass

        if max_value.strip():
            try:
                maximum = float(max_value)
                result = result[result["__num__"] <= maximum]
            except ValueError:
                pass

        result = result.drop(columns=["__num__"])
        return result

    def _apply_sorts(self, df: pd.DataFrame, sorts: Sequence[SortSpec]) -> pd.DataFrame:
        valid = [spec for spec in sorts if spec.column in df.columns]
        if not valid:
            return df

        by = [spec.column for spec in valid]
        ascending = [spec.ascending for spec in valid]
        return df.sort_values(by=by, ascending=ascending, kind="mergesort")
