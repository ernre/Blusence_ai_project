"""Human evaluation export utilities."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class HumanEvalItem:
    """A blind A/B human-eval row."""

    sample_id: str
    candidate_a: str
    candidate_b: str
    garment_category: str
    brand_id: str | None = None


def export_human_eval(items: list[HumanEvalItem], output_dir: Path) -> tuple[Path, Path]:
    """Export human-eval rows as CSV and JSON."""

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "human_eval.csv"
    json_path = output_dir / "human_eval.json"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["sample_id", "candidate_a", "candidate_b", "garment_category", "brand_id"],
        )
        writer.writeheader()
        for item in items:
            writer.writerow(asdict(item))
    json_path.write_text(json.dumps([asdict(item) for item in items], indent=2), encoding="utf-8")
    return csv_path, json_path
