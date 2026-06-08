from __future__ import annotations

import pandas as pd
from fpdf import FPDF
import io
import re
from typing import Dict, Any

class ExportService:
    """Service for exporting data and reports into various formats with security in mind."""

    def to_excel(self, dfs: Dict[str, pd.DataFrame]) -> bytes:
        """
        Exports multiple DataFrames to an Excel file bytes stream.
        Applies sanitation to prevent Formula Injection.
        """
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for name, df in dfs.items():
                # Sanitize sheet name
                clean_name = self.sanitize_sheet_name(name)
                # Sanitize data to prevent Formula Injection (working on a copy)
                safe_df = self._sanitize_for_formula_injection(df)
                safe_df.to_excel(writer, sheet_name=clean_name, index=False)
        return output.getvalue()

    def sanitize_sheet_name(self, name: str) -> str:
        """
        Cleans sheet names to be compatible with Excel limits and forbidden characters.
        Forbidden: : \ / ? * [ ]
        """
        # Replace forbidden characters with underscore
        clean_name = re.sub(r'[:\\/?*\[\]]', '_', str(name))
        # Limit length to 31 characters
        clean_name = clean_name[:31].strip()
        # Fallback if empty
        return clean_name if clean_name else "Sheet"

    def _sanitize_for_formula_injection(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prevents Excel Formula Injection by prefixing suspicious string values with a single quote.
        Targets values starting with =, +, -, @.
        """
        df_copy = df.copy()
        # Scan only object/string columns
        for col in df_copy.select_dtypes(include=['object']):
            # Vectorized prefixing for performance
            # Convert to string for checking but preserve NaNs
            mask = df_copy[col].astype(str).str.startswith(('=', '+', '-', '@'), na=False)
            df_copy.loc[mask, col] = "'" + df_copy.loc[mask, col].astype(str)
        return df_copy

    def quality_report_to_pdf(self, report_data: Dict[str, Any]) -> bytes:
        """
        Generates a PDF report from data quality analysis results with safe text handling.
        Uses multi_cell for text wrapping and includes error handling.
        """
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Using standard fonts
            pdf.set_font("helvetica", 'B', 16)
            pdf.cell(0, 10, "Data Quality Report", ln=True, align='C')
            pdf.ln(10)
            
            pdf.set_font("helvetica", '', 12)
            pdf.cell(0, 10, f"Quality Score: {report_data.get('score', 'N/A')}/100", ln=True)
            pdf.cell(0, 10, f"Total Missing Values: {report_data.get('missing_count', 0)}", ln=True)
            pdf.cell(0, 10, f"Duplicate Rows: {report_data.get('duplicate_count', 0)}", ln=True)
            pdf.ln(10)
            
            pdf.set_font("helvetica", 'B', 14)
            pdf.cell(0, 10, "Issues detected:", ln=True)
            pdf.ln(5)
            
            pdf.set_font("helvetica", '', 10)
            issues = report_data.get('issues', [])
            if not issues:
                pdf.cell(0, 10, "No significant issues detected.", ln=True)
            else:
                for issue in issues:
                    severity = str(getattr(issue, 'severity', 'low')).upper()
                    col = str(getattr(issue, 'column', 'Unknown'))
                    issue_type = str(getattr(issue, 'issue_type', 'General'))
                    desc = str(getattr(issue, 'description', ''))
                    
                    text = f"[{severity}] {col}: {issue_type} - {desc}"
                    # Use multi_cell for automatic line wrapping
                    pdf.multi_cell(0, 7, text)
                    pdf.ln(2)
                    
            return pdf.output()
        except Exception as e:
            # Return a simple error indicator in case of failure to prevent total crash
            return f"Error generating PDF: {str(e)}".encode('utf-8')
