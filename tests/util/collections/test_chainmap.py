from collections.abc import MutableMapping
import copy
import pickle

import pytest

from praw.util import ChainMap, ScopeChainMap


class TestChainMap:
    def test_init(self):
        assert issubclass(ChainMap, MutableMapping)

        d0 = {0: 0}
        d1 = {1: 1}
        d2 = {2: 2}
        cm = ChainMap(d0, d1, d2)
        assert cm.maps[0] is d0
        assert cm.maps[1] is d1
        assert cm.maps[2] is d2

        cm = ChainMap()
        assert cm == {}
        cm["a"] = 1
        cm["b"] = 2
        assert cm == {"a": 1, "b": 2}

    def test_len(self):
        assert len(ChainMap()) == 0
        cm = ChainMap(
            {"a": 1, "b": 2}, {"b": 20, "c": 30}, {"c": 300, "d": 400}
        )
        assert len(cm) == 4

    def test_getitem(self):
        cm = ChainMap(
            {"a": 1, "b": 2}, {"b": 20, "c": 30}, {"c": 300, "d": 400}
        )

        assert cm["a"] == 1
        assert cm["b"] == 2
        assert cm["c"] == 30
        assert cm["d"] == 400

        with pytest.raises(KeyError):
            cm["z"]

        cm2 = cm.new_child()
        cm2["a"] = "asdf"
        assert cm2["a"] == "asdf"
        assert cm2["b"] == 2
        assert cm2["c"] == 30
        assert cm2["d"] == 400

    def test_setitem(self):
        cm = ChainMap()
        cm["c"] = 300
        cm["d"] = 400
        cm = cm.new_child()
        cm["b"] = 20
        cm["c"] = 30
        cm = cm.new_child()
        cm["a"] = 1
        cm["b"] = 2

        assert cm["a"] == 1
        assert cm["b"] == 2
        assert cm["c"] == 30
        assert cm["d"] == 400
        assert cm.maps == [
            {"a": 1, "b": 2},
            {"b": 20, "c": 30},
            {"c": 300, "d": 400},
        ]

    def test_delitem(self):
        cm = ChainMap(
            {"a": 1, "b": 2}, {"b": 20, "c": 30}, {"c": 300, "d": 400}
        )

        assert cm["b"] == 2
        assert len(cm) == 4
        del cm["b"]
        assert len(cm) == 4
        assert cm["a"] == 1
        assert cm["b"] == 20
        assert cm["c"] == 30
        assert cm["d"] == 400

        with pytest.raises(KeyError):
            del cm["b"]

    def test_iter(self):
        cm = ChainMap(
            {"a": 1, "b": 2}, {"b": 20, "c": 30}, {"c": 300, "d": 400}
        )

        found = set()
        for key in cm:
            found.add(key)
        assert found == set("abcd")

        dict_items = {"c": 30, "d": 400, "b": 2, "a": 1}.items()
        for k, v in cm.items():
            assert (k, v) in dict_items

    def test_repr(self):
        def assert_dict_repr(mydict, items):
            dict_repr = repr(mydict)
            if not dict_repr.startswith(
                type(mydict).__name__ + "({"
            ) or not dict_repr.endswith("})"):
                return False

            str_items = ("%r: %r" % (k, v) for k, v in items)
            return all(item in dict_repr for item in str_items)

        cm = ChainMap()
        assert repr(cm) == str(cm) == "ChainMap({})"
        assert repr(cm.new_child()) == "ChainMap({}, {})"

        cm = ChainMap({"a": 1, "b": 2}, {"b": 20, "c": 30})
        assert assert_dict_repr(cm, [("a", 1), ("b", 2), ("b", 20), ("c", 30)])

    def test_update(self):
        cm = ChainMap({"a": 1, "b": 2, "c": 3})
        assert len(cm) == 3
        assert cm["a"] == 1
        assert cm["b"] == 2
        assert cm["c"] == 3
        cm.update({"a": 11, "b": 22})
        assert len(cm) == 3
        assert cm["a"] == 11
        assert cm["b"] == 22
        assert cm["c"] == 3

        cm = cm.new_child()
        cm["b"] = 20
        cm["c"] = 30
        assert cm["a"] == 11
        assert cm["b"] == 20
        assert cm["c"] == 30
        cm = cm.parents
        assert cm["a"] == 11
        assert cm["b"] == 22
        assert cm["c"] == 3

    def test_clear(self):
        cm = ChainMap({"a": 1, "b": 2}, {"a": 10, "b": 20})
        assert len(cm) == 2
        assert cm["a"] == 1
        cm.clear()
        assert len(cm) == 2
        assert cm["a"] == 10

        assert cm.maps[0] == {}
        assert cm.maps[1] == {"a": 10, "b": 20}

    def test_get(self):
        cm = ChainMap({"a": 1, "b": 2}, {"b": 20, "c": 30})
        for key, value in {"a": 1, "b": 2, "c": 30}.items():
            assert cm.get(key) == value

        assert cm.get(404) is None
        assert cm.get(404, 200) == 200

    def test_pop(self):
        cm = ChainMap({"a": 1, "b": 2}, {"a": 10, "b": 20})
        assert cm.pop("a") == 1
        with pytest.raises(KeyError):
            cm.pop("a")

        assert cm.pop("a", 789) == 789

    def test_popitem(self):
        cm = ChainMap({"a": 1, "b": 2}, {"a": 10, "b": 20})
        assert cm.popitem() == ("b", 2)
        assert cm.popitem() == ("a", 1)
        with pytest.raises(KeyError):
            cm.popitem()

    def test_new_child(self):
        d1 = {1: 1}
        d2 = {2: 2}
        cm = ChainMap(d1, d2)
        cm2 = cm.new_child()
        assert cm2.maps[0] == {}
        assert cm2.maps[1] is d1
        assert cm2.maps[2] is d2

        m1 = {"a": 1, "b": 2}
        cm = ChainMap(m1)
        m2 = {"b": 20, "c": 30}
        cm2 = cm.new_child(m2)
        assert cm2.maps == [{"b": 20, "c": 30}, {"a": 1, "b": 2}]
        assert m2 is cm2.maps[0]
        assert m1 is cm2.maps[1]

    def test_parents(self):
        d1 = {1: 1}
        d2 = {2: 2}
        d3 = {3: 3}
        cm = ChainMap(d1, d2, d3)
        assert cm.parents == ChainMap(d2, d3)
        assert cm.parents.maps == [d2, d3]

    def test_copy(self):
        cm = ChainMap({"a": 1, "b": 2}, {"a": 10, "b": 20})
        for m in (cm.copy(), copy.copy(cm)):
            assert m == cm
            assert m.maps == cm.maps
            assert m is not cm
            assert m.maps[0] is not cm.maps[0]
            for m1, m2 in zip(m.maps[1:], cm.maps[1:]):
                assert m1 is m2

    def test_pickle(self):
        cm = ChainMap(
            {"a": 1, "b": 2}, {"b": 20, "c": 30}, {"c": 300, "d": 400}
        )
        for level in range(pickle.HIGHEST_PROTOCOL + 1):
            other = pickle.loads(pickle.dumps(cm, protocol=level))
            assert cm == other
            assert cm.maps == other.maps
            assert cm is not other
            for m1, m2 in zip(cm.maps, other.maps):
                assert m1 is not m2

    def test_bool(self):
        assert not ChainMap()
        assert not ChainMap({}, {})
        assert ChainMap({1: 2}, {})
        assert ChainMap({}, {1: 2})

    def test_missing(self):
        class DefaultChainMap(ChainMap):
            def __missing__(self, key):
                return 999

        dcm = DefaultChainMap({"a": 1, "b": 2}, {"b": 20, "c": 30})

        # Check __getitem__
        for key, value in {"a": 1, "b": 2, "c": 30, "d": 999}.items():
            assert dcm[key] == value

        # Check get()
        for key, value in {"a": 1, "b": 2, "c": 30, "d": 77}.items():
            assert dcm.get(key, 77) == value

        # Check __contains__
        for key, value in dict(a=True, b=True, c=True, d=False).items():
            assert (key in dcm) == value

        assert dcm.pop("a", 1001) == 1
        assert dcm.pop("a", 1002) == 1002
        assert dcm.popitem() == ("b", 2)
        with pytest.raises(KeyError):
            dcm.popitem()

    def test_dict_coercion(self):
        cm = ChainMap({"a": 1, "b": 2}, {"b": 20, "c": 30})
        assert dict(cm) == {"a": 1, "b": 2, "c": 30}
        assert dict(cm.items()) == {"a": 1, "b": 2, "c": 30}

    def test_fromkeys(self):
        assert ChainMap.fromkeys("abc") == ChainMap(
            {"a": None, "b": None, "c": None}
        )
        assert ChainMap.fromkeys("abc", 1) == ChainMap(
            {"a": 1, "b": 1, "c": 1}
        )


class TestScopeChainMap:
    def test_init(self):
        assert issubclass(ScopeChainMap, ChainMap)

    def test_getitem(self):
        scm = ScopeChainMap({"a": 1, "b": 2}, {"a": 10, "b": 20})
        assert scm["a"] == 1
        assert scm["b"] == 2

        scm = ScopeChainMap({1: {"aa": 11}}, {1: {"aa": 110, "bb": 220}})
        inner_chainmap = scm[1]
        assert isinstance(inner_chainmap, ScopeChainMap)
        assert len(inner_chainmap.maps) == 2
        assert inner_chainmap == {"aa": 11, "bb": 220}
        maps = [{"aa": 11}, {"aa": 110, "bb": 220}]
        for m1, m2 in zip(inner_chainmap.maps, maps):
            assert m1 == m2

        scm = ScopeChainMap(
            {1: 8}, {1: {"aa": 11}}, {1: {"aa": 110, "bb": 220}}
        )
        assert scm[1] == 8

        scm = ScopeChainMap(
            {1: {"aa": 11}}, {1: 8}, {1: {"aa": 110, "bb": 220}}
        )
        assert len(scm[1].maps) == 1
        assert scm[1].maps[0] == {"aa": 11}

        with pytest.raises(KeyError):
            scm["z"]

    def test_missing(self):
        class DefaultScopeChainMap(ScopeChainMap):
            def __missing__(self, key):
                return 999

        dscm = DefaultScopeChainMap({"a": 1, "b": 2}, {"b": 20, "c": 30})
        for key, value in {"a": 1, "b": 2, "c": 30, "d": 999}.items():
            assert dscm[key] == value
