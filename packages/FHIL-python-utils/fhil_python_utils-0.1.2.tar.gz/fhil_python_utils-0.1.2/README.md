# FHIL Python Utils

A collection of general utility functions for Python data analysis and visualization, including SVM-based classification and plotting tools for various data types.

## Available Functions

### SVM Analysis
- **`svm_feature_weighting_heatmap`**: Generate heatmaps showing the top informative features per class for SVM models.
- **`svm_classes_from_proba`**: Extract predicted classes from SVM probability predictions with confidence thresholds and margin criteria.
- **`annotate_clusters_by_consensus`**: Annotate clusters based on consensus of individual cell predictions using proportion thresholds.

### Visualization
- **`plot_confusion_matrix`**: Create confusion matrix visualizations for comparing two sets of categorical labels with optional normalization.
- **`grid_plot_adata`**: Create grid layouts of plots from multiple AnnData objects for easy comparison across datasets and annotations.

## Dependencies

- pandas
- numpy
- scanpy
- seaborn
- matplotlib
- pybiomart (for mapping ensembl IDs to gene symbols)
- anndata
- sklearn (for SVM functionality)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
