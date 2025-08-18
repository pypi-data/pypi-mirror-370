try:
    from .somu import som
except ImportError:
    from .torchsom import som

    print("Failed to import somu. Falling back to the torch implementation.")

__all__ = ["som"]
