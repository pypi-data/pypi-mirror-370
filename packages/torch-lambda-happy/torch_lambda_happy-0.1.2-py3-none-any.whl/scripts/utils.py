import matplotlib


def choose_matplotlib_backend(interactive: bool = False) -> str:
    """Selects and sets an available matplotlib backend.

    Args:
        interactive (bool, optional): If True, prefer interactive backends.

    Raises:
        RuntimeError: If no suitable backend is found.

    Returns:
        str: The name of the selected backend.
    """
    preferred_backends = (
        ["Qt5Agg", "TkAgg", "Agg"] if interactive else ["Agg", "Qt5Agg", "TkAgg"]
    )
    for backend in preferred_backends:
        try:
            matplotlib.use(backend, force=True)
            print(f"[matplotlib] Using backend: {backend}")
            return backend
        except ImportError:
            continue
    raise RuntimeError("No suitable matplotlib backend found.")
