import json
from typing import Dict, List, Union


class Element:
    def __init__(self, value: Union[str, int, float] = None, deleted=False):
        self.value = value
        self.deleted = deleted

    @property
    def type(self) -> str:
        return "numerical" if self.is_numeric() else "categorical"

    @property
    def missing(self) -> bool:
        return self.value in {None, ""}

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
        if isinstance(e, self.__class__):
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


class Feature:
    def __init__(self, elements: List[Element] = None, label: str = "", deleted=False):
        if not elements:
            elements = []
        self.elements = elements
        self.label = label
        self.deleted = deleted

    @property
    def type(self) -> str:
        if all([e.is_numeric() for e in self.elements]):
            return "numerical"
        else:
            return "categorical"

    @property
    def values(self) -> List:
        return [e.value for e in self.elements]

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

    def count(self, e):
        return self.elements.count(Element(e))

    def n_elements(self) -> int:
        return len(self.elements)

    def is_numeric(self) -> bool:
        return all([o.is_numeric() for o in self.elements])

    def __repr__(self):
        name = self.__class__.__name__
        l = self.label
        i = id(self)
        n = len(self.elements)
        t = "numerical" if self.is_numeric() else "categorical"
        d = self.deleted
        return f'{name}(label="{l}", id={i}, n_elements={n}, type={t}, deleted={d})'

    def __eq__(self, f):
        if isinstance(f, self.__class__):
            if self.n_elements() == f.n_elements():
                comps = [so == fo for so, fo in zip(self.elements, f.elements)]
                return all(comps)
        else:
            return False


class Dataset:
    def __init__(
        self, features: List[Feature] = None, dataset_id: str = "", **metadata
    ):
        self.dataset_id = dataset_id
        if not features:
            features = []
        self.features = {id(f): f for f in features}
        self.metadata = metadata

    @property
    def values(self):
        return {k: [e.value for e in f.elements] for k, f in self.features.items()}

    @property
    def shape(self):
        rows = max([f.n_elements() for f in self.features.values()])
        cols = self.n_features()
        return (rows, cols)

    def add(self, f: Feature):
        if f.values not in self.values.values():
            self.features[id(f)] = f
        else:
            raise ValueError(
                "Feature already exists in the dataset. Adding"
                " it will overwrite any modifications made to"
                " the feature elements."
            )

    def delete(self, f: Feature):
        self.features[id(f)].delete()

    def restore(self, f: Feature):
        self.features[id(f)].restore()

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

    def __repr__(self):
        name = self.__class__.__name__
        ds_id = self.dataset_id
        n = self.n_features()
        return f"{name}(id={ds_id}, n_features={n})"
