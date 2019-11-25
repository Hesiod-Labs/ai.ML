from model.model import *


svc_params = {'C': 1.0, 'kernel': 'rbf', 'degree': 3, 'gamma': 'auto', 'coef0': 0.0,
              'shrinking': True, 'tol': 0.001, 'max_iter': 1}
svc = Model('SVC Model', 'SVC', svc_params, '1', '1')


def test_create_model():
    assert isinstance(svc, Model)
    lr_params = {'penalty': 'l2', 'dual': False, 'tol': 0.001, 'C': 1.0, 'fit_intercept': True,
                 'intercept_scaling': 1, 'max_iter': 100}
    lr = Model('LR Model', 'LR', lr_params, '2', '2')
    assert isinstance(lr, Model)
    knn_params = {'n_neighbors': 5, 'weights': 'uniform', 'algorithm': 'auto', 'leaf_size': 30, 'p': 2}
    knn = Model('KNN Model', 'KNN', knn_params, '3', '3')
    assert isinstance(knn, Model)
    lda_params = {'solver': 'svd', 'shrinkage': None, 'n_components': None, 'tol': 0.01}
    lda = Model('LDA Model', 'LDA', lda_params, '4', '4')
    assert isinstance(lda, Model)
    dct_params = {'criterion': 'gini', 'splitter': 'best', 'max_depth': None, 'min_samples_split': 2,
                  'min_samples_leaf': 1, 'min_weight_fraction_leaf': 0.0, 'max_features': None,
                  'max_leaf_nodes': None, 'min_impurity_decrease': 0.0}
    dct = Model('DCT Model', 'DCT', dct_params, '5', '5')
    assert isinstance(dct, Model)


def test_get_model_name():
    assert svc.get_model_name() is svc.model_name


def test_get_params():
    assert svc.get_params() is svc.params


def test_get_model_id():
    assert svc.get_model_id() is svc.model_id


def test_get_dataset_id():
    assert svc.get_dataset_id() is svc.dataset_id


def test_get_model_type():
    assert svc.get_model_type() is svc.model_type


def test_list_params():
    assert svc.list_params() == tuple(str(parameter) + ': ' + str(value) for parameter, value in zip(svc.params.keys(), svc.params.values()))


def test_get_specific_model():
    assert svc.get_model() is svc.model


def test__str__():
    assert str(svc) == f'Name: {svc.get_model_name()}, Type: {svc.get_model_type()}, Dataset_ID:' \
        f' {svc.get_dataset_id()}, Params: {svc.list_params()}'


if __name__ == '__main__':
    test_create_model()
    test_get_model_name()
    test_get_params()
    test_get_model_id()
    test_get_dataset_id()
    test_get_model_type()
    test_get_model_type()
    test_list_params()
    test_get_specific_model()
    test__str__()
