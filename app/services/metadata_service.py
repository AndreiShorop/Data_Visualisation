from __future__ import annotations

import pandas as pd


class MetadataService:
    def classify_columns(self, df: pd.DataFrame) -> tuple[list[str], list[str]]:
        categorical: list[str] = []
        numeric: list[str] = []

        for column in df.columns:
            series = df[column]
            if pd.api.types.is_numeric_dtype(series):
                numeric.append(str(column))
            else:
                non_null = series.dropna().astype(str)
                unique_count = non_null.nunique()
                if unique_count <= 100:
                    categorical.append(str(column))
        return categorical, numeric

    def categorical_values(self, df: pd.DataFrame, column: str) -> list[str]:
        if not column or column not in df.columns:
            return []
        values = df[column].dropna().astype(str).value_counts().head(200).index.tolist()
        return values
