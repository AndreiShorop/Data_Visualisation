from __future__ import annotations

import pandas as pd


class MetadataService:
    def classify_columns(self, df: pd.DataFrame, schema_hints: dict[str, list[str]] | None = None) -> tuple[list[str], list[str], list[str], list[str]]:
        hints = schema_hints or {}
        hinted_dates = set(hints.get("date_columns", []))
        hinted_multi = set(hints.get("multi_value_columns", []))

        categorical: list[str] = []
        numeric: list[str] = []
        date_columns: list[str] = []
        multi_value_columns: list[str] = []

        for column in df.columns:
            series = df[column]
            col_name = str(column)

            if col_name in hinted_multi:
                multi_value_columns.append(col_name)

            if col_name in hinted_dates:
                date_columns.append(col_name)
                continue

            if pd.api.types.is_numeric_dtype(series):
                numeric.append(col_name)
            else:
                non_null = series.dropna().astype(str)
                unique_count = non_null.nunique()
                if unique_count <= 100:
                    categorical.append(col_name)

                parsed = pd.to_datetime(non_null.head(200), errors="coerce", format="mixed")
                parse_ratio = (parsed.notna().sum() / len(non_null.head(200))) if len(non_null.head(200)) else 0
                if parse_ratio >= 0.7 and col_name not in date_columns:
                    date_columns.append(col_name)

        for col in date_columns:
            if col in categorical:
                categorical.remove(col)

        return categorical, numeric, date_columns, multi_value_columns

    def categorical_values(self, df: pd.DataFrame, column: str) -> list[str]:
        if not column or column not in df.columns:
            return []
        values = df[column].dropna().astype(str).value_counts().head(200).index.tolist()
        return values

    def multi_values(self, df: pd.DataFrame, column: str) -> list[str]:
        if not column or column not in df.columns:
            return []
        tokens: dict[str, int] = {}
        for value in df[column].dropna().astype(str):
            for token in value.split(","):
                cleaned = token.strip()
                if cleaned:
                    tokens[cleaned] = tokens.get(cleaned, 0) + 1
        return [k for k, _ in sorted(tokens.items(), key=lambda item: item[1], reverse=True)[:200]]
