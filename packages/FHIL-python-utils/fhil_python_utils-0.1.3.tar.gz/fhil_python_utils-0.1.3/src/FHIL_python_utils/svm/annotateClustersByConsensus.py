"""
SVM cluster annotation utilities for consensus-based labeling.
"""

from anndata import AnnData

def annotateClustersByConsensus(
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
    >>> annotateClustersByConsensus(
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