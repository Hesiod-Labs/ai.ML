import uuid
from typing import List, Union


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
        """rename an feature with a new name

            Args:
              new_name: string of a new feature name
            """
        self.label = new_name

    def add(self, e: Element):
        """adds an element to a feature

            Args:
              e: element to be added

            Raises:
              TypeError: element is not the same type as the feature
            """
        if e.type == self.type:
            self.elements.append(e)
        else:
            raise TypeError("Element must be the same type as the feature.")

    def remove(self, e: Element):
        """removes an element from a feature

            Args:
              e: the element to be removed

            Raises:
              ValueError: element not found in the feature
            """
        try:
            self.elements.remove(e)
        except ValueError:
            print("Element not found in feature.")

    def delete(self):
        """deletes the element from the feature
            """
        self.deleted = True

    def restore(self):
        """brings back the element to show the user
            """
        self.deleted = False

    def update(self, e_old: Element, e_new: Element):
        """replaces an old element with a new element

            Args:
              e_old: old element object
              e_new: replacement element object

            Raises:
              ValueError: The element is not in the feature
            """
        try:
            self.elements[self.elements.index(e_old)] = e_new
        except ValueError:
            print("Element not found in feature.")

    def count(self, e) -> int:
        """counts the number of a specific element in a feature

            Args:
              e: the element to be counted

            Returns:
              the number of elements that match the input element
            """
        return self.elements.count(Element(e))

    def n_elements(self) -> int:
        """counts the number of elements in a feature

            Returns:
              int denoting the number of elements
            """
        return len(self.elements)

    def is_numeric(self) -> bool:
        """determines if the feature contains numeric data

            Returns:
              a boolean denoting whether or not the contents of the feature are numeric
            """
        return all([o.is_numeric() for o in self.elements])

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
        """renames a feature

            Args:
              f: the feature to be renamed
              new_name: the string encompassing the new name to be changed

            Raises:
              KeyError: if the feature is not in this dataset
            """
        try:
            self.features[f.feature_id].rename(new_name)
        except KeyError:
            print("Feature does not exist in the dataset.")

    def rename_dataset(self, new_name: str):
        """changes the name of a dataset object

            Args:
              new_name: string denoting the name of the dataset to be changed to
            """
        self.dataset_id = new_name

    # TODO Use Feature.add()
    def add(self, f: Feature):
        """adds a new feature to the current dataset object list of features

            Args:
              f: the feature to be added

            Raises:
              ValueError: If the feature already exists
            """
        if f.values not in self.values.values():
            self.features[f.feature_id] = f
        else:
            raise ValueError(
                "Feature already exists in the dataset. Adding"
                " it will overwrite any modifications made to"
                " the feature elements."
            )

    def delete(self, f: Feature):
        """removes a feature as designated by a user via the interface

            Args:
              f: feature to be deleted
            """
        self.features[f.feature_id].delete()

    def restore(self, f: Feature):
        """makes a feature previously marked deleted by the user now available again

            Args:
              f: the feature which to bring back
            """
        self.features[id(f)].restore()

    def get_feature(self, f: Feature):
        """gets a feature object from an encapsulated dataset object

            Args:
              f: the feature needed to be returned

            Returns:
              the feature object assuming it does exist and is present

            Raises:
              ValueError: when the feature does not exist or is not present
            """
        try:
            return self.features[f.feature_id]
        except ValueError:
            print('Feature does not exist in the dataset.')

    def n_features(self) -> int:
        """calculates the number of features in total that are not deleted

            Returns:
              int denoting how many non-deleted features there are
            """
        n_deleted = len([f for f in self.features.values() if f.deleted])
        return len(self.features.keys()) - n_deleted

    def n_numerical(self):
        """determines how many numerical features there are in all features

            Returns:
              an int denoting how many features are numeric
            """
        return len([f.is_numeric() for f in self.features.values()])

    def n_categorical(self):
        """determines how many categorical entries are in the dataset

            Returns:
              an int representing the number of features that are categorical
            """
        return self.n_features() - self.n_numerical()

    def n_elements(self, f: Feature) -> int:
        """assesses how many elements are in a feature

            Args:
              f: feature denoting a series to be counted

            Returns:
              an int representing the number of elements in a feature
            """
        return self.features[id(f)].n_elements()

    def is_numeric(self, f: Feature) -> bool:
        """determines if a given feature of a dataset object is numeric

            Args:
              f: the feature denoting a series to be checked as numeric

            Returns:
              true if the feature is numerical and false otherwise
            """
        return self.features[id(f)].is_numeric()

    def __repr__(self):
        name = self.__class__.__name__
        ds_id = self.dataset_id
        n = self.n_features()
        return f"{name}(id={ds_id}, n_features={n})"
