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

# Import common dependencies at package level for use across all submodules
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# from typing import Dict, List, Tuple, Union, Optional, Callable
# from anndata import AnnData

# # Import functions from submodules
# from .svm import (
#     featureWeightHeatmap,
#     classesFromProba,
#     annotateClustersByConsensus,
#     confusionBubbleMatrix
# )

# from .plotting import (
#     confusionMatrix,
#     anndataGridplot,
#     rotateAxisLabels
# )

# # Define what gets imported with "from FHIL_python_utils import *"
# __all__ = [
#     # SVM functions
#     'featureWeightHeatmap',
#     'classesFromProba', 
#     'annotateClustersByConsensus',
#     'confusionBubbleMatrix',
#     # Plotting functions
#     'confusionMatrix',
#     'anndataGridplot',
#     'rotateAxisLabels',
# ]

from ._version import version as __version__
