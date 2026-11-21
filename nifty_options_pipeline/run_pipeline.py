#!/usr/bin/env python3
"""CLI for the NIFTY options history pipeline.

  python run_pipeline.py download --what fo        # F&O bhavcopies (resumable)
  python run_pipeline.py download --what indices   # NIFTY 50 / India VIX daily closes
  python run_pipeline.py build                     # raw -> standard-schema Parquet by year
  python run_pipeline.py validate                  # write reports/validation_report.md
  python run_pipeline.py all                       # everything, sequentially
"""
from __future__ import annotations

import argparse
import datetime as dt
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline import config  # noqa: E402


def _setup_logging(name: str) -> None:
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    logging.basicConfig(level=logging.INFO, format=fmt,
                        handlers=[logging.StreamHandler(sys.stdout),
                                  logging.FileHandler(config.LOG_DIR / f"{name}.log")])


def _date(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("download", help="download raw files (cached, resumable)")
    d.add_argument("--what", choices=["fo", "indices", "all"], default="all")
    d.add_argument("--start", type=_date, default=config.START_DATE)
    d.add_argument("--end", type=_date, default=dt.date.today())
    d.add_argument("--delay", type=float, default=1.0, help="seconds between requests")
    d.add_argument("--recheck-404", action="store_true", help="re-request dates previously recorded as 404")

    b = sub.add_parser("build", help="parse raw files into standard-schema Parquet")
    b.add_argument("--years", type=int, nargs="*", help="restrict to these years (default: all)")
    b.add_argument("--sample-month", default="2024-07", help="YYYY-MM written as a CSV sample")

    v = sub.add_parser("validate", help="write the markdown validation report")
    v.add_argument("--seed", type=int, default=42, help="seed for the random spot-check dates")

    a = sub.add_parser("all", help="download, build, validate")
    a.add_argument("--delay", type=float, default=1.0)
    a.add_argument("--seed", type=int, default=42)

    args = p.parse_args(argv)
    _setup_logging(args.cmd if args.cmd != "download" else f"download_{args.what}")

    if args.cmd == "download":
        from pipeline.download import download_range
        whats = ["fo", "indices"] if args.what == "all" else [args.what]
        for w in whats:
            download_range(w, args.start, args.end, delay=args.delay, recheck_404=args.recheck_404)
    elif args.cmd == "build":
        from pipeline.build import build
        build(years=args.years, sample_month=args.sample_month)
    elif args.cmd == "validate":
        from pipeline.validate import write_report
        write_report(seed=args.seed)
    elif args.cmd == "all":
        from pipeline.build import build
        from pipeline.download import download_range
        from pipeline.validate import write_report
        for w in ["fo", "indices"]:
            download_range(w, config.START_DATE, dt.date.today(), delay=args.delay)
        build()
        write_report(seed=args.seed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
