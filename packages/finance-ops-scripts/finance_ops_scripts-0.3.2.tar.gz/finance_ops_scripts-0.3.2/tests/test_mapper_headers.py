import csv
from pathlib import Path

from scripts.python.ramp_export_mapper import Options, map_columns


def test_expected_headers_present(tmp_path: Path) -> None:
    inp = tmp_path / "in.csv"
    inp.write_text(
        "Date,Amount,Merchant,Cardholder\n2025-01-05,1.00,X,Y\n",
        encoding="utf-8",
    )
    outp = tmp_path / "out.csv"

    opts = Options(input_file=inp, output_file=outp, map_json=None, strict=False)
    map_columns(opts)

    with outp.open("r", encoding="utf-8", newline="") as f:
        headers = next(csv.reader(f))
    assert headers == ["txn_date", "amount", "vendor", "employee"]


def test_headers_case_insensitive(tmp_path: Path) -> None:
    # intentionally mixed case + spaces
    inp = tmp_path / "in.csv"
    inp.write_text(
        " date ,AMOUNT,merchant , CARDHOLDER\n2025-01-05,1.00,X,Y\n",
        encoding="utf-8",
    )
    outp = tmp_path / "out.csv"

    opts = Options(input_file=inp, output_file=outp, map_json=None, strict=True)
    map_columns(opts)

    # header line
    first_line = outp.read_text(encoding="utf-8").splitlines()[0]
    assert first_line == "txn_date,amount,vendor,employee"


def test_missing_source_lenient(tmp_path: Path) -> None:
    # omit Merchant on purpose
    inp = tmp_path / "in.csv"
    inp.write_text(
        "Date,Amount,Cardholder\n2025-01-05,1.00,Y\n",
        encoding="utf-8",
    )
    outp = tmp_path / "out.csv"

    # lenient (default) – should succeed, vendor column empty
    opts = Options(input_file=inp, output_file=outp, map_json=None, strict=False)
    map_columns(opts)

    lines = outp.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "txn_date,amount,vendor,employee"
    assert lines[1].endswith(",Y")  # vendor empty, employee=Y
