"""Paths relative to the application, independent of the launch directory."""
from pathlib import Path
import sys

BASE_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent


def app_path(*parts):
    return BASE_DIR.joinpath(*parts)
