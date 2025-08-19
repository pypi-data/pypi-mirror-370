"""
Visualization utilities for spatial transcriptomics data.

This module provides functions for creating confusion matrices and grid plots
for multiple AnnData objects, commonly used in spatial transcriptomics analysis.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Union, Optional, Callable
from anndata import AnnData


def plot_confusion_matrix(
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
    >>> plot_confusion_matrix(true_labels, pred_labels)
    >>> 
    >>> # Plot normalized confusion matrix
    >>> plot_confusion_matrix(true_labels, pred_labels, normalize=True)
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


def grid_plot_adata(
    adata_dict: Dict[str, AnnData],
    plot_func: Callable,
    color_keys: List[str],
    plot_kwargs: Optional[Dict] = None,
    per_row: bool = True,
    figsize: Tuple[int, int] = (4, 4),
    pass_show: bool = True
) -> None:
    """
    Create a grid of plots from multiple AnnData objects.
    
    This function creates a grid layout of plots, where each plot is generated
    by applying a plotting function to an AnnData object with specific color
    keys. It's useful for comparing the same visualization across multiple
    datasets or different color annotations.
    
    Parameters
    ----------
    adata_dict : Dict[str, AnnData]
        Dictionary mapping names to AnnData objects.
    plot_func : Callable
        Function that creates plots from AnnData objects. Should accept
        AnnData as first argument and keyword arguments.
    color_keys : List[str]
        List of color keys to use for plotting (e.g., gene names, annotations).
    plot_kwargs : Optional[Dict], default=None
        Additional keyword arguments to pass to the plotting function.
    per_row : bool, default=True
        If True, each row represents an AnnData object and each column a color key.
        If False, each row represents a color key and each column an AnnData object.
    figsize : Tuple[int, int], default=(4, 4)
        Base figure size for individual plots. Final figure size will be
        (figsize[0] * n_cols, figsize[1] * n_rows).
    pass_show : bool, default=True
        Whether to pass show=False to the plotting function to prevent
        individual plots from being displayed.
    
    Returns
    -------
    None
        Displays the grid of plots.
    
    Notes
    -----
    - The plotting function should accept 'color' and 'ax' parameters
    - If pass_show=True, the function should also accept a 'show' parameter
    - The grid layout is automatically determined based on the number of
      AnnData objects and color keys
    
    Examples
    --------
    >>> import scanpy as sc
    >>> 
    >>> # Create sample AnnData objects
    >>> adata1 = sc.datasets.pbmc68k_reduced()
    >>> adata2 = sc.datasets.pbmc3k()
    >>> 
    >>> # Define plotting function (e.g., scanpy's umap)
    >>> def plot_umap(adata, color, ax=None, show=True):
    ...     sc.pl.umap(adata, color=color, ax=ax, show=show)
    >>> 
    >>> # Create grid plot
    >>> grid_plot_adata(
    ...     {'PBMC68k': adata1, 'PBMC3k': adata2},
    ...     plot_func=plot_umap,
    ...     color_keys=['leiden', 'louvain'],
    ...     figsize=(6, 6)
    ... )
    """
    if plot_kwargs is None:
        plot_kwargs = {}
    
    # Determine grid dimensions
    n_rows = len(adata_dict) if per_row else len(color_keys)
    n_cols = len(color_keys) if per_row else len(adata_dict)
    
    # Create subplot grid
    fig, axes = plt.subplots(
        n_rows, 
        n_cols, 
        figsize=(figsize[0] * n_cols, figsize[1] * n_rows)
    )
    
    # Handle single row/column cases
    if n_rows == 1:
        axes = np.expand_dims(axes, axis=0)
    if n_cols == 1:
        axes = np.expand_dims(axes, axis=1)
    
    # Create plots
    for row_i, (obj_name, adata) in enumerate(adata_dict.items() if per_row else color_keys):
        for col_i, color in enumerate(color_keys if per_row else adata_dict.items()):
            # Determine current indices and data
            i, j = (row_i, col_i) if per_row else (col_i, row_i)
            current_adata = adata if per_row else adata_dict[color]
            current_color = color if per_row else obj_name
            ax = axes[i, j]
            
            # Prepare function call arguments
            call_kwargs = {
                "color": current_color,
                "ax": ax,
                **plot_kwargs
            }
            
            if pass_show:
                call_kwargs["show"] = False
            
            # Create the plot
            plot_func(current_adata, **call_kwargs)
            
            # Set title
            title = f"{obj_name} - {current_color}" if per_row else f"{color} - {obj_name}"
            ax.set_title(title)
    
    plt.tight_layout()
    plt.show()
