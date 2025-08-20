"""
SVM-based classification utilities for spatial transcriptomics data.

This module provides functions for analyzing SVM models, extracting feature weights,
and performing consensus-based cluster annotation.
"""

from .featureWeightHeatmap import featureWeightingHeatmap
from .classesFromProba import classesFromProba
from .annotateClustersByConsensus import annotateClustersByConsensus
from .confusionBubbleMatrix import confusionBubbleMatrix

__all__ = [
    'featureWeightingHeatmap',
    'classesFromProba',
    'annotateClustersByConsensus',
    'confusionBubbleMatrix'
]
