import sys
import importlib

def __getattr__(name):
    try:
        rust_ext = sys.modules.get("velopix.velopix")
        if rust_ext is None:
            rust_ext = importlib.import_module("velopix.velopix")
    except ImportError as e:
        raise ImportError("Cannot load the Rust extension velopix.velopix") from e

    rust_sub = getattr(rust_ext, "DetectorEvent", None)
    if rust_sub is None:
        raise ImportError("Rust submodule 'DetectorEvent' not found in velopix.velopix")

    if hasattr(rust_sub, name):
        value = getattr(rust_sub, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module 'velopix.DetectorEvent' has no attribute '{name}'")
