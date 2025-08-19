"""
SVM-based classification utilities for spatial transcriptomics data.

This module provides functions for analyzing SVM models, extracting feature weights,
and performing consensus-based cluster annotation.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
from typing import Dict, List, Tuple, Union, Optional
from anndata import AnnData


def svm_feature_weighting_heatmap(
    model: Dict,
    n: int = 5,
    figsize: Tuple[int, int] = (8, 12)
) -> None:
    """
    Generate a heatmap showing the top informative features per class for an SVM model.
    
    This function analyzes the coefficients of a trained SVM classifier to identify
    the most important features for each class. It works with One-vs-One (OvO) SVM
    classifiers by accumulating feature weights across all pairwise comparisons.
    
    Parameters
    ----------
    model : Dict
        Dictionary containing the trained SVM model with 'svc' key containing
        the sklearn SVM classifier object.
    n : int, default=5
        Number of top features to display per class.
    figsize : Tuple[int, int], default=(8, 12)
        Figure size as (width, height) in inches.
    
    Returns
    -------
    None
        Displays the heatmap plot.
    
    Notes
    -----
    - The function expects the SVM model to be trained with One-vs-One strategy
    - Feature weights are accumulated across all pairwise comparisons
    - The heatmap shows the average absolute weight for each feature per class
    
    Examples
    --------
    >>> from sklearn.svm import SVC
    >>> from sklearn.multiclass import OneVsOneClassifier
    >>> 
    >>> # Train your SVM model
    >>> svc = SVC(kernel='linear', probability=True)
    >>> ovo_svm = OneVsOneClassifier(svc)
    >>> ovo_svm.fit(X_train, y_train)
    >>> 
    >>> # Create model dictionary
    >>> model = {'svc': ovo_svm}
    >>> 
    >>> # Generate feature weight heatmap
    >>> svm_feature_weighting_heatmap(model, n=10)
    """
    # Extract model components
    svc = model['svc']
    feature_names = svc.feature_names_in_
    class_labels = svc.classes_
    n_classes = len(class_labels)
    
    # Generate class pairs for One-vs-One comparisons
    class_pairs = list(combinations(range(n_classes), 2))
    
    # Initialize weight accumulation
    n_features = svc.coef_.shape[1]
    class_feature_weights = {cls: np.zeros(n_features) for cls in range(n_classes)}
    counts = {cls: 0 for cls in range(n_classes)}
    
    # Accumulate absolute weights from pairwise classifiers
    for coef, (i, j) in zip(svc.coef_, class_pairs):
        class_feature_weights[i] += np.abs(coef)
        class_feature_weights[j] += np.abs(coef)
        counts[i] += 1
        counts[j] += 1
    
    # Find top features for each class
    top_features = {}
    for cls in range(n_classes):
        weights = class_feature_weights[cls].A1 # if hasattr(class_feature_weights[cls], 'A1') else class_feature_weights[cls]
        top_idx = np.argsort(weights)[::-1][:n]
        top_features[class_labels[cls]] = {
            feature_names[i]: weights[i] for i in top_idx
        }
    
    # Convert to DataFrame for plotting
    plotdata = pd.DataFrame(top_features).fillna(0)
    
    # Create heatmap
    plt.figure(figsize=figsize)
    ax = sns.heatmap(
        plotdata, 
        cmap='viridis', 
        fmt=".2f", 
        cbar_kws={'label': 'Avg |Weight|'}
    )
    
    # Customize plot
    plt.title(f'Top {n} features per class from OvO SVM')
    ax.set_xticks(
        [x + 0.5 for x in range(plotdata.shape[1])], 
        plotdata.columns.values, 
        rotation=45, 
        ha='right', 
        rotation_mode='anchor'
    )
    plt.ylabel('Feature')
    plt.xlabel('Class')
    plt.tight_layout()
    plt.show()


def svm_classes_from_proba(
    probs: np.ndarray,
    classes: List[str],
    threshold: float = 0.5,
    margin: float = 0.1
) -> Tuple[List[str], List[str]]:
    """
    Extract predicted classes from SVM probability predictions with confidence thresholds.
    
    This function processes probability predictions from an SVM classifier and assigns
    class labels based on confidence thresholds and margin criteria. It can handle
    cases where predictions are uncertain or ambiguous.
    
    Parameters
    ----------
    probs : np.ndarray
        Probability predictions from SVM.predict_proba() with shape (n_samples, n_classes).
    classes : List[str]
        List of class labels corresponding to the probability columns.
    threshold : float, default=0.5
        Minimum required confidence for a prediction to be considered valid.
        Predictions below this threshold are labeled as 'unknown'.
    margin : float, default=0.1
        Margin for considering predictions as ambiguous. If the difference between
        top and second-best probabilities is within this margin, the prediction
        is marked as 'mixed'.
    
    Returns
    -------
    Tuple[List[str], List[str]]
        Two lists containing:
        - Detailed predictions (may include multiple classes for ambiguous cases)
        - Simplified predictions ('unknown', 'mixed', or single class)
    
    Examples
    --------
    >>> from sklearn.svm import SVC
    >>> 
    >>> # Assuming you have trained an SVM and made predictions
    >>> svm = SVC(probability=True)
    >>> svm.fit(X_train, y_train)
    >>> probabilities = svm.predict_proba(X_test)
    >>> 
    >>> # Get class predictions with confidence thresholds
    >>> detailed_preds, simple_preds = svm_classes_from_proba(
    ...     probabilities, 
    ...     classes=['class_A', 'class_B', 'class_C'],
    ...     threshold=0.6,
    ...     margin=0.15
    ... )
    """
    pred_classes = []
    pred_classes_simplified = []
    
    for prob in probs:
        # Find top and second-best predictions
        top_idx = np.argmax(prob)
        top_prob = prob[top_idx]
        
        # Find second-best prediction
        second_idx = np.argsort(prob)[-2]
        second_prob = prob[second_idx]
        
        # Apply classification logic
        if top_prob < threshold:
            pred_classes.append('unknown')
            pred_classes_simplified.append('unknown')
        elif (top_prob - second_prob) <= margin:
            pred_classes.append(f"{classes[top_idx]} | {classes[second_idx]}")
            pred_classes_simplified.append('mixed')
        else:
            pred_classes.append(classes[top_idx])
            pred_classes_simplified.append(classes[top_idx])
    
    return pred_classes, pred_classes_simplified


def annotate_clusters_by_consensus(
    obj: AnnData,
    cluster_column: str = 'over_clustering',
    annotation_column: str = 'svm_predicted_class',
    proportion_threshold: float = 0.5,
    margin: float = 0.15,
    output_column: str = 'overclustering_consensus_annotation'
) -> None:
    """
    Annotate clusters based on consensus of individual cell predictions.
    
    This function aggregates SVM predictions at the cluster level to assign
    consensus annotations. A cluster is annotated if a sufficient proportion
    of cells within it share the same prediction, or if there are two
    competing predictions within a specified margin.
    
    Parameters
    ----------
    obj : AnnData
        AnnData object containing the data and annotations.
    cluster_column : str, default='over_clustering'
        Column name in obj.obs containing cluster assignments.
    annotation_column : str, default='svm_predicted_class'
        Column name in obj.obs containing individual cell predictions.
    proportion_threshold : float, default=0.5
        Minimum proportion of cells that must share the same annotation
        for a cluster to be labeled (excluding 'unknown' predictions).
    margin : float, default=0.15
        Maximum difference in proportions between top two annotations
        for both to be included in the final label.
    output_column : str, default='overclustering_consensus_annotation'
        Column name for the consensus annotations in obj.obs.
    
    Returns
    -------
    None
        Modifies obj.obs by adding the consensus annotations.
    
    Notes
    -----
    - Clusters with no clear majority are labeled as 'unknown'
    - When two annotations are within the margin, they are combined with ' | '
    - The function modifies the AnnData object in-place
    
    Examples
    --------
    >>> import scanpy as sc
    >>> 
    >>> # Assuming you have an AnnData object with cluster and prediction columns
    >>> adata = sc.read_h5ad("your_data.h5ad")
    >>> 
    >>> # Annotate clusters based on SVM predictions
    >>> annotate_clusters_by_consensus(
    ...     adata,
    ...     cluster_column='leiden_clusters',
    ...     annotation_column='svm_predictions',
    ...     proportion_threshold=0.6,
    ...     margin=0.1
    ... )
    """
    # Calculate proportions of each annotation within each cluster
    data = (
        obj.obs.groupby(cluster_column)[annotation_column]
        .value_counts(normalize=True)
        .groupby(level=0)
        .head(2)  # Get top 2 annotations per cluster
        .reset_index(name='count')
    )
    
    # Assign consensus labels
    assigned_labels = {}
    for group, group_df in data.groupby(cluster_column):
        top_values = group_df.sort_values('count', ascending=False).reset_index(drop=True)
        top1 = top_values.loc[0]
        
        # Check if top annotation meets threshold
        if top1['count'] >= proportion_threshold:
            assigned_labels[group] = top1[annotation_column]
        
        # Check for competing annotations within margin
        elif len(top_values) > 1:
            top2 = top_values.loc[1]
            
            # Check margin condition (exclude 'unknown' from dual labeling)
            if (abs(top1['count'] - top2['count']) <= margin and 
                'unknown' not in {top1[annotation_column], top2[annotation_column]}):
                values = sorted([top1[annotation_column], top2[annotation_column]])
                assigned_labels[group] = f"{values[0]} | {values[1]}"
            else:
                assigned_labels[group] = 'unknown'
        
        else:
            assigned_labels[group] = 'unknown'
    
    # Add consensus annotations to AnnData object
    obj.obs[output_column] = obj.obs[cluster_column].map(assigned_labels)