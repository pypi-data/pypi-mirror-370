from .datasets import load_data_lalonde, load_data_tof
from .design.diagnostics import summarize_matching
from .design.matchers import stochastic_match
from .estimation.ensemble import estimate_te, estimate_te_multi
from .utils import as_pairwise

__all__ = [
    "load_data_tof",
    "load_data_lalonde",
    "stochastic_match",
    "estimate_te",
    "summarize_matching",
    "estimate_te_multi",
    "as_pairwise",
]

try:
    from importlib.metadata import PackageNotFoundError, version  # Py3.8+
except Exception:  # pragma: no cover
    from importlib_metadata import (  # type: ignore  # backport
        PackageNotFoundError,
        version,
    )

try:
    __version__ = version("causalem")  # <-- use *distribution* name
except PackageNotFoundError:  # e.g., running from source without install
    __version__ = "0+unknown"
