from nytimes_api.helpers import flatten_dict

def test_empty_dict():
    test_dict = {}
    assert len(flatten_dict(test_dict)) == 0
    assert flatten_dict(test_dict) == {}

def test_value_dict():
    test_dict = {"key1": "value1"}
    assert len(flatten_dict(test_dict)) == 1
    assert flatten_dict(test_dict) == {"key1": "value1"}


def test_simple_dict():
    test_dict = {"key1": {"key2": "value1"}}
    assert len(flatten_dict(test_dict)) == 1
    assert flatten_dict(test_dict) == {"key1.key2": "value1"}


def test_nested_dict():
    test_dict = {"key1": {"key2": "value1", "key3": {"key4": "value2"}}}
    assert len(flatten_dict(test_dict)) == 2
    assert flatten_dict(test_dict) == {"key1.key2": "value1", "key1.key3.key4": "value2"}


def test_list_of_dicts():
    test_dict = {"key1": [{"key2": "value1"}, {"key3": "value2"}]}
    assert len(flatten_dict(test_dict)) == 2
    assert flatten_dict(test_dict) == {"key1.0.key2": "value1", "key1.1.key3": "value2"}


def test_list_of_values():
    test_dict = {"key1": ["value1", "value2"]}
    assert len(flatten_dict(test_dict)) == 2
    assert flatten_dict(test_dict) == {"key1.0": "value1", "key1.1": "value2"}


def test_list_of_values_and_dicts():
    test_dict = {"key1": ["value1", {"key2": "value2"}]}
    assert len(flatten_dict(test_dict)) == 2
    assert flatten_dict(test_dict) == {"key1.0": "value1", "key1.1.key2": "value2"}


def test_list_of_lists():
    test_dict = {"key1": [["value1", "value2"], ["value3", "value4"]]}
    assert len(flatten_dict(test_dict)) == 4
    assert flatten_dict(test_dict) == {
        "key1.0.0": "value1",
        "key1.0.1": "value2",
        "key1.1.0": "value3",
        "key1.1.1": "value4",
    }


def test_complex_dict():
    test_dict = {
        "key1": {
            "key2": "value1",
        },
        "key3": ["value2", "value3"],
        "key4": {"key5": "value4", "key6": ["value5", "value6"]},
    }
    assert len(flatten_dict(test_dict)) == 6
    assert flatten_dict(test_dict) == {
        "key1.key2": "value1",
        "key3.0": "value2",
        "key3.1": "value3",
        "key4.key5": "value4",
        "key4.key6.0": "value5",
        "key4.key6.1": "value6",
    }

def test_flatten_dict():
    # Simple test case
    nested_dict = {"a": {"b": 1, "c": 2}, "d": 3}
    flattened = flatten_dict(nested_dict)
    assert flattened == {"a.b": 1, "a.c": 2, "d": 3}
    
    # Test with nested arrays
    nested_dict = {"a": [1, 2, 3], "b": {"c": [4, 5]}}
    flattened = flatten_dict(nested_dict)
    assert flattened == {"a.0": 1, "a.1": 2, "a.2": 3, "b.c.0": 4, "b.c.1": 5}
