"""
SVM classification utilities for probability-based predictions.
"""

from typing import List, Tuple
import numpy as np

def classesFromProba(
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
    >>> detailed_preds, simple_preds = classesFromProba(
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

