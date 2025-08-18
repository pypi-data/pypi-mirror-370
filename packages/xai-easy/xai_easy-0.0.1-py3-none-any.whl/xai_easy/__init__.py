"""xai_easy: v2 - Improved Explainable AI helpers with broader model support."""
__version__ = "0.0.1"

from .explain import explain_model, explain_instance, permutation_importance, select_top_features
from .visualize import plot_importance, save_html_report

__all__ = [
    "explain_model",
    "explain_instance",
    "permutation_importance",
    "select_top_features",
    "plot_importance",
    "save_html_report",
]
