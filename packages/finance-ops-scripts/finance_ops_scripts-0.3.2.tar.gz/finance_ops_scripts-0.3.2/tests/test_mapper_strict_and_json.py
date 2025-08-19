import csv
import json
from pathlib import Path

import pytest

from scripts.python.ramp_export_mapper import Options, map_columns


def _read_headers(p: Path) -> list[str]:
    with p.open("r", encoding="utf-8", newline="") as f:
        return next(csv.reader(f))


def test_map_json_override(tmp_path: Path) -> None:
    """
    Covers: JSON override path (load_mapping + custom header matching).
    """
    # Input with totally different source headers than defaults
    inp = tmp_path / "custom.csv"
    inp.write_text(
        "When,Cost,Vndr,Emp\n2025-02-01,12.34,Coffee Spot,Jane\n",
        encoding="utf-8",
    )

    # JSON mapping: map these custom headers to internal targets
    mapping = {
        "When": "txn_date",
        "Cost": "amount",
        "Vndr": "vendor",
        "Emp": "employee",
    }
    map_json = tmp_path / "mapping.json"
    map_json.write_text(json.dumps(mapping), encoding="utf-8")

    outp = tmp_path / "out.csv"
    opts = Options(input_file=inp, output_file=outp, map_json=map_json, strict=True)
    map_columns(opts)

    # Validate headers + a couple normalized fields
    headers = _read_headers(outp)
    assert headers == ["txn_date", "amount", "vendor", "employee"]
    lines = outp.read_text(encoding="utf-8").splitlines()
    assert lines[1].startswith("2025-02-01,12.34,Coffee Spot,")


def test_strict_missing_required_header_fails(tmp_path: Path) -> None:
    """
    Covers: strict mode branch that exits on missing source headers.
    (Merchant is intentionally omitted.)
    """
    inp = tmp_path / "in.csv"
    inp.write_text(
        "Date,Amount,Cardholder\n2025-01-05,1.00,Y\n",
        encoding="utf-8",
    )
    outp = tmp_path / "out.csv"

    opts = Options(input_file=inp, output_file=outp, map_json=None, strict=True)
    with pytest.raises(SystemExit) as e:
        map_columns(opts)
    assert e.value.code == 2  # our strict failure exit code


def test_strict_amounts_invalid_fails(tmp_path: Path) -> None:
    """
    Covers: strict-amounts branch that fails when amount can't be parsed.
    """
    inp = tmp_path / "in.csv"
    inp.write_text(
        "Date,Amount,Merchant,Cardholder\n2025-01-05,abc,Coffee,Y\n",  # invalid amount
        encoding="utf-8",
    )
    outp = tmp_path / "out.csv"

    opts = Options(
        input_file=inp,
        output_file=outp,
        map_json=None,
        strict=False,
        strict_amounts=True,
    )
    with pytest.raises(SystemExit) as e:
        map_columns(opts)
    assert e.value.code == 2
