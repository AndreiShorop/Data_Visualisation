from __future__ import annotations

import pandas as pd
from fpdf import FPDF
import io

class ExportService:
    def to_excel(self, dfs: dict[str, pd.DataFrame]) -> bytes:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for name, df in dfs.items():
                df.to_excel(writer, sheet_name=name[:31]) # Excel limit
        return output.getvalue()

    def quality_report_to_pdf(self, report_data: dict) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(40, 10, "Data Quality Report")
        pdf.ln(20)
        
        pdf.set_font("Arial", '', 12)
        pdf.cell(40, 10, f"Quality Score: {report_data.get('score', 'N/A')}/100")
        pdf.ln(10)
        pdf.cell(40, 10, f"Total Missing Values: {report_data.get('missing_count', 0)}")
        pdf.ln(10)
        pdf.cell(40, 10, f"Duplicate Rows: {report_data.get('duplicate_count', 0)}")
        pdf.ln(20)
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(40, 10, "Issues detected:")
        pdf.ln(10)
        
        pdf.set_font("Arial", '', 10)
        for issue in report_data.get('issues', []):
            pdf.cell(0, 10, f"[{issue.severity.upper()}] {issue.column}: {issue.issue_type} - {issue.description}")
            pdf.ln(6)
            
        return pdf.output()
