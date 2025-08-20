try:
    from . import main
except ImportError as exc:
    raise ImportError("One or more dependencies of polybot were not found. "
                      "Consider installing halerium_utilities with `pip install halerium_utilities[polybot]`.")
