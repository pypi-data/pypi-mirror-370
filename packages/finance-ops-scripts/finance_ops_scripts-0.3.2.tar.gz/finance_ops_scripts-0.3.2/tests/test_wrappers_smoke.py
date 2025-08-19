import platform
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "ramp_raw.csv"
OUT = REPO / "output" / "ramp_mapped.csv"


def run(cmd, **kwargs):
    """Run a subprocess with consistent defaults; allow overrides via kwargs."""
    return subprocess.run(
        cmd,
        cwd=kwargs.pop("cwd", REPO),
        text=kwargs.pop("text", True),
        capture_output=kwargs.pop("capture_output", True),
        **kwargs,
    )


@pytest.mark.skipif(platform.system() == "Windows", reason="bash test runs in non-Windows CI")
def test_bash_wrapper_dry_run():
    OUT.unlink(missing_ok=True)
    # no explicit cwd: our helper defaults to REPO
    res = run(["bash", "-lc", "bash tools/ramp.sh --dry-run"])
    assert res.returncode == 0, res.stdout + res.stderr
    assert not OUT.exists()  # dry-run shouldn't create the file


@pytest.mark.skipif(platform.system() != "Windows", reason="PowerShell test runs on Windows")
def test_powershell_wrapper_dry_run():
    OUT.unlink(missing_ok=True)
    res = run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "./tools/ramp.ps1",
            "-Raw",
            str(DATA),
            "-Out",
            str(OUT),
            "-DryRun",
        ]
    )
    assert res.returncode == 0, res.stdout + res.stderr
    assert not OUT.exists()
