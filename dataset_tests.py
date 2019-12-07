import numpy as np

from hypothesis import given, example
import hypothesis.strategies as s

from dataset.dataset import Element, Feature

element = [
    s.one_of(
        s.integers(),
        s.none(),
        s.text(),
        s.floats(allow_infinity=True, allow_nan=True)
    ),
    s.booleans()
]

two_elements = element * 2

feature = [s.lists(s.tuples(*element)), s.text(), s.booleans()]

two_features = feature * 2


def generate_test_element(value, deleted):
    return Element(value=value, deleted=deleted)


def generate_test_feature(elements, label, deleted):
    e_list = [generate_test_element(e[0], e[1]) for e in elements]
    return Feature(elements=e_list, label=label, deleted=deleted)


@given(*element)
def test_class_element_missing_attribute(v, d):
    e = generate_test_element(value=v, deleted=d)
    if v == "":
        assert e.missing is True
    else:
        assert e.missing is False


@given(*element)
def test_class_element_delete_restore_and_deleted_attribute(v, d):
    e = generate_test_element(value=v, deleted=d)
    assert e.deleted is d
    if d:
        e.restore()
        assert e.deleted is False
    else:
        e.delete()
        assert e.deleted is True


@given(*element)
def test_class_element_is_numeric_and_type_property(v, d):
    e = generate_test_element(value=v, deleted=d)
    if isinstance(v, str):
        if v.isnumeric():
            assert e.is_numeric() is True
            assert e.type == "numerical"
        else:
            assert e.is_numeric() is False
            assert e.type == "categorical"
    elif isinstance(v, (int, float)):
        assert e.is_numeric() is True
        assert e.type == "numerical"
    else:
        assert e.is_numeric() is False
        assert e.type == "categorical"


@given(*two_elements)
@example(None, False, '', False)
def test_class_element_equality(v1, d1, v2, d2):
    e1 = generate_test_element(value=v1, deleted=d1)
    e2 = generate_test_element(value=v2, deleted=d2)
    assert e1 == e2 if v1 == v2 else e1 != e2


@given(*two_elements)
def test_class_element_instance_comparison(v1, d1, v2, d2):
    e1 = generate_test_element(value=v1, deleted=d1)
    e2 = generate_test_element(value=v2, deleted=d2)
    if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
        if v1 >= v2:
            assert e1 >= e2
        if v1 > v2:
            assert e1 > e2
        if v1 <= v2:
            assert e1 <= e2
        if v1 < v2:
            assert e1 < e2
    else:
        assert ValueError


@given(*feature)
def test_class_feature_is_numeric_and_type_property(e_list, l, d):
    f = generate_test_feature(elements=e_list, label=l, deleted=d)
    if all([e.is_numeric() for e in f.elements]):
        assert f.is_numeric() is True
        assert f.type == "numerical"
    else:
        assert f.is_numeric() is False
        assert f.type == "categorical"


@given(*feature)
def test_class_feature_deleted_attribute(e_list, l, d):
    f = generate_test_feature(elements=e_list, label=l, deleted=d)
    if d:
        assert f.deleted is True
    else:
        assert f.deleted is False


@given(*feature)
def test_class_feature_values_property(e_list, l, d):
    f = generate_test_feature(elements=e_list, label=l, deleted=d)
    assert all(v is e[0] for v, e in zip(f.values, e_list))


@given(*feature)
def test_class_feature_delete_restore_and_deleted_attribute(e_list, l, d):
    f = generate_test_feature(elements=e_list, label=l, deleted=d)
    assert f.deleted is d
    if d:
        f.restore()
        assert f.deleted is False
    else:
        f.delete()
        assert f.deleted is True


@given(*two_features)
def test_class_feature_equality(e1, l1, d1, e2, l2, d2):
    f1 = generate_test_feature(elements=e1, label=l1, deleted=d1)
    f2 = generate_test_feature(elements=e2, label=l2, deleted=d2)
    f1_values = [e[0] for e in e1]
    f2_values = [e[0] for e in e2]
    if len(f1_values) == len(f2_values):
        if all([v1 == v2 for v1, v2 in zip(f1_values, f2_values)]):
            assert f1 == f2
    else:
        assert f1 != f2


@given(*feature)
def test_class_feature_remove(e_list, l, d):
    f = Feature(elements=e_list, label=l, deleted=d)
    if e_list:
        i = np.random.randint(0, len(e_list))
        e_in_f = Element(value=e_list[i][0], deleted=e_list[i][1])
        if e_in_f in f.elements:
            assert e_in_f not in f.remove(e_in_f)
        else:
            assert ValueError


if __name__ == "__main__":
    test_class_element_equality()
    test_class_element_missing_attribute()
    test_class_feature_delete_restore_and_deleted_attribute()
    test_class_element_is_numeric_and_type_property()
    test_class_element_instance_comparison()
    test_class_feature_is_numeric_and_type_property()
    test_class_feature_deleted_attribute()
    test_class_feature_values_property()
    test_class_feature_equality()
    test_class_feature_remove()