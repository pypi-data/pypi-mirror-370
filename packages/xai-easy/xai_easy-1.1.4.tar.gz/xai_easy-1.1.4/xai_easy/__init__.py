"""
XAI Easy - Explainable AI Made Simple
Created by Prajwal

A powerful yet simple Python package for making machine learning models 
interpretable and transparent through advanced explainability techniques.
"""

__version__ = "1.0.0"
__author__ = "Prajwal"
__description__ = "Explainable AI Made Simple - Professional ML Model Interpretation"

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
