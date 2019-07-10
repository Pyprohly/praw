"""Provide the InboxToggleableMixin class."""
from ....const import API_PATH


class InboxToggleableMixin:
    """Interface for classes that can optionally receive inbox replies."""

    def disable_inbox_replies(self):
        """Disable inbox replies for the item.

        Example usage:

        .. code:: python

           comment = reddit.comment('dkk4qjd')
           comment.disable_inbox_replies()

           submission = reddit.submission('8dmv8z')
           submission.disable_inbox_replies()

        See also :meth:`~.enable_inbox_replies`

        """
        self._reddit._request_and_check_error(
            "POST",
            API_PATH["sendreplies"],
            data={"id": self.fullname, "state": False},
        )

    def enable_inbox_replies(self):
        """Enable inbox replies for the item.

        Example usage:

        .. code:: python

           comment = reddit.comment('dkk4qjd')
           comment.enable_inbox_replies()

           submission = reddit.submission('8dmv8z')
           submission.enable_inbox_replies()

        See also :meth:`~.disable_inbox_replies`

        """
        self._reddit._request_and_check_error(
            "POST",
            API_PATH["sendreplies"],
            data={"id": self.fullname, "state": True},
        )
