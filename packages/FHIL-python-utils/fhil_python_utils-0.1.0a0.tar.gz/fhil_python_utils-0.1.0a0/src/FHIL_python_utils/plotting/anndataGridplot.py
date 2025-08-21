"""
Grid plotting utilities for AnnData objects.
"""

from typing import Dict, List, Callable, Optional, Tuple
from anndata import AnnData
import numpy as np
import matplotlib.pyplot as plt

def anndataGridplot(
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
    >>> anndataGridplot(  
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