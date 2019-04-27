from collections import ChainMap
from collections.abc import Mapping
import copy
import pickle

import pytest

from praw.util import AttributeContainer


class TestAttributeContainer:
    def test_init(self):
        assert issubclass(AttributeContainer, Mapping)

        mydict = {"a": 1, "b": 2}
        ac = AttributeContainer(mydict)
        assert ac.a == 1
        assert ac["a"] == 1
        assert abs(ac) is mydict
        assert callable(ac.get)

    def test_repr(self):
        def assert_dict_repr(mydict, items):
            dict_repr = repr(mydict)
            if not dict_repr.startswith(
                type(mydict).__name__ + "({"
            ) or not dict_repr.endswith("})"):
                return False

            str_items = ("%r: %r" % (k, v) for k, v in items)
            return all(item in dict_repr for item in str_items)

        assert repr(AttributeContainer({})) == "AttributeContainer({})"
        assert (
            repr(AttributeContainer({"a": 1}))
            == "AttributeContainer({'a': 1})"
        )
        cm = ChainMap({"a": 1, "b": 2}, {"b": 20, "c": 30})
        assert assert_dict_repr(
            AttributeContainer(cm), dict(a=1, b=2, c=30).items()
        )

    def test_str(self):
        # For code coverage.
        # The str needs to be long enough for `_pprint_attribute_container()`
        # to automatically be invoked.
        str(AttributeContainer({chr(i): i for i in range(97, 97 + 26)}))

    def test_iter(self):
        found = set()
        for key in AttributeContainer({"a": 1, "b": 2, "c": 3}):
            found.add(key)
        assert found == {"a", "b", "c"}

    def test_len(self):
        ac = AttributeContainer({"a": 1, "b": 2, "c": 3})
        assert len(ac) == 3
        assert len(abs(ac)) == 3
        assert len(ac.keys()) == 3

    def test_abs(self):
        mydict = {"key": "value"}
        ac = AttributeContainer(mydict)
        mydict["key2"] = "value2"
        assert "key2" in ac
        assert ac["key2"] == "value2"
        assert abs(ac) is mydict

    def test_dir(self):
        ac = AttributeContainer({"a": 1, "b": 2, "c": 3})
        assert dir(ac) == sorted(ac)

    def test_getitem(self):
        ac = AttributeContainer({"a": 1, "b": {"bb": 3}})
        assert ac["a"] == 1
        assert type(ac["b"]) is dict
        assert ac["b"]["bb"] == 3

        with pytest.raises(KeyError):
            ac["z"]

    def test_getattr(self):
        ac = AttributeContainer({"a": 1, "b": {"bb": 3}})
        assert ac.a == 1

        with pytest.raises(AttributeError):
            ac.z

        with pytest.raises(AttributeError):
            ac["b"].bb

        assert type(ac.b) is AttributeContainer
        assert ac.b == {"bb": 3}

    def test_noclobber(self):
        ac = AttributeContainer({"get": 1})

        with pytest.raises(AttributeError):
            ac.get = 1

        assert ac["get"] == 1

    def test_pickle(self):
        mydict = {
            "a": 1,
            "b": {"aa": {"aaa": 6, "bbb": [1, 2, 3]}},
            "c": [1, "asdf", set([1, 2])],
        }
        ac = AttributeContainer(mydict)
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(ac, protocol=level))
            assert ac == other

    def test_copyability(self):
        ac = AttributeContainer({0: 0})

        # Test shallow copy
        ac1 = copy.copy(ac)
        # Check for exceptions
        repr(ac1)
        ac1[0]
        with pytest.raises(KeyError):
            ac1[1]

        assert abs(ac1) is abs(ac)

        # Test deep copy
        ac2 = copy.deepcopy(ac)
        # Check for exceptions
        repr(ac2)
        ac2[0]
        with pytest.raises(KeyError):
            ac2[1]

        assert abs(ac2) is not abs(ac)
        assert abs(ac2) == abs(ac)

        ac2_dict = abs(ac2)
        ac2_dict[20] = 40
        assert ac2[20] == 40
        assert 20 in dict(ac2)

    def test_callable(self):
        data = {0: 0}
        ac = AttributeContainer(data)
        assert ac[0] == 0
        with pytest.raises(KeyError):
            ac[1]

        data = {0: 0}

        def callback(name):
            data[1] = 1

        ac = AttributeContainer(data, callback)
        assert ac[0] == 0
        with pytest.raises(KeyError):
            ac[1]

        data = {0: 0}

        def callback(name):
            data[1] = 1
            return True

        ac = AttributeContainer(data, callback)
        assert ac[0] == 0
        assert ac[1] == 1
        with pytest.raises(KeyError):
            ac[2]
