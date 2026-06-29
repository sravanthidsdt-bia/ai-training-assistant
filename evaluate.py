"""Evaluate routing and retrieval against the labeled evaluation set."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.assistant import TrainingAssistant
from src.config import CHROMA_DIR


def run_evaluation(eval_path: Path, output_path: Path | None = None) -> None:
    if not CHROMA_DIR.exists():
        print("Error: Run 'python -m src.ingest' first.")
        sys.exit(1)

    assistant = TrainingAssistant()
    rows = list(csv.DictReader(eval_path.open(encoding="utf-8")))

    correct_route = 0
    results = []

    for row in rows:
        qid = row["question_id"]
        question = row["question"]
        expected = row["expected_route"]

        result = assistant.ask(question)
        actual = result["route"]
        match = actual == expected
        if match:
            correct_route += 1

        results.append(
            {
                "question_id": qid,
                "question": question,
                "expected_route": expected,
                "actual_route": actual,
                "route_match": match,
                "routing_method": result["routing_method"],
                "num_sources": len(result.get("sources", [])),
                "answer_preview": result["answer"][:120],
            }
        )
        status = "✓" if match else "✗"
        print(f"{status} {qid}: expected={expected}, got={actual}")

    accuracy = correct_route / len(rows) * 100
    print(f"\nRouting accuracy: {correct_route}/{len(rows)} ({accuracy:.1f}%)")

    if output_path:
        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"Results saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate the training assistant")
    parser.add_argument(
        "--eval",
        default="evaluation_set.csv",
        help="Path to evaluation CSV",
    )
    parser.add_argument(
        "--output",
        default="evaluation_results.csv",
        help="Path to save results",
    )
    args = parser.parse_args()
    run_evaluation(Path(args.eval), Path(args.output))
