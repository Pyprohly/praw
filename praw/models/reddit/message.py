"""Provide the Message class."""
import sys
from ...const import API_PATH
from .base import RedditBase
from .mixins import InboxableMixin, ReplyableMixin
from .redditor import Redditor
from .subreddit import Subreddit


string_types = (str,)
if sys.version_info.major <= 2:
    string_types = (basestring,)


class Message(InboxableMixin, ReplyableMixin, RedditBase):
    """A class for private messages.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``author``              Provides an instance of :class:`.Redditor`.
    ``body``                The body of the message.
    ``created_utc``         Time the message was created, represented in
                            `Unix Time`_.
    ``dest``                Provides an instance of :class:`.Redditor`. The
                            recipient of the message.
    ``id``                  The ID of the message.
    ``name``                The full ID of the message, prefixed with 't4'.
    ``subject``             The subject of the message.
    ``subreddit``           If the message was sent from a subreddit,
                            provides an instance of :class:`.Subreddit`.
    ``was_comment``         Whether or not the message was a comment reply.
    ======================= ===================================================


    .. _Unix Time: https://en.wikipedia.org/wiki/Unix_time

    """

    STR_FIELD = "id"
    OBJECTIFIABLE = {"author", "dest", "replies", "subreddit"}

    @classmethod
    def _objectify(cls, reddit, data):
        key = "author"
        item = data.get(key)
        if isinstance(item, string_types):
            data[key] = (
                None
                if item in ("[deleted]", "[removed]")
                else Redditor(reddit, name=item)
            )

        key = "dest"
        item = data.get(key)
        if isinstance(item, string_types):
            if item.startswith("#"):
                data[key] = Subreddit(reddit, item[1:])
            else:
                data[key] = Redditor(reddit, item)

        key = "replies"
        item = data.get(key)
        if isinstance(item, (string_types, dict)):
            if item == "":
                data[key] = []
            else:
                data[key] = reddit._objector.objectify(
                    item["data"]["children"]
                )

        key = "subreddit"
        item = data.get(key)
        if isinstance(item, string_types):
            data[key] = Subreddit(reddit, display_name=item)

    def __new__(cls, reddit, _data):
        """Create a new instance."""
        if _data.get("subreddit") is None:
            return super(Message, cls).__new__(cls)
        else:
            return super(Message, cls).__new__(SubredditMessage)

    def __getnewargs__(self):
        return (self._reddit, self._data)

    def __init__(self, reddit, _data):
        """Construct an instance of the Message object."""
        super(Message, self).__init__(reddit, _data=_data)
        self._fetched = True

    def _init_attributes(self, attrs):
        super(Message, self)._init_attributes(attrs)

        objectified, rdata = attrs[-1], attrs[0]
        objectified.update(
            {key: rdata[key] for key in self.OBJECTIFIABLE if key in rdata}
        )
        self._objectify(self._reddit, objectified)

    def delete(self):
        """Delete the message.

        .. note:: Reddit does not return an indication of whether or not the
                  message was successfully deleted.
        """
        self._reddit.post(
            API_PATH["delete_message"], data={"id": self.fullname}
        )


class SubredditMessage(Message):
    """A class for messages to a subreddit."""

    def mute(self, _unmute=False):
        """Mute the sender of this SubredditMessage."""
        self._reddit.post(API_PATH["mute_sender"], data={"id": self.fullname})

    def unmute(self):
        """Unmute the sender of this SubredditMessage."""
        self._reddit.post(
            API_PATH["unmute_sender"], data={"id": self.fullname}
        )
