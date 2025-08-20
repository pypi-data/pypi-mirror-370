"""
SVM feature weight analysis utilities.
"""

from itertools import combinations
from typing import Dict, Tuple

def featureWeightingHeatmap(
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
        Displays the feature weight heatmap.
    
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
    >>> featureWeightingHeatmap(model, n=10)
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

