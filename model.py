from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import SVC

# - Raise errors if there is bad data
# - Return numpy array? Or just add it into it yourself
# - Accuracy scores and metrics from confusion matrix etc, score and loss
# - Look into what grid search csv does
# - Cross validation strategies


LOGISTIC_REGRESSION = (
    'penalty',
    'dual',
    'tol',
    'C',
    'fit_intercept',
    'intercept_scaling',
    'max_iter',
    'l1_ratio'
)

SUPPORT_VECTOR_CLASSIFICATION = (
    'C',
    'kernel',
    'degree',
    'gamma',
    'coeff0',
    'shrinking',
    'tol',
    'max_iter',
)

K_NEAREST_NEIGHBORS = (
    'n_neighbors',
    'weights',
    'algorithm',
    'leaf_size',
    'p',
)
DECISION_TREE_CLASSIFICATION = (
    'criterion',
    'splitter',
    'max_depth',
    'min_samples_split',
    'min_samples_leaf',
    'min_weight_fraction_leaf',
    'max_features',
    'max_leaf_nodes',
    'min_impurity_decrease',
)

LINEAR_DISCRIMINANT_ANALYSIS = (
    'solver',
    'shrinkage',
    'priors',
    'n_components',
    'tol'
)

def build_model():
    pass


class Model:

    def __init__(self, model_name, model_type, params, model_id, dataset_id):
        self.model_name = model_name
        self.model_type = model_type
        self.params = params
        self.param_keys = self.params.keys()
        self.param_values = self.params.values()
        self.model_id = model_id
        self.dataset_id = dataset_id
        self.specific_model = self.create_model()

    def create_model(self):
        if self.model_type == "SVC":
            C = self.params['C']
            kernel = self.params['kernel']
            degree = self.params['degree']
            gamma = self.params['gamma']
            coef0 = self.params['coef0']
            shrinking = self.params['shrinking']
            tol = self.params['tol']
            max_iter = self.params['max_iter']
            svc = SVC(C=C, kernel=kernel, degree=degree, gamma=gamma, shrinking=shrinking, coef0=coef0,
                      tol=tol, max_iter=max_iter)
            return svc
        if self.model_type == "LR":
            penalty = self.params['penalty']
            dual = self.params['dual']
            tol = self.params['tol']
            C = self.params['C']
            fit_intercept = self.params['fit_intercept']
            intercept_scaling = self.params['intercept_scaling']
            max_iter = self.params['max_iter']
            # l1_ratio = None
            lr = LogisticRegression(penalty=penalty, dual=dual, tol=tol, C=C, fit_intercept=fit_intercept,
                                    intercept_scaling=intercept_scaling, max_iter=max_iter)
            return lr
        if self.model_type == "KNN":
            n_neighbors = self.params['n_neighbors']
            weights = self.params['weights']
            algorithm = self.params['algorithm']
            leaf_size = self.params['leaf_size']
            p = self.params['p']
            knn = KNeighborsClassifier(n_neighbors=n_neighbors, weights=weights, algorithm=algorithm,
                                       leaf_size=leaf_size, p=p)
            return knn
        if self.model_type == "LDA":
            solver = self.params['solver']
            shrinkage = self.params['shrinkage']
            n_components = self.params['n_components']
            tol = self.params['n_components']
            lda = LinearDiscriminantAnalysis(solver=solver, shrinkage=shrinkage,
                                             n_components=n_components, tol=tol)
            return lda
        if self.model_type == "DCT":
            criterion = self.params['criteron']
            splitter = self.params['splitter']
            max_depth = self.params['max_depth']
            mss = self.params['min_samples_split']
            msl = self.params['min_samples_leaf']
            mwfl = self.params['min_weight_fraction_leaf']
            mf = self.params['max_features']
            mln = self.params['max_leaf_nodes']
            mid = self.params['min_impurity_decrease']
            dct = DecisionTreeClassifier(criterion=criterion, splitter=splitter, max_depth=max_depth,
                                         min_samples_split=mss, min_samples_leaf=msl, min_weight_fraction_leaf=mwfl,
                                         max_features=mf, max_leaf_nodes=mln, min_impurity_decrease=mid)
            return dct

        def get_model_name(self):
            return self.model_name

        def get_params(self):
            return self.params

        def get_model_id():
            return self.model_id

        def get_dataset_id(self):
            return self.dataset_id

        def get_model_type(self):
            return self.model_type

        def list_params(self):
            return tuple(str(parameter) + ': ' + str(value) for parameter, value in
                         zip(self.params.keys(), self.params.values()))

        def get_specific_model(self):
            return self.specific_model

        def __str__(self):
            return f'Name: {self.get_model_name()}, Type: {self.get_model_type()}, Dataset_ID:' \
                   f' {self.get_dataset_id()}, Params: {self.list_params()}'
