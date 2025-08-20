# syntaxmatrix/project_root.py

import os
import inspect
from pathlib import Path
import syntaxmatrix


def scandir() -> Path:
    """
    Find the first stack frame outside of the syntaxmatrix package
    whose filename is a real .py file on disk, and return its parent dir.
    """
    framework_dir = Path(syntaxmatrix.__file__).resolve().parent

    for frame in inspect.stack():
        fname = frame.filename

        # 1) skip internal frames (<frozen ...>) or empty names
        if not fname or fname.startswith("<"):
            continue

        candidate = Path(fname)

        # 2) skip non-.py or non-existent paths
        if candidate.suffix != ".py" or not candidate.exists():
            continue

        try:
            candidate = candidate.resolve()
        except (OSError, RuntimeError):
            # if for some reason resolve() fails, skip it
            continue

        # 3) skip anything inside the framework itself
        if framework_dir in candidate.parents:
            continue

        # FOUND: a user file (e.g. app.py, manage.py, etc.)
        return candidate.parent

    # fallback: whatever cwd() is
    return Path(os.getcwd()).resolve()


def detect_project_root() -> Path:
    """
    Returns the consumer project's syntaxmatrixdir folder, creating it if necessary.
    All framework data & uploads live here.
    """
    # 1) First check the CWD (where your app:app is running)
    cwd = Path.cwd()
    candidate = cwd / "syntaxmatrixdir"
    if candidate.exists():
        return candidate

    # 2) Otherwise fall back to the old logic (e.g. inside site-packages)
    proj_root = scandir()
    fw_root = proj_root / "syntaxmatrixdir"
    fw_root.mkdir(exist_ok=True)
    return fw_root
