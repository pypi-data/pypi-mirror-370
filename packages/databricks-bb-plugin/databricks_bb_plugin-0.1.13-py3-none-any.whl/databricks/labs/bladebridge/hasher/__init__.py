import sys
import importlib
import platform
from pathlib import Path
from typing import Callable

_compute_hash: Callable[[list[str]], str] | None = None


def _load_hasher() -> Callable[[list[str]], str]:
    global _compute_hash
    if _compute_hash is None:
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == "darwin":
            system = "macos_arm64" if machine in ("arm64", "aarch64") else "macos"
        # load module dynamically to avoid side effects with pytest
        # trying to load binaries for non-current platform
        if system == "windows":
            if sys.maxsize > 2**32:
                system = "windows_x86_64"
            else:
                system = "windows_x86"
        hasher = importlib.import_module(f".{system}", package=__name__)
        _compute_hash = getattr(hasher, "compute_hash", None)
    return _compute_hash


def compute_hash(args: list[str]) -> str:
    try:
        _load_hasher()
        return _compute_hash(args)
    except ImportError as e:
        path = Path("pyarmor.bug.log")
        if path.exists():
            print(path.read_text("utf-8"))
        raise e
