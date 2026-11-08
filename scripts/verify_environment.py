"""Check the declared version snapshot against the current interpreter."""
import importlib.metadata
import platform
from pathlib import Path
import yaml

root = Path(__file__).resolve().parents[1]
snapshot = yaml.safe_load((root/"environment.snapshot.yml").read_text())
checked = 0
for item in snapshot["dependencies"]:
    if isinstance(item, str) and item.startswith("python="):
        assert platform.python_version() == item.split("=",1)[1], "Python version mismatch"
    if isinstance(item, dict):
        for requirement in item.get("pip", []):
            name, expected = requirement.split("==", 1)
            actual = importlib.metadata.version(name)
            assert actual == expected, f"{name}: expected {expected}, found {actual}"
            checked += 1
print(f"Environment parity: PASS ({checked} declared pip versions; Python {platform.python_version()})")
