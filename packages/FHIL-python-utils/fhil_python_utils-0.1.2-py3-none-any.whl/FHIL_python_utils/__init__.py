"""
FHIL Python Utils

A collection of general utility functions for Python data analysis and visualization, including SVM-based classification
and plotting tools for various data types.

This package provides tools for:
- SVM feature analysis and classification
- Confusion matrix visualization
- Grid plotting for multiple AnnData objects
- Cluster annotation and consensus calling
"""

# Import functions from modules
from .svm import (
    svm_feature_weighting_heatmap,
    svm_classes_from_proba,
    annotate_clusters_by_consensus
)

from .plotting import (
    plot_confusion_matrix,
    grid_plot_adata
)

# Define what gets imported with "from FHIL_python_utils import *"
__all__ = [
    'svm_feature_weighting_heatmap',
    'svm_classes_from_proba', 
    'annotate_clusters_by_consensus',
    'plot_confusion_matrix',
    'grid_plot_adata'
]

__version__ = "0.1.2" 

