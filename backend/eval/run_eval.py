"""
backend/eval/run_eval.py
────────────────
Evaluation script for the Legixo Q&A API.

Calls POST /ask for every test case in backend/eval/test_cases.json.
Checks:
  - In-corpus: expected facts appear in the answer (substring match)
  - In-corpus: at least one expected source file appears in citations
  - Out-of-corpus: grounded=False OR answer contains refusal phrasing

Results are printed to stdout and saved to backend/eval/results.md.

Usage (server must be running):
    python backend/eval/run_eval.py [--host http://localhost:8000]
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Force UTF-8 output on Windows so emoji in results.md don't crash the terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    import requests
except ImportError:
    print("Please install requests: pip install requests")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
EVAL_DIR = Path(__file__).parent
TEST_CASES_FILE = EVAL_DIR / "test_cases.json"
RESULTS_FILE = EVAL_DIR / "results.md"
REFUSAL_PHRASES = [
    "cannot find",
    "not found",
    "do not appear",
    "does not appear",
    "cannot answer",
    "not stated",
    "no information",
    "not in the documents",
    "unable to find",
    "not available",
]


# ── Evaluation helpers ─────────────────────────────────────────────────────────

def facts_present(answer: str, expected_facts: List[str]) -> tuple[bool, List[str]]:
    """Return (all_present, missing_facts). Case-insensitive substring match."""
    answer_lower = answer.lower()
    missing = [f for f in expected_facts if f.lower() not in answer_lower]
    return len(missing) == 0, missing


def citation_matches(citations: List[Dict], expected_files: List[str]) -> bool:
    """Return True if at least one expected source file appears in citations."""
    cited = {c.get("source_file", "") for c in citations}
    return any(f in cited for f in expected_files)


def is_refusal(answer: str, grounded: bool) -> bool:
    """Return True if the response is an honest refusal."""
    if not grounded:
        return True
    answer_lower = answer.lower()
    return any(phrase in answer_lower for phrase in REFUSAL_PHRASES)


# ── Runner ────────────────────────────────────────────────────────────────────

def run_eval(host: str) -> None:
    test_cases = json.loads(TEST_CASES_FILE.read_text(encoding="utf-8"))
    url = f"{host.rstrip('/')}/ask"

    results = []
    passed = 0
    failed = 0
    errors = 0

    print(f"\n{'='*60}")
    print(f"  Legixo Q&A Eval  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Endpoint: {url}")
    print(f"  Cases: {len(test_cases)}")
    print(f"{'='*60}\n")

    for case in test_cases:
        case_id = case["id"]
        question = case["question"]
        case_type = case["type"]

        print(f"[{case_id}] {question[:70]}...")

        try:
            resp = requests.post(url, json={"question": question}, timeout=60)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            print(f"  [ERROR] {exc}\n")
            errors += 1
            results.append({**case, "status": "ERROR", "error": str(exc)})
            continue

        answer = data.get("answer", "")
        citations = data.get("citations", [])
        grounded = data.get("grounded", False)
        trace = data.get("trace", [])
        cited_files = [c.get("source_file", "") for c in citations]

        if case_type == "in_corpus":
            expected_facts = case.get("expected_facts", [])
            expected_files = case.get("expected_source_files", [])

            facts_ok, missing = facts_present(answer, expected_facts)
            cite_ok = citation_matches(citations, expected_files)
            status = "PASS" if (facts_ok and cite_ok) else "FAIL"

            if status == "PASS":
                passed += 1
                print(f"  [PASS]  (trace: {' -> '.join(trace)})")
            else:
                failed += 1
                print(f"  [FAIL]")
                if not facts_ok:
                    print(f"     Missing facts: {missing}")
                if not cite_ok:
                    print(f"     Expected citations: {expected_files}, got: {cited_files}")

            results.append({
                **case,
                "status": status,
                "cited_files": cited_files,
                "answer_preview": answer[:200],
                "trace": trace,
                "missing_facts": missing if not facts_ok else [],
            })

        else:  # out_of_corpus
            refused = is_refusal(answer, grounded)
            status = "PASS" if refused else "FAIL"

            if status == "PASS":
                passed += 1
                print(f"  [PASS] correctly refused (grounded={grounded})")
            else:
                failed += 1
                print(f"  [FAIL] should have refused but answered (grounded={grounded})")
                print(f"     Answer: {answer[:150]}")

            results.append({
                **case,
                "status": status,
                "grounded": grounded,
                "cited_files": cited_files,
                "answer_preview": answer[:200],
                "trace": trace,
            })

        print()
        time.sleep(0.5)  # gentle rate limiting

    # ── Summary ───────────────────────────────────────────────────────────────
    total = passed + failed + errors
    print(f"{'='*60}")
    print(f"  Results: {passed}/{total} passed | {failed} failed | {errors} errors")
    print(f"{'='*60}\n")

    _write_results_md(results, passed, failed, errors, url)
    print(f"Full results saved to: {RESULTS_FILE}")


def _write_results_md(results, passed, failed, errors, url):
    lines = [
        "# Eval Results",
        "",
        f"**Run date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"**Endpoint:** `{url}`  ",
        f"**Total:** {passed + failed + errors} | **Passed:** {passed} | **Failed:** {failed} | **Errors:** {errors}",
        "",
        "---",
        "",
        "## Case-by-case",
        "",
        "| ID | Type | Status | Notes |",
        "|----|------|--------|-------|",
    ]

    for r in results:
        status_icon = "✅" if r.get("status") == "PASS" else "❌"
        notes = ""
        if r.get("missing_facts"):
            notes += f"Missing: {r['missing_facts']}. "
        if r.get("cited_files"):
            notes += f"Cited: {r['cited_files']}."
        if r.get("error"):
            notes += f"Error: {r['error']}"
        lines.append(f"| {r['id']} | {r['type']} | {status_icon} {r.get('status', '?')} | {notes} |")

    lines += [
        "",
        "---",
        "",
        "## Full Answers",
        "",
    ]

    for r in results:
        lines.append(f"### [{r['id']}] {r['question']}")
        lines.append(f"**Status:** {r.get('status')}  ")
        lines.append(f"**Answer preview:** {r.get('answer_preview', '')}  ")
        lines.append(f"**Cited files:** {r.get('cited_files', [])}  ")
        lines.append(f"**Trace:** {r.get('trace', [])}  ")
        lines.append("")

    RESULTS_FILE.write_text("\n".join(lines), encoding="utf-8")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run eval against the Q&A API.")
    parser.add_argument("--host", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()
    run_eval(args.host)
