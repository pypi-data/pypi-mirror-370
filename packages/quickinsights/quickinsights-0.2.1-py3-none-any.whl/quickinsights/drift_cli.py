#!/usr/bin/env python3
"""
QuickInsights - Drift Radar CLI

Usage:
  python src/quickinsights/drift_cli.py --base path/to/base.csv --current path/to/current.csv \
      --segment-by region --out quickinsights_output/drift_report.json

Supports CSV or Parquet. Outputs a JSON report with columns, overall risk, and alerts.
"""

import argparse
import json
import os
import sys
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd  # noqa: E402
from .data_validation import drift_radar  # noqa: E402


def _read_table(path: str) -> pd.DataFrame:
    low = path.lower()
    if low.endswith(".parquet"):
        return pd.read_parquet(path)
    # default CSV
    return pd.read_csv(path)


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description="QuickInsights Drift Radar CLI")
    parser.add_argument("--base", required=True, help="Path to baseline CSV/Parquet")
    parser.add_argument("--current", required=True, help="Path to current CSV/Parquet")
    parser.add_argument("--segment-by", default=None, help="Optional column to segment by")
    parser.add_argument("--bins", type=int, default=10, help="Bins for numeric PSI")
    parser.add_argument("--topk", type=int, default=20, help="Top-K categories for PSI")
    parser.add_argument("--low-th", type=float, default=0.25, help="PSI threshold for medium risk")
    parser.add_argument("--high-th", type=float, default=0.5, help="PSI threshold for high risk")
    parser.add_argument("--out", required=True, help="Output JSON report path")

    args = parser.parse_args(argv)

    base_df = _read_table(args.base)
    curr_df = _read_table(args.current)

    report = drift_radar(
        base_df,
        curr_df,
        bins=args.bins,
        top_k_categories=args.topk,
        segment_by=args.segment_by,
        psi_thresholds=(args.low_th, args.high_th),
    )

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Saved drift report to: {args.out}")
    print(f"Overall risk: {report.get('overall_risk')}")
    print(f"Alerts: {len(report.get('alerts', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


