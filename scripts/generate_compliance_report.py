"""
Week 6: generate the EU AI Act compliance PDF.

Feeds fairness_audit.json through EthicsOfficer then assembles the PDF.
Output goes to outputs/reports/ AND photos/ (for Jawad).
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.ethics_officer import EthicsOfficer
from src.reports.compliance_pdf import ComplianceReportGenerator


def main():
    project_root = Path(__file__).parent.parent
    report_path  = project_root / "outputs/reports/fairness_audit.json"
    photos_dir   = project_root / "photos"

    if not report_path.exists():
        print("fairness_audit.json not found. Run scripts/evaluate_fairness.py first.")
        sys.exit(1)

    with open(report_path) as f:
        report = json.load(f)

    # ── Get EthicsOfficer text ────────────────────────────────────────────────
    print("Calling Ethics Officer (2 API calls)...")
    officer = EthicsOfficer()

    print("  [1/2] analyze_fairness_report...")
    analysis = officer.analyze_fairness_report(report)

    print("  [2/2] generate_compliance_summary...")
    summary  = officer.generate_compliance_summary(report)

    # ── Generate PDF ──────────────────────────────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"ethos_compliance_audit_{timestamp}.pdf"
    pdf_path = project_root / "outputs/reports" / pdf_filename

    print(f"\nBuilding PDF...")
    generator = ComplianceReportGenerator(
        plots_dir=str(project_root / "outputs/plots")
    )
    out = generator.generate(
        report=report,
        analysis_text=analysis,
        compliance_summary_text=summary,
        output_path=str(pdf_path),
    )
    size_kb = Path(out).stat().st_size // 1024
    print(f"  Generated: {pdf_filename}  ({size_kb} KB)")

    # ── Copy to photos/ ───────────────────────────────────────────────────────
    photos_dir.mkdir(exist_ok=True)
    photos_copy = photos_dir / pdf_filename
    shutil.copy2(out, photos_copy)
    print(f"  Copied to: photos/{pdf_filename}")

    print(f"\nDone. Open it:")
    print(f"  open \"{photos_copy}\"")


if __name__ == "__main__":
    main()
