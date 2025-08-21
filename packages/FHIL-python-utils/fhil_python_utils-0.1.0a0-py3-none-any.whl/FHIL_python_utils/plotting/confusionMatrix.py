"""
Visualization utilities for spatial transcriptomics data.

This module provides functions for creating confusion matrices and grid plots
for multiple AnnData objects, commonly used in spatial transcriptomics analysis.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Union, List, Tuple


def confusionMatrix(
    x: Union[List, np.ndarray, pd.Series],
    y: Union[List, np.ndarray, pd.Series],
    normalize: bool = False,
    figsize: Tuple[int, int] = (8, 6),
    cmap: str = 'Blues',
    annot: bool = True
) -> None:
    """
    Create a confusion matrix visualization for any two sets of labels.
    
    This function creates a confusion matrix heatmap comparing two sets of
    categorical labels. It can handle any categorical data and provides
    options for normalization and customization.
    
    Parameters
    ----------
    x : Union[List, np.ndarray, pd.Series]
        First set of labels (typically true labels).
    y : Union[List, np.ndarray, pd.Series]
        Second set of labels (typically predicted labels).
    normalize : bool, default=False
        If True, normalize rows (true classes) to sum to 1 (percentage).
    figsize : Tuple[int, int], default=(8, 6)
        Figure size as (width, height) in inches.
    cmap : str, default='Blues'
        Colormap for the heatmap visualization.
    annot : bool, default=True
        Whether to display numerical annotations on the heatmap.
    
    Returns
    -------
    None
        Displays the confusion matrix plot.
    
    Notes
    -----
    - The confusion matrix shows y labels on rows and x labels on columns
    - When normalize=True, values are shown as percentages
    - All unique labels from both x and y are included in the matrix
    
    Examples
    --------
    >>> import numpy as np
    >>> 
    >>> # Create sample data
    >>> true_labels = ['A', 'B', 'A', 'C', 'B']
    >>> pred_labels = ['A', 'B', 'A', 'B', 'B']
    >>> 
    >>> # Plot confusion matrix
    >>> confusionMatrix(true_labels, pred_labels)   
    >>> 
    >>> # Plot normalized confusion matrix
    >>> confusionMatrix(true_labels, pred_labels, normalize=True)
    """
    # Convert inputs to categorical for consistent handling
    x_cat = pd.Categorical(x)
    y_cat = pd.Categorical(y)
    
    # Create confusion matrix DataFrame initialized to zero
    cm = pd.DataFrame(
        0, 
        index=y_cat.categories, 
        columns=x_cat.categories, 
        dtype=float if normalize else int
    )
    
    # Populate the confusion matrix
    for true, pred in zip(x_cat, y_cat):
        cm.loc[pred, true] += 1
    
    # Normalize if requested
    if normalize:
        cm = cm.div(cm.sum(axis=1), axis=0).fillna(0) * 100
    
    # Create the plot
    plt.figure(figsize=figsize)
    ax = sns.heatmap(
        cm,
        annot=annot,
        fmt=".0f" if normalize else "d",
        cmap=cmap,
        cbar=True,
        cbar_kws={'label': '% of Label 2'} if normalize else None
    )
    
    # Customize axis labels
    ax.set_xticks(
        [x + 0.5 for x in range(len(x_cat.categories))], 
        x_cat.categories, 
        rotation=45, 
        ha='right', 
        rotation_mode='anchor'
    )
    plt.xlabel("Label 1")
    plt.ylabel("Label 2")
    plt.title("Confusion Matrix" + (" (Normalized)" if normalize else ""))
    plt.tight_layout()
    plt.show()