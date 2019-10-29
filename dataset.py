import json
from typing import List, Dict, Union


def _create_dataset(data: json):

    d = json.loads(data)

    return {
        l: Feature(l, [Element(o, False) for o in obs]) for l, obs in d.items()
        }


class Element():

    def __init__(self, value: Union[str, int, float], deleted=False):
        self.value = value
        self.deleted = deleted

    def is_numeric(self) -> bool:
        if isinstance(self.value, str):
            return str.isnumeric(self.value)
        else:
            return True

    def __repr__(self):
        name = self.__class__.__name__
        v = self.value
        d = self.deleted
        return f'{name}(value={v}, deleted={d})'

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


class Feature():

    def __init__(self, label: str, elements: List[Element]):
        self.label = label
        self.elements = elements

    def __repr__(self):
        name = self.__class__.__name__
        l = self.label
        n = len(self.elements)
        t = 'numerical' if self.is_numeric() else 'categorical'
        return f'{name}(label="{l}", n_elements={n}, type={t})'

    def __eq__(self, f):
        if isinstance(f, self.__class__):
            if self.n_elements == f.n_elements:
                return all(
                    [so == fo for so, fo in zip(self.elements, f.elements)]
                    )
        else:
            return False

    def n_elements(self) -> int:
        return len(self.elements)

    def is_numeric(self) -> bool:
        return all([o.is_numeric() for o in self.elements])


class Dataset():

    def __init__(self, dataset_id: str, data: json, **metadata):
        self.dataset_id = dataset_id
        self.metadata = metadata
        self.features = _create_dataset(data)

    def __repr__(self):
        name = self.__class__.__name__
        ds_id = self.dataset_id
        n = self.n_features()
        return f'{name}(id={ds_id}, n_features={n})'

    def n_features(self) -> int:
        return len(self.features.keys())

    def n_elements(self, feature: str) -> int:
        return self.features[feature].n_elements()

    def is_numeric(self, feature: str) -> bool:
        return self.features[feature].is_numeric()
