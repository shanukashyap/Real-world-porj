"""Resolved paths to bundled data (corpus, IOC samples)."""

from pathlib import Path


def project_root() -> Path:
    # app/data_paths.py -> project root is parent of `app`
    return Path(__file__).resolve().parents[1]
