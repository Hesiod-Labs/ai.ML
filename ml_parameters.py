

PARAMETERS = {
    'logistic regression':
        (
            'penalty',
            'dual',
            'tol',
            'C',
            'fit_intercept',
            'intercept_scaling',
            'max_iter',
            'l1_ratio'
        ),
    'support vector classification':
        (
            'C',
            'kernel',
            'degree',
            'gamma',
            'coeff0',
            'shrinking',
            'tol',
            'max_iter',
        ),
    'k nearest neighbors':
        (
            'n_neighbors',
            'weights',
            'algorithm',
            'leaf_size',
            'p',
        ),
    'decision tree classification':
        (
            'criterion',
            'splitter',
            'max_depth',
            'min_samples_split',
            'min_samples_leaf',
            'min_weight_fraction_leaf',
            'max_features',
            'max_leaf_nodes',
            'min_impurity_decrease',
        ),
    'linear discriminant analysis':
        (
            'solver',
            'shrinkage',
            'priors',
            'n_components',
            'tol'
        )
}
