"""Run collected unit cases and save actual counts, including skipped/errors."""

import json
import sys
import unittest
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    suite = unittest.defaultTestLoader.discover(
        str(root / "scripts"), pattern="*tests.py"
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        "executed": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "passed": result.testsRun
        - len(result.failures)
        - len(result.errors)
        - len(result.skipped),
    }
    (root / "reports/unit_test_results.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
