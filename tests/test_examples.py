"""Run every example script under ``examples/`` as a smoke test.

Each script is executed top-to-bottom (as Sphinx-Gallery does). A test fails
if the script raises, or if it logs anything at ``WARNING`` level or above (a
script demonstrating "normal" library usage should not need to warn).

``plt.show()`` calls are neutralized (patched to a no-op) so that scripts
don't block waiting for a GUI window during test collection.

"""

import importlib.util
import logging
from pathlib import Path
from unittest.mock import patch

import matplotlib
import pytest

matplotlib.use("Agg")

EXAMPLES_DIR = Path(__file__).parents[1] / "examples"


def _example_scripts() -> list[Path]:
    """List every example script, sorted for stable, readable test output."""
    if not EXAMPLES_DIR.is_dir():
        return []
    return sorted(EXAMPLES_DIR.glob("*.py"))


@pytest.mark.example
@pytest.mark.parametrize(
    "script_path", _example_scripts(), ids=lambda p: p.stem
)
def test_example_runs_without_error_or_warning(
    script_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Check that the example script runs and logs nothing above WARNING."""
    module_name = f"examples.{script_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    assert spec is not None and spec.loader is not None, (
        f"Could not build an import spec for {script_path}."
    )
    module = importlib.util.module_from_spec(spec)

    with caplog.at_level(logging.WARNING), patch("matplotlib.pyplot.show"):
        spec.loader.exec_module(module)

    problematic_records = [
        record
        for record in caplog.records
        if record.levelno >= logging.WARNING
    ]
    messages = "\n".join(
        f"\t[{rec.levelname}] {rec.message}" for rec in problematic_records
    )
    assert not problematic_records, (
        f"{script_path} logged at WARNING level or above:\n{messages}"
    )
