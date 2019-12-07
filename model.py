from sklearn.base import BaseEstimator
from sklearn.linear_model import LogisticRegression as LR
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.tree import DecisionTreeClassifier as DTC
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn import metrics

from typing import Dict, List
import numpy as np
import jsonpickle

from aiml_dash import utils


class Model:

    def __init__(self, model_id: str, model_type: str, dataset_id: str,
                 estimator: BaseEstimator = None, classes: List = None,
                 scores: Dict = None):
        self.model_id = model_id
        self.model_type = model_type
        self.dataset_id = dataset_id
        self.estimator = estimator
        self.classes = classes
        self.scores = dict() if not scores else scores

    @property
    def params(self):
        return self.estimator.get_params()

    def __str__(self):
        """stringifies a clean and readable format of the model

            Returns:
              String version of model
            """
        return f'Name: {self.model_id}, Type: {self.model_type}, ' \
            f'Dataset_ID:{self.dataset_id}, Params: {self.params}'

    def score(self, true, predicted, feature_labels):
        """Updates self.scores property with dictionary of confusion matrix, classification report and accuracy score

            Args:
              true:
              predicted:
              feature_labels:

            """
        self.scores.update({
            'confusion matrix': metrics.confusion_matrix(true, predicted),
            'classification report': metrics.classification_report(
                true,
                predicted,
                output_dict=True,
                target_names=feature_labels),
            'accuracy': metrics.accuracy_score(true, predicted)
        })

    def train(self, features: np.ndarray, target: np.ndarray, **params):
        """Trains the respective model and updates the model_type, estimator, and calculates the score

            Args:
              features:
              target:
              **params:

            """
        enc_target = LabelEncoder().fit(target)
        self.classes = enc_target.classes_
        feat_tr, feat_te, tar_train, tar_test = train_test_split(
            features,
            enc_target.fit_transform(target),
            test_size=0.3
        )
        if self.model_type == 'logistic regression':
            self.estimator = LR(**params).fit(feat_tr, tar_train)
        if self.model_type == 'support vector classification':
            self.estimator = SVC(**params).fit(feat_tr, tar_train)
        if self.model_type == 'linear discriminant analysis':
            self.estimator = LDA(**params).fit(feat_tr, tar_train)
        if self.model_type == 'decision tree classification':
            self.estimator = DTC(**params).fit(feat_tr, tar_train)
        if self.model_type == 'k nearest neighbors':
            self.estimator = KNN(**params).fit(feat_tr, tar_train)

        self.score(tar_test, self.estimator.predict(feat_te),
                   enc_target.classes_)


def unpickle(model_json: str):
    """unpickles the object to it can be used within python code again

        Args:
          model_json:

        Returns:
          the decoded json object
        """
    return jsonpickle.decode(model_json)


def pickle(model: Model):
    """pickles to model for ease of transfer to plotly and html in a usable format

        Args:
          model:

        Returns:
          encoded json object
        """
    return jsonpickle.encode(model)
