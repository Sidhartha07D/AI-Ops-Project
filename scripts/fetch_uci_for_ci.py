"""Restore the pinned public source CSV for an isolated CI checkout.

CI has no access to the VM-only DVC remote, so this verifies the original
archive and CSV hashes before running the same DVC stages.
"""

from hashlib import sha256
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
URL = "https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip"
ZIP_SHA256 = "f601f14294bcf190f9d720676b7f0aea46a26cde9ab8ebc7b4f8174d9d26b252"
CSV_SHA256 = "dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e"


def main() -> None:
    with urlopen(URL, timeout=60) as response:
        archive = response.read()
    assert sha256(archive).hexdigest() == ZIP_SHA256, "Source ZIP hash mismatch"
    with ZipFile(BytesIO(archive)) as bundle:
        names = [
            name for name in bundle.namelist() if name.lower().endswith("ai4i2020.csv")
        ]
        assert len(names) == 1, f"Expected one AI4I CSV, found {names}"
        csv = bundle.read(names[0])
    assert sha256(csv).hexdigest() == CSV_SHA256, "Source CSV hash mismatch"
    output = ROOT / "data/raw/ai4i2020.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(csv)
    print(f"Verified UCI source: {len(csv)} bytes, SHA-256 {CSV_SHA256}")


if __name__ == "__main__":
    main()
