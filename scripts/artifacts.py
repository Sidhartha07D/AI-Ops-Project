"""Content identity and trusted local MLflow model loading."""

from hashlib import sha256
from pathlib import Path


def tree_digest(path):
    """Include relative names and bytes so renamed or missing files change identity."""
    root = Path(path)
    digest = sha256()
    for file in sorted(root.rglob("*")):
        if file.is_file():
            digest.update(str(file.relative_to(root)).encode() + b"\0")
            digest.update(file.read_bytes())
    return digest.hexdigest()


def load_model(path):
    import mlflow.pyfunc

    return mlflow.pyfunc.load_model(str(path))
