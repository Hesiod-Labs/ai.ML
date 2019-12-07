"""Reference data dictionaries for scoring metrics and algorithm parameters.
    Utilized in aiml_dash.callbacks.py for generating Dash core component
    options, and functionality. Allows Dash core components to be
    auto-generated since the structure of the dictionary is known.
"""

SCORING_METRICS = {
    'classification': {
        'default': 'accuracy',
        'options': {
            'accuracy': {'label': 'accuracy'},
            'balanced_accuracy': {'label': 'balanced accuracy'},
            'brier_score_loss': {'label': 'brier score loss'},
            'f1': {'label': 'f1 (no averaging)'},
            'f1_micro': {'label': 'f1 (micro averaging)'},
            'f1_macro': {'label': 'f1 (macro averaging)'},
            'f1_weighted': {'label': 'f1 (weighted averaging)'},
            'f1_samples': {'label': 'f1 (samples averaging)'},
            'precision': {'label': 'precision (no averaging)'},
            'precision_micro': {'label': 'precision (micro averaging)'},
            'precision_macro': {'label': 'precision (macro averaging)'},
            'precision_weighted': {'label': 'precision (weighted averaging)'},
            'precision_samples': {'label': 'precision (samples averaging)'},
            'recall': {'label': 'precision (no averaging)'},
            'recall_micro': {'label': 'recall (micro averaging)'},
            'recall_macro': {'label': 'recall (macro averaging)'},
            'recall_weighted': {'label': 'recall (weighted averaging)'},
            'recall_samples': {'label': 'recall (samples averaging)'},
            'jaccard': {'label': 'jaccard (no averaging)'},
            'jaccard_micro': {'label': 'jaccard (micro averaging)'},
            'jaccard_macro': {'label': 'jaccard (macro averaging)'},
            'jaccard_weighted': {'label': 'jaccard (weighted averaging)'},
            'jaccard_samples': {'label': 'jaccard (samples averaging)'},
            'roc_auc_score': {'label': 'ROC AUC'}
        }
    }
}

PARAMETERS = {
    'logistic regression': {
        'solver': {
            'label': 'algorithm',
            'widget': 'dropdown',
            'options': {
                'newton-cg': {'label': 'nonlinear conjugate gradient'},
                'lbfgs': {'label': 'limited-memory BFGS'},
                'sag': {'label': 'stochastic average gradient'},
                'saga': {'label': 'stochastic average gradient ameliore'},
                'liblinear': {
                    'label': 'library for large linear classification'}
            },
            'default': 'liblinear'
        },
        'penalty': {
            'label': 'penalty',
            'widget': 'dropdown',
            'options': {
                'l1': {'label': 'l1'},
                'l2': {'label': 'l2'},
                'elasticnet': {'label': 'elastic net'},
                'none': {'label': 'none'}
            },
            'default': 'l2'
        },
        'l1_ratio': {
            'label': 'l1 ratio',
            'widget': 'input',
            'options': {'min': 0,
                        'max': 1,
                        'step': 0.0001,
                        },
            'default': 0
        },
        'dual': {
            'label': 'dual',
            'widget': 'switch',
            'options': (True, False),
            'default': False
        },
        'tol': {
            'label': 'tolerance',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 0.0001,
            },
            'default': 0.0001
        },
        'C': {
            'label': 'cost',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 0.0001,
            },
            'default': 1
        },
        'fit_intercept': {
            'label': 'fit intercept',
            'widget': 'switch',
            'options': (True, False),
            'default': True
        },
        'intercept_scaling': {
            'label': 'intercept scaling',
            'widget': 'input',
            'options': {'min': 0,
                        'max': 1000000,
                        'step': 0.0001,
                        },
            'default': 1
        },
        'max_iter': {
            'label': 'max iterations (0 = no limit)',
            'widget': 'input',
            'options': {'min': 0,
                        'max': 1000000,
                        'step': 1,
                        },
            'default': 1000000
        }
    },
    'support vector classification (coming soon)': {
        'kernel': {
            'label': 'kernel',
            'widget': 'dropdown',
            'options': {
                'linear': {'label': 'linear'},
                'poly': {'label': 'polynomial'},
                'rbf': {'label': 'radial basis function'},
                'sigmoid': {'label': 'sigmoid'}
            },
            'default': 'rbf'
        },
        'C': {
            'label': 'cost',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 0.0001,
            },
            'default': 1
        },
        'degree': {
            'label': 'degree',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 1,
            },
            'default': 3
        },
        'gamma': {
            'label': 'gamma',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 0.0001,
            },
            'default': 50
        },
        'coef0': {
            'label': 'constant coefficient',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 0.0001,
            },
            'default': 0
        },
        'shrinking': {
            'label': 'shrinking',
            'widget': 'switch',
            'options': (True, False),
            'default': True,
        },
        'tol': {
            'label': 'tolerance',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 0.001,
            },
            'default': 0.001
        },
        'max_iter': {
            'label': 'max iterations (0 = no limit)',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 1,
            },
            'default': 1000000,
        }
    },
    'k nearest neighbors (coming soon)': {
        'algorithm': {
            'label': 'algorithm',
            'widget': 'dropdown',
            'options': {
                'auto': {'label': 'auto'},
                'ball_tree': {'label': 'ball tree'},
                'kd_tree': {'label': 'kd tree'},
                'brute': {'label': 'brute force'}
            },
            'default': 'auto'
        },
        'weights': {
            'label': 'weights',
            'widget': 'dropdown',
            'options': {
                'uniform': {'label': 'uniform'},
                'distance': {'label': 'distance'}
            },
            'default': 'uniform',
        },
        'metric': {
            'label': 'distance metric',
            'widget': 'dropdown',
            'options': {
                'euclidian': {'label': 'euclidian'},
                'manhattan': {'label': 'manhattan'},
                'chebyshev': {'label': 'chebyshev'},
                'minkowski': {'label': 'minkowski'}
            },
            'default': 'euclidian'
        },
        'p': {
            'label': 'minkowski power',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 0.0001,
            },
            'default': 0
        },
        'n_neighbors': {
            'label': 'number of neighbors',
            'widget': 'input',
            'options': {
                'min': 1,
                'max': 1000000,
                'step': 1,
            },
            'default': 5,
        },
        'leaf_size': {
            'label': 'leaf size',
            'widget': 'input',
            'options': {
                'min': 1,
                'max': 1000000,
                'step': 1,
            },
            'default': 30
        },
    },
    'decision tree classification (coming soon)': {
        'criterion': {
            'label': 'split criterion',
            'widget': 'dropdown',
            'options': {
                'gini': {'label': 'gini'},
                'entropy': {'label': 'entropy'}
            },
            'default': 'gini'
        },
        'splitter': {
            'label': 'split strategy',
            'widget': 'dropdown',
            'options': {
                'best': {'label': 'best'},
                'random': {'label': 'random'}
            },
            'default': 'best'
        },
        'max_features': {
            'label': 'max features for split',
            'widget': 'dropdown',
            'options': {
                'sqrt': {'label': 'square root'},
                'log2': {'label': 'log (base 2)'},
                'num_features': {'label': 'number of features'},
            },
            'default': 'sqrt'
        },
        'max_depth': {
            'label': 'max depth (0 = no limit)',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 1,
            },
            'default': 0
        },
        'min_samples_split': {
            'label': 'min samples to split',
            'widget': 'input',
            'options': {
                'min': 1,
                'max': 1000000,
                'step': 1,
            },
            'default': 2
        },
        'min_samples_leaf': {
            'label': 'min samples per leaf',
            'widget': 'input',
            'options': {
                'min': 1,
                'max': 1000000,
                'step': 1,
            },
            'default': 5
        },
        'min_weight_fraction_leaf': {
            'label': 'min weight fraction per leaf',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1,
                'step': 0.0001,
            },
            'default': 0
        },
        'max_leaf_nodes': {
            'label': 'max leaf nodes (0 = no limit)',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 1,
            },
            'default': 5
        },
        'min_impurity_decrease': {
            'label': 'min impurity decrease',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 0.0001,
            },
            'default': 0
        }
    },
    'linear discriminant analysis (coming soon)': {
        'solver': {
            'label': 'solver',
            'widget': 'dropdown',
            'options': {
                'svd': {'label': 'singular value decomposition'},
                'lsqr': {'label': 'least squares solution'},
                'eigen': {'label': 'eigenvalue decomposition'}
            },
            'default': 'svd'
        },
        'shrinkage': {
            'label': 'shrinkage',
            'widget': 'dropdown',
            'options': {
                'fixed': {'label': 'fixed'},
                'auto': {'label': 'Ledoit-Wolf (auto)'}
            },
            'default': 'fixed'
        },
        'n_components': {
            'label': 'number of components',
            'widget': 'input',
            'options': {
                'min': 1,
                'max': 1000000,
                'step': 1,
            },
            'default': 5
        },
        'tol': {
            'label': 'tolerance',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 0.0001,
            },
            'default': 0.0001
        },
    }
}
