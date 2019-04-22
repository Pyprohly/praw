"""AttributeContainer implementation."""

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping
from pprint import PrettyPrinter, pformat


class AttributeContainer(Mapping):
    """A container for holding arbitrary attributes.

    Besides indexing, attributes can be accessed as if they were members.

    The standard mapping methods, `.get()`, `.keys()`, `.values()`, and
    `.items()`, will always take precedence over arbitrary attribute access.
    Indexing should be used to access values of attributes with those names.

    A reference to the mapping passed to the constructor will be stored.
    This makes it suitable for wrapping mapping types.

    The inner dict object can be retrieved using `abs(self)`.
    """

    __slots__ = ("__data", "__callback")

    @staticmethod
    def _pprint_attribute_container(
        printer, obj, stream, indent, allowance, context, level
    ):
        cls_name = obj.__class__.__name__
        stream.write(cls_name + "(")
        printer._format(
            obj._as_dict_maybe_ref(),
            stream,
            indent + len(cls_name) + 1,
            allowance + 1,
            context,
            level,
        )
        stream.write(")")

    def __init__(self, data, callback=None):
        """Initialize an AttributeContainer.

        Takes any mapping.

        An optional callback function may specified. During a KeyError or
        AttributeError this function will be called. If a truthy value is
        returned a second attempt will be made to retrieve the attribute.
        """
        self.__data = data
        self.__callback = callback

    def __repr__(self):
        """Return repr(self)."""
        return "%s(%r)" % (self.__class__.__name__, self._as_dict_maybe_ref())

    def __str__(self):
        """Return str(self)."""
        return pformat(self)

    def __iter__(self):
        """Implement iter(self)."""
        return iter(self.__data)

    def __len__(self):
        """Return len(self)."""
        return len(self.__data)

    def __abs__(self):
        """Return the inner mapping object."""
        return self.__data

    def __dir__(self):
        """Support tab completion."""
        return self.keys()

    def __getitem__(self, key):
        """Return the value of attribute `key`."""
        try:
            return self.__data[key]
        except KeyError:
            if self.__callback is None:
                raise

        if self.__callback(key):
            return self.__data[key]

        raise KeyError(repr(key))

    def __getattr__(self, name, mapping_type=dict):
        """Return the value of attribute `name`.

        Mapping objects are wrapped in an AttributeContainer before
        being returned. This lets you dot chain into inner mappings.
        """
        try:
            attr = self[name]
        except KeyError:
            pass
        else:
            if isinstance(attr, mapping_type):
                return type(self)(attr)
            return attr

        raise AttributeError(repr(name))

    def __contains__(self, item):
        """Implement `in` membership test."""
        return item in self.__data

    def __getstate__(self):
        """Extract state to pickle."""
        return (self.__data, self.__callback)

    def __setstate__(self, state):
        """Restore from pickled state."""
        self.__data = state[0]
        self.__callback = state[1]

    def _as_dict_maybe_ref(self):
        data = self.__data
        if not isinstance(data, dict):
            data = dict(data)
        return data

    if isinstance(getattr(PrettyPrinter, "_dispatch", None), dict):
        PrettyPrinter._dispatch[
            __repr__
        ] = _pprint_attribute_container.__func__
