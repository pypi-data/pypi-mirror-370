"""
bvalcalc: calculate relative diversity (B) under background selection.
"""

__version__ = "0.6.5"

# Expose main entry point
from .cli import main
from .core.calculateB import calculateB_linear, calculateB_recmap, calculateB_unlinked, get_params


__all__ = [
    "get_params", "calculateB_linear", "calculateB_unlinked",
    "main",
    "__version__",
]