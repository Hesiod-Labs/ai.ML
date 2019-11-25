import uuid
from typing import List, Union
import numpy as np
import pandas as pd
import math


# need pandas seires objects passed in, too complicated with objects

def ratio(numerator, denominator):
    return numerator / denominator


# takes in a list of only boolean columns
def count_boolean(series_list):
    rows = len(series_list[0])
    new_column = np.empty(rows, dtype=int)
    counter = 0
    while counter < rows:
        total = 0
        for series in series_list:
            total += series[counter]
        new_column[counter] = total
        counter += 1
    return new_column


def absolute_value(series):
    new_column = np.empty(len(series), dtype=float)
    counter = 0
    for entry in series:
        new_column[counter] = abs(entry)
        counter += 1
    return new_column


def squared(series):
    new_column = np.empty(len(series), dtype=float)
    counter = 0
    for entry in series:
        new_column[counter] = math.pow(entry, 2)
        counter += 1
    return new_column


def z_score(series):
    new_column = np.empty(len(series), dtype=float)
    counter = 0
    mean = series.mean()
    std = series.std()
    for entry in series:
        new_column[counter] = (entry - mean) / std
        counter += 1
    return new_column


def sin(series):
    new_column = np.empty(len(series), dtype=float)
    counter = 0
    for entry in series:
        new_column[counter] = math.sin(entry)
        counter += 1
    return new_column


def cos(series):
    new_column = np.empty(len(series), dtype=float)
    counter = 0
    for entry in series:
        new_column[counter] = math.cos(entry)
        counter += 1
    return new_column


class Element:
    def __init__(
            self,
            value: Union[str, int, float],
            deleted=False
    ):
        self.value = value
        self.deleted = deleted

    # TODO Unclear if categories are represented with dummy variables
    @property
    def type(self) -> str:
        return "numerical" if self.is_numeric() else "categorical"

    @property
    def missing(self) -> bool:
        return self.value == ""

    def delete(self):
        self.deleted = True

    def restore(self):
        self.deleted = False

    def is_numeric(self) -> bool:
        if isinstance(self.value, str):
            return str.isnumeric(self.value)
        elif isinstance(self.value, (int, float)):
            return True
        else:
            return False

    def __repr__(self):
        name = self.__class__.__name__
        v = self.value
        t = self.type
        d = self.deleted
        m = self.missing
        return f"{name}(value={v}, type={t}, missing={m}, deleted={d})"

    def __eq__(self, e):
        if self.__class__ == e.__class__:
            return self.value == e.value
        else:
            return False

    def __gt__(self, e):
        return self.value > e.value

    def __lt__(self, e):
        return self.value < e.value

    def __ge__(self, e):
        return self.value >= e.value

    def __le__(self, e):
        return self.value <= e.value


# TODO Add is_target attribute. Allows for both supervised and unsupervised
#   learning since no target indicates unsupervised.
class Feature:
    def __init__(
            self,
            elements: List[Element] = None,
            label: str = "",
            feature_id: str = None,
            deleted: bool = False,
            is_target: bool = False
    ):
        if not elements:
            elements = []
        self.elements = elements
        self.label = label
        self.feature_id = str(uuid.uuid4()) if not feature_id else feature_id
        self.deleted = deleted
        self.is_target = is_target

    @property
    def type(self) -> str:
        return "numerical" if self.is_numeric() else "categorical"

    @property
    def values(self) -> List:
        return [e.value for e in self.elements]

    def rename(self, new_name: str):
        self.label = new_name

    def add(self, e: Element):
        if e.type == self.type:
            self.elements.append(e)
        else:
            raise TypeError("Element must be the same type as the feature.")

    def remove(self, e: Element):
        try:
            self.elements.remove(e)
        except ValueError:
            print("Element not found in feature.")

    def delete(self):
        self.deleted = True

    def restore(self):
        self.deleted = False

    def update(self, e_old: Element, e_new: Element):
        try:
            self.elements[self.elements.index(e_old)] = e_new
        except ValueError:
            print("Element not found in feature.")

    def count(self, e) -> int:
        return self.elements.count(Element(e))

    def n_elements(self) -> int:
        return len(self.elements)

    def is_numeric(self) -> bool:
        return all([o.is_numeric() for o in self.elements])

    def unique_elements(self):
        series = pd.DataFrame(self.values)
        return list(series.unique())

    def value_counts(self):
        series = pd.DataFrame(self.values)
        return dict(series.value_counts())

    def series_describe(self):
        series = pd.DataFrame(self.values)
        return series.describe()

    # TODO Possibly use UUIDs instead for Dataset identifier.
    def __repr__(self):
        name = self.__class__.__name__
        l = self.label
        i = self.feature_id
        n = len(self.elements)
        t = "numerical" if self.is_numeric() else "categorical"
        d = self.deleted
        return f'{name}(' \
            f'label="{l}", id={i}, n_elements={n}, type={t}, deleted={d})'

    def __eq__(self, f):
        if self.__class__ == f.__class__:
            if self.n_elements() == f.n_elements():
                comps = [so == fo for so, fo in zip(self.elements, f.elements)]
                return all(comps)
        else:
            return False


class Dataset:
    def __init__(
            self,
            features: List[Feature] = None,
            dataset_id: str = "",
            **metadata
    ):
        self.dataset_id = dataset_id
        if not features:
            features = []
        self.features = {f.feature_id: f for f in features}
        self.metadata = metadata

    @property
    def values(self):
        return {
            k: [e.value for e in f.elements] for k, f in self.features.items()
        }

    @property
    def shape(self):
        rows = max([f.n_elements() for f in self.features.values()])
        cols = self.n_features()
        return rows, cols

    def rename_feature(self, f: Feature, new_name: str):
        try:
            self.features[f.feature_id].rename(new_name)
        except KeyError:
            print("Feature does not exist in the dataset.")

    def rename_dataset(self, new_name: str):
        self.dataset_id = new_name

    # TODO Use Feature.add()
    def add(self, f: Feature):
        if f.values not in self.values.values():
            self.features[f.feature_id] = f
        else:
            raise ValueError(
                "Feature already exists in the dataset. Adding"
                " it will overwrite any modifications made to"
                " the feature elements."
            )

    def delete(self, f: Feature):
        self.features[f.feature_id].delete()

    def restore(self, f: Feature):
        self.features[id(f)].restore()

    def get_feature(self, f: Feature):
        try:
            return self.features[f.feature_id]
        except ValueError:
            print('Feature does not exist in the dataset.')

    def n_features(self) -> int:
        n_deleted = len([f for f in self.features.values() if f.deleted])
        return len(self.features.keys()) - n_deleted

    def n_numerical(self):
        return len([f.is_numeric() for f in self.features.values()])

    def n_categorical(self):
        return self.n_features() - self.n_numerical()

    def n_elements(self, f: Feature) -> int:
        return self.features[id(f)].n_elements()

    def is_numeric(self, f: Feature) -> bool:
        return self.features[id(f)].is_numeric()

    def head(self):
        df = pd.DataFrame(self.features)
        return df.head()

    def tail(self):
        df = pd.DataFrame(self.features)
        return df.tail()

    def sum_isnull(self):
        df = pd.DataFrame(self.features)
        return df.isnull().sum()

    def df_describe(self):
        df = pd.DataFrame(self.features)
        return df.describe()

    def __repr__(self):
        name = self.__class__.__name__
        ds_id = self.dataset_id
        n = self.n_features()
        return f"{name}(id={ds_id}, n_features={n})"
