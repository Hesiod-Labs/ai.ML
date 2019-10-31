from hypothesis import given
import hypothesis.strategies as s

from dataset.dataset import Element

element_given = s.one_of(
        s.integers(),
        s.none(),
        s.text(),
        s.floats(allow_infinity=True, allow_nan=True)
    )


@given(element_given)
def test_class_element_missing_attribute(v):
    e = Element(v)
    if v in {None, ""}:
        assert e.missing is True
    else:
        assert e.missing is False


@given(s.booleans())
def test_class_element_delete_restore_and_deleted_attribute(b):
    e = Element(deleted=b)
    assert e.deleted is b
    if b:
        e.restore()
        assert e.deleted is False
    else:
        e.delete()
        assert e.deleted is True


@given(element_given)
def test_class_element_is_numeric_and_type_property(v):
    e = Element(v)
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


@given(element_given, element_given)
def test_class_element_instance_equality(v1, v2):
    e1 = Element(v1)
    e2 = Element(v2)
    if v1 == v2:
        assert e1 == e2
    else:
        assert e1 != e2


@given(element_given, element_given)
def test_class_element_instance_comparison(v1, v2):
    e1 = Element(v1)
    e2 = Element(v2)
    if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
        if v1 >= v2:
            assert e1 >= e2
        if v1 > v2:
            assert e1 > e2
        if v1 <= v2:
            assert e1 <= e2
        if v1 < v2:
            assert e1 < e2


if __name__ == "__main__":
    test_class_element_missing_attribute()
    test_class_element_delete_restore_and_deleted_attribute()
    test_class_element_is_numeric_and_type_property()
    test_class_element_instance_equality()
    test_class_element_instance_comparison()
