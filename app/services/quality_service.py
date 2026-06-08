from __future__ import annotations

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class QualityIssue:
    column: str
    issue_type: str
    severity: str  # 'low', 'medium', 'high'
    description: str

@dataclass
class QualityReport:
    score: int
    missing_count: int
    duplicate_count: int
    issues: List[QualityIssue]
    recommendations: List[str]
    column_stats: Dict[str, Any]

class QualityService:
    def analyze(self, df: pd.DataFrame) -> QualityReport:
        issues = []
        recommendations = []
        
        # 1. Missing values
        missing_stats = df.isnull().sum()
        total_missing = missing_stats.sum()
        
        for col, count in missing_stats.items():
            if count > 0:
                pct = (count / len(df)) * 100
                severity = 'high' if pct > 30 else 'medium' if pct > 5 else 'low'
                issues.append(QualityIssue(
                    column=str(col),
                    issue_type="Missing Values",
                    severity=severity,
                    description=f"{count} ({pct:.1f}%) missing values"
                ))
                if pct > 30:
                    recommendations.append(f"Column '{col}' has a high percentage of missing values. Consider dropping it or using imputation.")

        # 2. Duplicates
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            issues.append(QualityIssue(
                column="All",
                issue_type="Duplicates",
                severity="medium",
                description=f"{dup_count} duplicate rows found"
            ))
            recommendations.append(f"Found {dup_count} duplicate rows. Consider removing them to avoid biased analysis.")

        # 3. Constant columns
        for col in df.columns:
            if df[col].nunique() == 1:
                issues.append(QualityIssue(
                    column=str(col),
                    issue_type="Constant Column",
                    severity="low",
                    description="Column has only one unique value"
                ))
                recommendations.append(f"Column '{col}' is constant and provides no information for analysis.")

        # 4. Outliers (IQR method for numeric columns)
        num_cols = df.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            if not outliers.empty:
                count = len(outliers)
                pct = (count / len(df)) * 100
                issues.append(QualityIssue(
                    column=str(col),
                    issue_type="Outliers",
                    severity="low" if pct < 5 else "medium",
                    description=f"{count} ({pct:.1f}%) outliers detected"
                ))

        # 5. Type Mismatches (simple check for mixed types in object columns)
        for col in df.select_dtypes(include=['object']).columns:
            types = df[col].apply(type).nunique()
            if types > 1:
                issues.append(QualityIssue(
                    column=str(col),
                    issue_type="Structural Error",
                    severity="medium",
                    description="Mixed data types found in column"
                ))

        # Calculate Score (simple heuristic)
        base_score = 100
        penalties = 0
        penalties += (total_missing / (len(df) * len(df.columns))) * 50 if len(df) > 0 else 0
        penalties += (dup_count / len(df)) * 20 if len(df) > 0 else 0
        penalties += len([i for i in issues if i.severity == 'high']) * 10
        penalties += len([i for i in issues if i.severity == 'medium']) * 5
        
        score = max(0, int(base_score - penalties))

        return QualityReport(
            score=score,
            missing_count=int(total_missing),
            duplicate_count=int(dup_count),
            issues=issues,
            recommendations=list(set(recommendations)),
            column_stats=missing_stats.to_dict()
        )
