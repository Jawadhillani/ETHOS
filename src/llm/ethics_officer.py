"""
EthicsOfficer: LLM-powered fairness analyst for ETHOS.

Wraps the Anthropic API to turn raw fairness JSON into:
  1. Plain-English bias analysis (for the demo + slides)
  2. Counterfactual failure explanation (why a specific match failed)
  3. EU AI Act compliance executive summary (feeds the Week 6 PDF)

Caching: responses are memoised in-process by MD5 of the serialised input,
so repeated calls during a demo never hit the API twice for the same data.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import anthropic
from dotenv import load_dotenv

# Load .env from project root (two levels above this file: src/llm/ → project/)
_ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

MODEL = "claude-sonnet-4-5"
MAX_TOKENS = 2048

_SYSTEM_PROMPT = """You are the Ethics Officer of ETHOS, an EU AI Act compliance \
auditing system for facial biometric recognition technology. Your role is to:

- Translate raw statistical fairness metrics into clear, professional language
- Identify compliance violations and their real-world implications
- Explain bias findings to both technical and non-technical audiences
- Reference relevant EU AI Act provisions (Article 10 data governance, \
Article 13 transparency, Annex III high-risk systems)

Be precise, factual, and direct. Use concrete numbers. Avoid hedging language. \
When the data shows a compliance failure, name it clearly."""


def _cache_key(data: Any) -> str:
    serialised = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(serialised.encode()).hexdigest()


class EthicsOfficer:
    """
    LLM-powered fairness analysis. All public methods return plain strings.

    Usage:
        officer = EthicsOfficer()
        analysis = officer.analyze_fairness_report(report_dict)
        print(analysis)
    """

    def __init__(self, api_key: str = None):
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY not found. "
                "Create a .env file at the project root (see .env.example)."
            )
        self._client = anthropic.Anthropic(api_key=key)
        self._cache: dict[str, str] = {}

    # ── Core API call ─────────────────────────────────────────────────────────

    def _call(self, user_message: str, cache_key: str) -> str:
        if cache_key in self._cache:
            return self._cache[cache_key]

        response = self._client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        text = response.content[0].text
        self._cache[cache_key] = text
        return text

    # ── Public methods ────────────────────────────────────────────────────────

    def analyze_fairness_report(self, report: dict) -> str:
        """
        Plain-English bias analysis from the full fairness audit JSON.

        Covers:
          - What the audit found (compliance pass/fail per demographic axis)
          - The headline numbers (FMRD, DI, worst-to-best FAR gap)
          - Real-world implications of the failures
          - Suggested mitigations
        """
        prompt = f"""Here is the full ETHOS fairness audit report for a facial \
biometric recognition system (ArcFace buffalo_l, evaluated on LFW + FairFace datasets):

{json.dumps(report, indent=2, default=str)}

Write a comprehensive plain-English analysis covering:

1. **Executive summary** (3-4 sentences): overall verdict, how many axes passed/failed.

2. **Race bias findings**: explain the FMRD number, name the best and worst groups, \
quantify the gap, and explain what this means in a real deployment (airport, phone \
unlock, border control).

3. **Age bias findings**: explain the infant/elderly FAR spike. Why does ArcFace \
struggle with these groups? What are the deployment implications?

4. **Gender findings**: report the result honestly, including the slight female disadvantage.

5. **EU AI Act compliance verdict**: which provisions are implicated? Is this system \
deployable today under EU law as a high-risk biometric system?

6. **Recommended mitigations**: 3 concrete steps the development team should take \
before deployment.

Be specific with numbers throughout. Write for a technically literate audience \
(engineers + regulators), not the general public."""

        return self._call(prompt, _cache_key({"method": "analyze", "report": report}))

    def counterfactual_failure(self, failure_data: dict) -> str:
        """
        Explains why a specific verification attempt failed and what threshold
        would have produced the correct decision.

        failure_data keys:
          - query_id: identifier for the probe image
          - matched_id: identifier of the false match (or rejected genuine)
          - similarity_score: float
          - current_threshold: float
          - demographic_group: str (e.g. "East Asian")
          - failure_type: "false_accept" | "false_reject"
          - group_far: float (FAR for this demographic at current threshold)
        """
        prompt = f"""A facial biometric verification system produced the following \
failure. Analyse it as a forensic ethics officer:

{json.dumps(failure_data, indent=2, default=str)}

Provide:

1. **What happened**: describe the failure in one clear sentence using the numbers.

2. **Why it happened**: explain the demographic context. How does this group's FAR \
compare to the system average? Is this an outlier or typical for this group?

3. **Threshold analysis**: at what threshold would this specific failure have been \
avoided? What would be the trade-off (increased FRR)?

4. **Fairness implication**: is this failure consistent with known bias in ArcFace \
training data? Rate the severity: LOW / MEDIUM / HIGH.

5. **Recommended action**: one concrete next step for the development team."""

        return self._call(prompt, _cache_key({"method": "counterfactual", **failure_data}))

    def generate_compliance_summary(self, report: dict) -> str:
        """
        EU AI Act executive summary suitable for inclusion in a PDF compliance report.

        Structured as:
          - System identification
          - Audit methodology
          - Findings per demographic axis (table format)
          - Compliance verdict with legal citations
          - Required actions before deployment
        """
        prompt = f"""Generate a formal EU AI Act compliance summary for inclusion in \
an official audit report. Use professional regulatory language throughout.

Audit data:
{json.dumps(report, indent=2, default=str)}

Structure the output exactly as follows:

## SYSTEM IDENTIFICATION
[System name, model, evaluation datasets, audit date from metadata]

## AUDIT METHODOLOGY
[2-3 sentences: datasets used, metric definitions (FAR, FMRD, DI), threshold source]

## FINDINGS SUMMARY
[Present findings as a structured table: Demographic Axis | FMRD | DI | Verdict]
[Then 2-3 sentences per axis explaining the key finding]

## COMPLIANCE VERDICT
[Cite specific EU AI Act articles. State clearly: COMPLIANT / NON-COMPLIANT / \
CONDITIONALLY COMPLIANT for each axis and overall.]

## REQUIRED ACTIONS PRIOR TO DEPLOYMENT
[Numbered list of mandatory remediation steps under EU AI Act Article 9 \
(risk management) and Article 10 (data governance)]

## LIMITATIONS OF THIS AUDIT
[Note the LFW/FairFace hybrid approach, the FNMRD gap, the infant sample size]

Keep the tone formal and precise. This document may be reviewed by regulators."""

        return self._call(
            prompt,
            _cache_key({"method": "compliance_summary", "report": report}),
        )
