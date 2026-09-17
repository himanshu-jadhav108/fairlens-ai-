"""
Explainability and attribution analysis module.
"""
from .shap_engine import SHAPEngine
from .comparison import compare_attributions

__all__ = ["SHAPEngine", "compare_attributions"]
