from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import SVC
import jsonpickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn import metrics
from sklearn.datasets import load_iris
# - Raise errors if there is bad data
# - Return numpy array? Or just add it into it yourself
# - Accuracy scores and metrics from confusion matrix etc, score and loss
# - Look into what grid search csv does
# - Cross validation strategies


class Model:
    LDA = 'LDA'
    DTC = 'DTC'
    SVC = 'SVC'
    KNN = 'KNN'
    LGR = 'LGR'

    def __init__(self, model_name, model_id, model_type, dataset_id, X,
                 y, params):
        self.model_name = model_name
        self.model_type = model_type
        self.params = params
        self.model_id = model_id
        self.dataset_id = dataset_id
        self.X = X
        self.y = y
        self.model = self.create_model()
        self.results = None

    def linear_discriminant_analysis(self):
        return LinearDiscriminantAnalysis(
            solver=self.params['solver'],
            shrinkage=self.params['shrinkage'],
            n_components=self.params[
                'n_components'],
            tol=self.params['tol']
        )

    def support_vector_classification(self):
        return SVC(
            C=self.params['C'],
            kernel=self.params['kernel'],
            degree=self.params['degree'],
            gamma=self.params['gamma'],
            coef0=self.params['coef0'],
            shrinking=self.params['shrinking'],
            tol=self.params['tol'],
            max_iter=self.params['max_iter']
        )

    def decision_tree_classification(self):
        return DecisionTreeClassifier(
            criterion=self.params['criterion'],
            splitter=self.params['splitter'],
            max_depth=self.params['max_depth'],
            min_samples_split=self.params[
                'min_samples_split'],
            min_samples_leaf=self.params[
                'min_samples_leaf'],
            min_weight_fraction_leaf=self.params[
                'min_weight_fraction_leaf'],
            max_features=self.params['max_features'],
            max_leaf_nodes=self.params[
                'max_leaf_nodes'],
            min_impurity_decrease=self.params[
                'min_impurity_decrease'])

    def k_nearest_neighbors(self):
        return KNeighborsClassifier(
            n_neighbors=self.params['n_neighbors'],
            weights=self.params['weights'],
            algorithm=self.params['algorithm'],
            leaf_size=self.params['leaf_size'],
            p=self.params['p'])

    def logistic_regression(self):
        return LogisticRegression(
            penalty=self.params['penalty'],
            dual=self.params['dual'],
            tol=self.params['tol'],
            C=self.params['C'],
            fit_intercept=self.params['fit_intercept'],
            intercept_scaling=self.params[
                'intercept_scaling'],
            l1_ratio=self.params['l1_ratio'],
            max_iter=self.params['max_iter'])

    def create_model(self):
        if self.model_type == Model.LDA:
            return self.linear_discriminant_analysis()
        if self.model_type == Model.DTC:
            return self.decision_tree_classification()
        if self.model_type == Model.KNN:
            return self.k_nearest_neighbors()
        if self.model_type == Model.LGR:
            return self.logistic_regression()
        if self.model_type == Model.SVC:
            return self.support_vector_classification()

    def get_model_name(self):
        return self.model_name

    def get_params(self):
        return self.params

    def get_model_id(self):
        return self.model_id

    def get_dataset_id(self):
        return self.dataset_id

    def get_model_type(self):
        return self.model_type

    def list_params(self):
        return tuple(str(parameter) + ': ' + str(value) for parameter, value in
                     zip(self.params.keys(), self.params.values()))

    def get_model(self):
        return self.model

    def __str__(self):
        return f'Name: {self.get_model_name()}, Type: {self.get_model_type()}, Dataset_ID:' \
            f' {self.get_dataset_id()}, Params: {self.list_params()}'

    def train(self):
        # after the model is fit to some data
        X = load_iris().data
        y = load_iris().target
        #oh_enc = OneHotEncoder(categories='auto')
        #label_enc = LabelEncoder().fit_transform(self.y)
        #oh_enc.fit_transform(X, y)
       # y = oh_enc.fit_transform(oh_enc).toarray()
        X_train, y_train, X_test, y_test = train_test_split(
            X, y, test_size=0.3)
        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)
        conf_matrix = metrics.confusion_matrix(y_test, predictions)
        acc_score = metrics.accuracy_score(y_test, predictions)
        class_report = metrics.classification_report(y_test, predictions)
        self.results = {
            'Confusion Matrix': conf_matrix,
            'Accuracy Score': acc_score,
            'Classification Report': class_report
        }

    def picklize(self):
        return jsonpickle.encode(self.model)

    @staticmethod
    def depickleize(model_json):
        return jsonpickle.decode(model_json)