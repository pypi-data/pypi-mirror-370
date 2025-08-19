import ctypes
import os
from pathlib import Path

__all__ = ["start_session"]

# Find the shared library
def _find_library():
    """Find the shared library in the package directory."""
    package_dir = Path(__file__).parent
    if os.name == "nt":
        files = package_dir.glob("_gosmp.*.pyd")
    else:
        files = package_dir.glob("_gosmp.*.so")
    if files:
        return str(next(files))

    raise RuntimeError(f"Could not find _gosmp shared library in {package_dir}")

_lib = ctypes.CDLL(_find_library())

# Bindings/Renaming (to keep standard Python naming conventions)
_StartSession = _lib.StartSession
_StartSession.restype = ctypes.c_void_p
_StartSession.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]

def start_session(sessionId: str, url: str, tokenValue: str, endpoint: str, clientId: str, targetId: str) -> None:
    _StartSession(sessionId.encode('utf-8'), url.encode('utf-8'), tokenValue.encode('utf-8'), endpoint.encode('utf-8'), clientId.encode('utf-8'), targetId.encode('utf-8'))