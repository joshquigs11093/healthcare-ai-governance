"""Executive board report generation (.spec §6.6, §2)."""

from healthcare_ai_governance.board_report.generator import (
    BoardReportData,
    build_board_report_data,
    generate_board_report_pdf,
)

__all__ = ["BoardReportData", "build_board_report_data", "generate_board_report_pdf"]
