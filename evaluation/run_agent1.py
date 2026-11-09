
import argparse
import json
import sys
import time
from pathlib import Path

# Ensure imports work when running this file directly.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.meeting_agent import extract_action_items
from evaluation.agent1_cases import CASES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--case",
        required=True,
        help="Case ID, for example M01"
    )
    args = parser.parse_args()

    case = next(
        (c for c in CASES if c["id"] == args.case),
        None
    )

    if case is None:
        raise ValueError(f"Unknown case: {args.case}")

    print(f"Running: {case['id']}")
    print(f"Category: {case['category']}")
    print(f"Expected items: {len(case['expected'])}")

    start = time.perf_counter()

    try:
        analysis = extract_action_items(case["notes"])

        result = {
            "case_id": case["id"],
            "category": case["category"],
            "latency_seconds": round(
                time.perf_counter() - start, 3
            ),
            "expected": [
                {
                    "title": title,
                    "assignee": assignee,
                    "deadline": deadline
                }
                for title, assignee, deadline
                in case["expected"]
            ],
            "predicted": [
                {
                    "title": item.title,
                    "assignee": item.assignee,
                    "deadline": (
                        item.deadline.isoformat()
                        if item.deadline else None
                    ),
                    "source_excerpt": item.source_excerpt
                }
                for item in analysis.action_items
            ],
            "error": None
        }

    except Exception as exc:
        result = {
            "case_id": case["id"],
            "category": case["category"],
            "latency_seconds": round(
                time.perf_counter() - start, 3
            ),
            "expected": [
                {
                    "title": title,
                    "assignee": assignee,
                    "deadline": deadline
                }
                for title, assignee, deadline
                in case["expected"]
            ],
            "predicted": [],
            "error": str(exc)
        }

    output_dir = ROOT / "evaluation" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    path = output_dir / f"{case['id']}.json"
    path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"Saved result: {path}")


if __name__ == "__main__":
    main()
