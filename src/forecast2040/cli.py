"""Command line entry point.

    forecast2040 list
    forecast2040 fetch --all
    forecast2040 fetch --source worldbank_deu_gdp --source stooq_vw
    forecast2040 manifest

The CLI is deliberately thin: all logic lives in the modules, so that every
step can be imported from a notebook and tested without a terminal.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from .config import ConfigError, load_settings, select
from .manifest import read_manifest
from .sources.registry import fetch_many


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forecast2040",
        description="Data layer for the 2040 study",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="list registered sources")

    fetch = sub.add_parser("fetch", help="download sources and record provenance")
    fetch.add_argument("--source", action="append", default=[], help="source id, repeatable")
    fetch.add_argument("--all", action="store_true", help="fetch every registered source")

    sub.add_parser("manifest", help="show the provenance manifest")

    sub.add_parser("panel", help="assemble the panels and the codebook from raw data")

    model = sub.add_parser("model", help="backtest the benchmark models and project to 2040")
    model.add_argument("--series", default="vw_group_china_deliveries", help="panel column")
    model.add_argument("--to-year", type=int, default=2040, help="last projected year")
    model.add_argument("--horizon", type=int, default=5, help="maximum backtest horizon")
    return parser


def _cmd_list() -> int:
    settings = load_settings()
    for source in settings.sources:
        flag = "on " if source.enabled else "off"
        print(f"{flag} {source.id:24s} {source.kind:10s} {source.cadence:8s} {source.label}")
    print(f"\n{len(settings.sources)} sources, registry {settings.raw_dir.parent.name}/../config")
    return 0


def _cmd_fetch(ids: Sequence[str], all_sources: bool) -> int:
    settings = load_settings()
    chosen = select(settings, None) if all_sources else select(settings, ids)
    if not chosen:
        print("nothing selected, use --all or --source", file=sys.stderr)
        return 2

    results = fetch_many(settings, chosen)
    failures = 0
    for source, path, error in results:
        if path is None:
            failures += 1
            print(f"FAIL {source.id:24s} {error}")
        else:
            print(f"ok   {source.id:24s} {path.name}")
    print(f"\n{len(results) - failures} of {len(results)} fetched")
    return 1 if failures else 0


def _cmd_manifest() -> int:
    settings = load_settings()
    records = read_manifest(settings.manifest_path)
    if not records:
        print("manifest is empty")
        return 0
    print(f"{'fetched_at_utc':22s} {'source_id':24s} {'rows':>7s} {'sha256':10s}")
    for record in records:
        print(
            f"{record.fetched_at_utc:22s} {record.source_id:24s} "
            f"{record.rows:>7d} {record.sha256[:10]}"
        )
    return 0


def _cmd_panel() -> int:
    from .panel import PanelError, write_panels

    settings = load_settings()
    try:
        written = write_panels(settings)
    except PanelError as exc:
        print(f"panel error: {exc}", file=sys.stderr)
        return 1
    for path in written:
        print(f"wrote {path}")
    return 0


def _cmd_model(series: str, to_year: int, horizon: int) -> int:
    from .models import ModelError, format_register_line, run_benchmark

    settings = load_settings()
    panel = settings.raw_dir.parent / "panel" / "panel_annual.csv"
    try:
        written = run_benchmark(
            panel,
            series,
            settings.raw_dir.parent / "model",
            last_year=to_year,
            horizons=tuple(range(1, horizon + 1)),
        )
    except ModelError as exc:
        print(f"model error: {exc}", file=sys.stderr)
        return 1
    for path in written.values():
        print(f"wrote {path}")
    print(format_register_line(written["register"]))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "list":
            return _cmd_list()
        if args.command == "fetch":
            return _cmd_fetch(args.source, args.all)
        if args.command == "manifest":
            return _cmd_manifest()
        if args.command == "panel":
            return _cmd_panel()
        if args.command == "model":
            return _cmd_model(args.series, args.to_year, args.horizon)
    except ConfigError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
