"""
Week 5 smoke test: feed the Day 7 fairness audit JSON to EthicsOfficer
and print Claude's plain-English analysis.

Run:
    /opt/miniconda3/envs/ethos/bin/python3 scripts/smoke_test_ethics_officer.py
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.ethics_officer import EthicsOfficer

REPORT_PATH = Path("outputs/reports/fairness_audit.json")


def main():
    # Load the Day 7 fairness audit
    if not REPORT_PATH.exists():
        print(f"Report not found at {REPORT_PATH}")
        print("Run scripts/evaluate_fairness.py first.")
        sys.exit(1)

    with open(REPORT_PATH) as f:
        report = json.load(f)

    print("Initialising EthicsOfficer...")
    officer = EthicsOfficer()
    print(f"  Model: claude-sonnet-4-5")
    print(f"  Report: {REPORT_PATH}  ({len(json.dumps(report))} chars)\n")

    print("=" * 70)
    print("ETHICS OFFICER — FAIRNESS ANALYSIS")
    print("=" * 70)

    analysis = officer.analyze_fairness_report(report)
    print(analysis)

    print("\n" + "=" * 70)
    print("Smoke test complete. Cache populated — second call is instant.")

    # Verify caching
    import time
    t0 = time.time()
    _ = officer.analyze_fairness_report(report)
    elapsed = (time.time() - t0) * 1000
    print(f"Cache hit latency: {elapsed:.1f} ms")


if __name__ == "__main__":
    main()
