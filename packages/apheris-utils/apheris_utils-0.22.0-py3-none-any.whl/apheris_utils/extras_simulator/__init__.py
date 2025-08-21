try:
    from . import data

    __all__ = [
        "data",
    ]

except ImportError:
    raise ImportError(
        "Simulator dependencies not found. Please install "
        "apheris-utils with the 'simulator' extra to use this module. "
        "`pip install apheris-utils[simulator]`"
    )
