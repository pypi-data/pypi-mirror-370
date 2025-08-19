import subprocess
from pathlib import Path


def test_dry_run(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "python" / "ramp_export_mapper.py"

    # Create a minimal sample CSV in a temp dir (don’t rely on repo files)
    sample = tmp_path / "sample.csv"
    sample.write_text(
        "Date,Amount,Merchant,Cardholder\n2025-01-05,12.34,Coffee Spot,Jane Analyst\n",
        encoding="utf-8",
    )
    outp = tmp_path / "dry_run_out.csv"

    res = subprocess.run(
        ["python", str(script), str(sample), str(outp), "--dry-run"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, res.stdout + res.stderr
    # basic sanity check on output
    assert "Dry run: validation succeeded." in res.stdout
    assert "rows:" in res.stdout
    assert "sample[1]:" in res.stdout
