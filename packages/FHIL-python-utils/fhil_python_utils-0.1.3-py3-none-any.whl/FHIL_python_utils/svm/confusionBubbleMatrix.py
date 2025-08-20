"""
SVM confusion matrix visualization utilities.
"""

from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colorbar import ColorbarBase
from typing import Union, List, Optional
import numpy as np
import pandas as pd

def confusionBubbleMatrix(
    probs: Union[pd.DataFrame, np.ndarray], 
    y_true: Union[List, np.ndarray, pd.Series], 
    class_names: Optional[List[str]] = None
) -> None:
    """
    Create a bubble plot confusion matrix showing prediction probabilities.
    
    Parameters
    ----------
    probs : pd.DataFrame or np.ndarray
        Probability predictions from SVM.predict_proba()
    y_true : array-like
        True labels
    class_names : list, optional
        Names of the classes. If None, inferred from probs columns.
    
    Returns
    -------
    None
        Displays the bubble plot confusion matrix.
    """
    # Convert true labels to categorical if not already
    y_true = pd.Categorical(y_true)

    # If class names are not provided, infer them from columns of probs
    if class_names is None:
        class_names = probs.columns
    # class_names = pd.Index(class_names)
    
    # Convert probs to DataFrame if it's not already
    probs = pd.DataFrame(probs, columns=class_names)
    
    # Get predicted labels and max probabilities
    pred_labels = probs.idxmax(axis=1)
    pred_probs = probs.max(axis=1)

    # Combine all into a DataFrame
    df = pd.DataFrame({
        'current_label': y_true,
        'pred_label': pd.Categorical(pred_labels, categories=class_names),
        'pred_prob': pred_probs
    })

    # Group stats
    grouped = (
        df.groupby(['current_label', 'pred_label'])
        .agg(count=('pred_prob', 'count'), median_score=('pred_prob', 'median'))
        .reset_index(name='count')
    )

    # Compute proportion within each true label
    total_per_true = df['current_label'].value_counts()
    grouped['proportion'] = grouped.apply(
        lambda row: row['count'] / total_per_true[row['current_label']],
        axis=1
    )

    # Set up plot
    true_classes = pd.Index(y_true.categories)
    pred_classes = pd.Index(class_names)

    fig, ax = plt.subplots(figsize=(max((len(pred_classes) / 3) + 4, 6), max((len(true_classes) / 4) + 4, 6)))
    ax.set_xlim(-0.5, len(pred_classes) - 0.5)
    ax.set_ylim(-0.5, len(true_classes) - 0.5)

    # norm = plt.Normalize(df['pred_prob'].min(), df['pred_prob'].max())
    norm = plt.Normalize(0, 1)
    cmap = plt.cm.YlGnBu
    max_dot_size = 800

    for _, row in grouped.iterrows():
        x = pred_classes.get_loc(row['pred_label'])
        y = true_classes.get_loc(row['current_label'])
        size = max_dot_size * row['proportion']
        color = cmap(norm(row['median_score']))
        ax.scatter(x, y, s=size, color=color, edgecolor='black', alpha=0.8)

    # Label axes
    ax.set_xticks(range(len(pred_classes)))
    ax.set_xticklabels(pred_classes, rotation=45, ha='right')
    ax.set_yticks(range(len(true_classes)))
    ax.set_yticklabels(true_classes)
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")

    # Size legend
    size_legend_props = [0.1, 0.25, 0.5, 0.75]
    size_handles = [
        ax.scatter([], [], s=p * max_dot_size, color='gray', alpha=0.6, label=f"{int(p*100)}%")
        for p in size_legend_props
    ]
    legend1 = ax.legend(
        handles=size_handles,
        title="% of true label",
        loc='upper left',
        bbox_to_anchor=(1.05, 1),
        frameon=True
    )
    ax.add_artist(legend1)

    # Colorbar for median probability
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="4%", pad=0.1)
    colorbar = ColorbarBase(cax, cmap=cmap, norm=norm) #, norm=norm, 
    colorbar.set_label('Median predicted probability')

    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()
