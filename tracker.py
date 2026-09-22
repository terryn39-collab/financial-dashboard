"""Financial growth tracker.

Calculates compound interest and simulates asset growth over time.
Outputs simulation results as JSON Lines for easy downstream processing.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class GrowthPoint:
    year: int
    value: float


def compound_interest(principal: float, annual_rate: float, years: int, compounds_per_year: int = 12) -> float:
    if principal < 0:
        raise ValueError("principal must be non-negative")
    if annual_rate <= -1:
        raise ValueError("annual_rate must be greater than -1")
    if years < 0:
        raise ValueError("years must be non-negative")
    if compounds_per_year <= 0:
        raise ValueError("compounds_per_year must be positive")
    return principal * (1 + annual_rate / compounds_per_year) ** (compounds_per_year * years)


def simulate_growth(initial_value: float, annual_rate: float, years: int) -> list[GrowthPoint]:
    if years < 0:
        raise ValueError("years must be non-negative")
    return [
        GrowthPoint(year=year, value=round(compound_interest(initial_value, annual_rate, year), 2))
        for year in range(years + 1)
    ]


def log_results(points: list[GrowthPoint], output_file: Path, *, principal: float, annual_rate: float) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "principal": principal,
        "annual_rate": annual_rate,
        "results": [asdict(point) for point in points],
    }
    with output_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate compound investment growth.")
    parser.add_argument("--principal", type=float, default=10_000.0)
    parser.add_argument("--rate", type=float, default=0.07, help="Annual rate as decimal, e.g. 0.07")
    parser.add_argument("--years", type=int, default=10)
    parser.add_argument("--output", type=Path, default=Path("growth_log.jsonl"))
    args = parser.parse_args()

    points = simulate_growth(args.principal, args.rate, args.years)
    log_results(points, args.output, principal=args.principal, annual_rate=args.rate)
    print(f"Final value after {args.years} years: ${points[-1].value:,.2f}")
    print(f"Logged {len(points)} data points to {args.output}")


if __name__ == "__main__":
    main()
