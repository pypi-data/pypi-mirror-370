import os

try:
    from .somu import som

    assert os.path.exists("/opt/arrayfire")
except (ImportError, AssertionError):
    from .torchsom import som

    print("Failed to import somu. Falling back to the torch implementation.")

__all__ = ["som"]
