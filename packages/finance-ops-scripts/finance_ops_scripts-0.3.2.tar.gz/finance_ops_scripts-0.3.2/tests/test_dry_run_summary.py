from pathlib import Path

from scripts.python.ramp_export_mapper import Options, map_columns

CSV = """Date,Amount,Merchant,Cardholder
2025-01-05,12.34,Coffee Spot,Jane Analyst
not-a-date,99.99,Store,John
2025-01-06,abc,Vendor,Alex
"""


def test_dry_run_reports_counts(tmp_path: Path):
    raw = tmp_path / "raw.csv"
    out = tmp_path / "mapped.csv"
    raw.write_text(CSV, encoding="utf-8")

    opts = Options(input_file=raw, output_file=out, dry_run=True)
    # Capture stdout
    import io
    import sys

    buf, old = io.StringIO(), sys.stdout
    sys.stdout = buf
    try:
        map_columns(opts)
    finally:
        sys.stdout = old
    out_s = buf.getvalue()

    assert "rows: 3" in out_s
    assert "invalid_dates: 1" in out_s
    assert "invalid_amounts: 1" in out_s
    assert "sample[1]:" in out_s
