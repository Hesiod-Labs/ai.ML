import numpy as np
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn.metrics import accuracy_score
import argparse


class Model(object):
    """
    Args:
    dataset: Dictionary of the data used by the algorithm to build the model.
        Structured as {'predictor' [predictor data]}.
    predictors: List of strings that are in the dataset and used as features
        of the model.
    outcomes: List of strings that are in the dataset and used as outcomes of
        the model.
    params: Dictionary of model parameters determined during the training and
        testing phases.
    objective: String of what type of learning the model is
    performing: regression or classification.
    hyperparams: Dictionary of model hyperparameters that defines the nature
        of the model. Structured as {'hyperparameter': value}.
    preprocessing: List of preprocessing techniques applied to the data
        before building the model.
    function: String of the objective function optimized during the model
        training and testing phases.
    created_on: Datetime of when the model was first created. Generated at
        the conclusion of training.
    last_edited: Datetime of when the model was last edited, including
        changing of parameters, hyperparameters, or preprocessing aspects.
    """

    def __init__(self, dataset, params, predictors, hyperparams,
                 objective, preprocessing, function, created_on,
                 last_edited, **kwargs):
        self.dataset = dataset
        self.predictors = predictors
        self.outcomes = outcomes
        self.params = params
        self.hyperparams = hyperparams
        self.objective = objective
        self.preprocessing = preprocessing
        self.function = function
        self.created_on = created_on
        self.last_edited = last_edited
        self.__dict__ = kwargs

    def predict(self, new_data):
        """Given new data, predict the value(s) or class(es) of the data.
        """

    def _validate_new_data(self, new_data):
        pass

    def retrain(self, preprocess=None, hyperparams=None, parameters=None):
        pass


def iris():
    iris_data = datasets.load_iris()
    x = iris_data.data
    y = iris_data.target
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.5)
    classifier = tree.DecisionTreeClassifier()
    classifier.fit(x_train, y_train)
    predictions = classifier.predict(x_test)
    print(accuracy_score(y_test, predictions))
