"""Provide the ModAction class."""

import sys

from .base import PRAWBase
from .reddit.redditor import Redditor

string_types = (str,)
if sys.version_info.major <= 2:
    string_types = (basestring,)


class ModAction(PRAWBase):
    """Represent a moderator action."""

    @property
    def mod(self):
        """Return the Redditor who the action was issued by."""
        return self._data["mod"]

    @mod.setter
    def mod(self, value):
        self._data["mod"] = value

    @classmethod
    def _objectify(cls, reddit, data):
        key = "mod"
        item = data.get(key)
        if isinstance(item, string_types):
            data[key] = Redditor(reddit, name=item)
        elif isinstance(item, Redditor):
            item._reddit = reddit

    def __init__(self, reddit, _data):
        """Initialize a ModAction instance."""
        if _data is not None:
            self._objectify(reddit, _data)
        super(ModAction, self).__init__(reddit, _data=_data)
