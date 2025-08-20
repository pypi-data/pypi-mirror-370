__version__ = "0.0.0"

from .core import Graph

import warnings

warnings.warn(
    (
        "\n\nIf you are using this package, please contact the symbolic reasoning team.\n\n"
        "This library is still in the early stages of development. Interfaces "
        "_will_ change. Performance is appropriate only for exploring small "
        "graphs; there are known asymptotic catastrophes. For more, please see the README."
    ),
    FutureWarning,
    stacklevel=2
)

__all__ = [
    "Graph",
]
