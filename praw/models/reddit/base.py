"""Provide the RedditBase class."""

from collections import defaultdict
from operator import attrgetter
import sys

from ...const import API_PATH, urlparse
from ...exceptions import ClientException, PRAWException
from ...util.collections import AttributeContainer, ChainMap
from ..base import PRAWBase

string_types = (str,)
if sys.version_info.major <= 2:
    string_types = (basestring,)


class RedditBase(PRAWBase):
    """Base class that represents actual Reddit objects."""

    @staticmethod
    def _url_parts(url):
        parsed = urlparse(url)
        if not parsed.netloc:
            raise ClientException("Invalid URL: {}".format(url))
        return parsed.path.rstrip("/").split("/")

    @property
    def fullname(self):
        """Return the object's fullname.

        A fullname is an object's kind mapping like ``t3`` followed by an
        underscore and the object's base36 ID, e.g., ``t1_c5s96e0``.

        """
        return "{}_{}".format(self._reddit._objector.kind(self), self.id)

    a = property(
        attrgetter("_attributes"),
        doc="Provide an object to access the data fetched from reddit.",
    )

    def __eq__(self, other):
        """Return whether the other instance equals the current."""
        if isinstance(other, string_types):
            return other.lower() == str(self).lower()
        return (
            isinstance(other, self.__class__)
            and str(self).lower() == str(other).lower()
        )

    def __getattr__(self, name):
        """Return the value of attribute `name`."""
        if name.startswith("_"):
            raise AttributeError(name)

        try:
            return self._attributes[name]
        except KeyError:
            pass

        raise AttributeError(
            "{!r} object has no attribute {!r}".format(
                self.__class__.__name__, name
            )
        )

    def __hash__(self):
        """Return the hash of the current instance."""
        return hash(self.__class__.__name__) ^ hash(str(self).lower())

    def __init__(self, reddit, _data):
        """Initialize a RedditBase instance (or a subclass).

        :param reddit: An instance of :class:`~.Reddit`.

        """
        super(RedditBase, self).__init__(reddit, _data=_data)
        self._fetched = False
        self._info_params = {}

        attrs = self._attrs = defaultdict(dict)
        mapping = attrs[0] = self._data
        self._init_attributes(attrs)
        if len(attrs) > 1:
            mapping = ChainMap(*[attrs[k] for k in sorted(attrs)])
        self._attributes = AttributeContainer(mapping, self._maybe_fetch)

    def __repr__(self):
        """Return an object initialization representation of the instance."""
        return "{}({}={!r})".format(
            self.__class__.__name__, self.STR_FIELD, str(self)
        )

    def __str__(self):
        """Return a string representation of the instance."""
        return getattr(self, self.STR_FIELD)

    def __ne__(self, other):
        """Return whether the other instance differs from the current."""
        return not (self == other)

    def _fetch(self):
        if hasattr(self, "_info_path"):
            other = self._reddit.get(
                self._info_path(), params=self._info_params
            )
        else:
            self._info_params["id"] = self.fullname
            children = self._reddit.get(
                API_PATH["info"], params=self._info_params
            )._data["children"]
            if not children:
                raise PRAWException(
                    "No {!r} data returned for thing {}".format(
                        self.__class__.__name__, self.fullname
                    )
                )
            other = children[0]
        self._update_attributes(other._attrs)
        self._fetched = True

    def _init_attributes(self, attrs):
        pass

    def _reset_attributes(self, attrs):
        for attr in attrs:
            for attr_layer in self._attrs.values():
                attr_layer.pop(attr, None)

    def _update_attributes(self, attrs):
        self_attrs = self._attrs
        for key, value in attrs.items():
            self_attrs[key].update(value)

    def _maybe_fetch(self, name):
        if not (self._fetched or name.startswith("_")):
            self._fetch()
            return True
