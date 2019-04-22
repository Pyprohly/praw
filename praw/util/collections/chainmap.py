"""ChainMap implementation."""

try:
    from collections.abc import Mapping, MutableMapping
except ImportError:  # pragma: no cover
    from collections import Mapping, MutableMapping
from reprlib import recursive_repr


class ChainMap(MutableMapping):
    """See :py:class:`collections.ChainMap`.

    This class is optimized for PRAW's use. Users may want to consider using
    the standard ``collections.ChainMap`` implementation instead of this one.
    """

    @classmethod
    def fromkeys(cls, iterable, *args):
        """Create a ChainMap with a single dict created from the iterable."""
        return cls(dict.fromkeys(iterable, *args))

    @property
    def parents(self):
        """New ChainMap from maps[1:]."""
        return type(self)(*self.maps[1:])

    def __init__(self, *maps):
        """Create a new ChainMap.

        Create a new ChainMap from the provided mappings, otherwise
        if no mappings are provided, use a single empty dictionary.
        """
        self.maps = list(maps) or [{}]

    @recursive_repr()
    def __repr__(self):
        """Return repr(self)."""
        return "{0.__class__.__name__}({1})".format(
            self, ", ".join(map(repr, self.maps))
        )

    def __len__(self):
        """Return len(self)."""
        return len(set().union(*self.maps))

    def __iter__(self):
        """Implement iter(self)."""
        combined = {}
        for mapping in reversed(self.maps):
            combined.update(mapping)
        return iter(combined)

    def __contains__(self, key):
        """Implement `in` membership test."""
        return any(key in m for m in self.maps)

    def __bool__(self):
        """Implement `bool(self)`."""
        return any(self.maps)

    def __missing__(self, key):
        """Support missing key action for subclasses."""
        raise KeyError(key)

    def __getitem__(self, key):
        """Get self[key]."""
        for mapping in self.maps:
            try:
                return mapping[key]
            except KeyError:
                pass
        return self.__missing__(key)

    def __setitem__(self, key, value):
        """Set self[key] to `value`."""
        self.maps[0][key] = value

    def __delitem__(self, key):
        """Delete self[key]."""
        try:
            del self.maps[0][key]
        except KeyError:
            raise KeyError("Key not found in the first mapping: %r" % key)

    def get(self, key, default=None):
        """Return the value for key if key is in the dictionary,
        else return default.
        """
        return self[key] if key in self else default

    def copy(self):
        """New ChainMap or subclass with a new copy of maps[0]
        and refs to maps[1:]
        """
        return type(self)(self.maps[0].copy(), *self.maps[1:])

    __copy__ = copy

    def clear(self):
        """Clear maps[0]. Leave maps[1:] intact."""
        self.maps[0].clear()

    def popitem(self):
        """Remove and return an item pair from maps[0].
        Raise KeyError is maps[0] is empty.
        """
        try:
            return self.maps[0].popitem()
        except KeyError:
            raise KeyError("No keys found in the first mapping.")

    def pop(self, key, *args):
        """Remove *key* from maps[0] and return its value.
        Raise KeyError if *key* not in maps[0].
        """
        try:
            return self.maps[0].pop(key, *args)
        except KeyError:
            raise KeyError("Key not found in the first mapping: %r" % key)

    def new_child(self, m=None):
        """New ChainMap with a new map followed by all previous maps.
        If no map is provided, an empty dict is used.
        """
        if m is None:
            m = {}
        return type(self)(m, *self.maps)


class ScopeChainMap(ChainMap):
    """Like ChainMap but chains nested mappings.

    If key value is a mapping type then successive mappings will continue
    to be searched until either a non-mapping type is found or each of the
    maps have been seen. All mappings found are then combined into a new
    ScopeChainMap before being returned.

    Item retrieval behaves the same as ChainMap for non-mapping types.
    """

    def __getitem__(self, key):
        maps = []
        for mapping in self.maps:
            if key in mapping:
                value = mapping[key]
                if isinstance(value, Mapping):
                    maps.append(value)
                elif maps:
                    return type(self)(*maps)
                else:
                    return value
        if maps:
            return type(self)(*maps)
        return self.__missing__(key)
