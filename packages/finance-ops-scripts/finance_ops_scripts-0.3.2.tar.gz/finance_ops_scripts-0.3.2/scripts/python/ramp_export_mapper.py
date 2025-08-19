"""
Ramp Export Mapper

This script maps data exported from Ramp into an internal schema for further processing.
It can run in normal mode (writing the mapped data to a file) or in dry-run mode
(printing to stdout).

Usage:
    python ramp_export_mapper.py <input_csv> <output_csv> [--dry-run]
"""

from __future__ import annotations

import csv
import io
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

__version__ = "0.1.2"

# Default External (Ramp) -> Internal schema
DEFAULT_COLUMN_MAP: Dict[str, str] = {
    "Date": "txn_date",
    "Amount": "amount",
    "Merchant": "vendor",
    "Cardholder": "employee",
}


@dataclass(frozen=True)
class Options:
    input_file: Path
    output_file: Path
    map_json: Path | None = None
    strict: bool = False
    strict_amounts: bool = False
    dry_run: bool = False


def _normalize(s: str) -> str:
    """Lowercase + strip to make header matching robust to case/whitespace."""
    return s.strip().lower()


def _to_iso_date(s: str) -> str:
    """Parse common date formats and return YYYY-MM-DD; return '' if unparseable."""
    val = s.strip()
    if not val:
        return ""
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d-%b-%Y"):
        try:
            return datetime.strptime(val, fmt).date().isoformat()
        except ValueError:
            pass
    return ""


def _to_decimal_str(s: str) -> str:
    """Normalize numeric amounts: strip $, commas; return '0.00' for blanks; '' if bad."""
    val = s.strip().replace(",", "").replace("$", "")
    if val in ("", "-", "—"):
        val = "0"
    try:
        return f"{Decimal(val):.2f}"
    except (InvalidOperation, ValueError):
        return ""


def load_mapping(map_json: Path | None) -> Dict[str, str]:
    if map_json is None:
        return DEFAULT_COLUMN_MAP
    data = json.loads(map_json.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not all(
        isinstance(k, str) and isinstance(v, str) for k, v in data.items()
    ):
        raise ValueError("Mapping JSON must be an object of {source_header: target_header}.")
    # defensively ensure no duplicate targets
    targets = list(data.values())
    if len(set(targets)) != len(targets):
        raise ValueError("Duplicate target headers found in mapping.")
    return data


def validate_required_sources(
    required_sources: Iterable[str],
    available_headers: Iterable[str],
    strict: bool,
) -> list[str]:
    """Return list of missing required source columns (original names)."""
    avail_norm = {_normalize(h) for h in available_headers}
    missing: list[str] = []
    for src in required_sources:
        if _normalize(src) not in avail_norm:
            missing.append(src)
    if missing and strict:
        print("Missing required source columns: " + ", ".join(missing), file=sys.stderr)
        sys.exit(2)
    return missing


def _sniff_dialect(sample: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(sample)
    except csv.Error:
        return csv.excel


def _map_rows(
    reader: csv.DictReader,
    mapping: Dict[str, str],
    strict: bool,
    strict_amounts: bool,
) -> Tuple[List[str], List[Dict[str, str]]]:
    """Return (output_headers, list_of_output_rows_as_dicts)."""
    # Case/space-insensitive lookup for actual input header names
    norm_to_actual = {_normalize(h): h for h in (reader.fieldnames or [])}
    out_headers = list(mapping.values())
    out_rows: List[Dict[str, str]] = []

    for row in reader:
        out_row: Dict[str, str] = {}
        for src, dst in mapping.items():
            actual_src = norm_to_actual.get(_normalize(src))
            raw = "" if actual_src is None else row.get(actual_src, "")

            if dst == "txn_date":
                val = _to_iso_date(raw)
                if strict and not val:
                    print("Invalid date encountered in strict mode.", file=sys.stderr)
                    sys.exit(2)
                out_row[dst] = val
            elif dst == "amount":
                norm = _to_decimal_str(raw)
                if strict_amounts and norm == "":
                    print(
                        "Invalid amount encountered in strict-amounts mode.",
                        file=sys.stderr,
                    )
                    sys.exit(2)
                out_row[dst] = norm
            else:
                out_row[dst] = raw
        out_rows.append(out_row)

    return out_headers, out_rows


def map_columns(opts: Options) -> None:
    mapping = load_mapping(opts.map_json)

    with opts.input_file.open("r", newline="", encoding="utf-8-sig") as f_in:
        sample = f_in.read(4096)
        f_in.seek(0)
        dialect = _sniff_dialect(sample)
        reader = csv.DictReader(f_in, dialect=dialect)
        if reader.fieldnames is None:
            print("Input CSV has no header row.", file=sys.stderr)
            sys.exit(2)

        # Validate / note missing
        missing = validate_required_sources(mapping.keys(), reader.fieldnames, opts.strict)
        if missing and not opts.strict:
            print("Note: missing columns treated as empty (lenient mode): " + ", ".join(missing))

        out_headers, out_rows = _map_rows(
            reader,
            mapping=mapping,
            strict=opts.strict,
            strict_amounts=opts.strict_amounts,
        )

    # Simple quality counters for visibility
    invalid_dates = sum(1 for r in out_rows if "txn_date" in r and r["txn_date"] == "")
    invalid_amounts = sum(1 for r in out_rows if "amount" in r and r["amount"] == "")

    if opts.dry_run:
        print("Dry run: validation succeeded.")
        print(f"rows: {len(out_rows)}")
        print(f"invalid_dates: {invalid_dates} (strict would fail if --strict)")
        print(f"invalid_amounts: {invalid_amounts} (strict would fail if --strict-amounts)")
        print("mapping:")
        for src, dst in mapping.items():
            print(f"  {src} -> {dst}")

        # Build CSV-formatted preview lines using csv module for correctness
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=out_headers, lineterminator="\n")
        writer.writeheader()
        for r in out_rows[:3]:
            writer.writerow(r)
        preview = buf.getvalue().splitlines()[1:]  # drop header for preview lines
        for i, line in enumerate(preview, start=1):
            print(f"sample[{i}]: {line}")
        return

    # Write actual output
    opts.output_file.parent.mkdir(parents=True, exist_ok=True)
    with opts.output_file.open("w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=out_headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Wrote mapped data to {opts.output_file}")


def parse_args(argv: list[str]) -> Options:
    # Minimal, dependency-free arg parsing
    if len(argv) >= 2 and argv[1] in ("--version", "-V"):
        print(__version__)
        sys.exit(0)

    if len(argv) < 3:
        print(
            "Usage: python scripts/python/ramp_export_mapper.py INPUT.csv OUTPUT.csv "
            "[--map-json mapping.json] [--strict] [--strict-amounts] [--dry-run] [--version|-V]",
            file=sys.stderr,
        )
        sys.exit(1)

    input_file = Path(argv[1])
    output_file = Path(argv[2])

    map_json: Path | None = None
    strict = False
    strict_amounts = False
    dry_run = False

    i = 3
    while i < len(argv):
        arg = argv[i]
        if arg == "--map-json":
            if i + 1 >= len(argv):
                print("Missing value for --map-json", file=sys.stderr)
                sys.exit(1)
            map_json = Path(argv[i + 1])
            i += 2
            continue
        if arg == "--strict":
            strict = True
            i += 1
            continue
        if arg == "--strict-amounts":
            strict_amounts = True
            i += 1
            continue
        if arg == "--dry-run":
            dry_run = True
            i += 1
            continue
        print(f"Unknown option: {arg}", file=sys.stderr)
        sys.exit(1)

    if not input_file.exists():
        print(f"Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    # Only ensure output dir exists if we might write
    if not dry_run:
        output_file.parent.mkdir(parents=True, exist_ok=True)

    return Options(
        input_file=input_file,
        output_file=output_file,
        map_json=map_json,
        strict=strict,
        strict_amounts=strict_amounts,
        dry_run=dry_run,
    )


def main() -> None:
    """Console entry point."""
    map_columns(parse_args(sys.argv))


if __name__ == "__main__":
    main()
