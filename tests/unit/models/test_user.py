import pytest
from praw.models import User

from .. import UnitTest


class TestUser(UnitTest):
    def test_me__in_read_only_mode(self):
        assert self.reddit.read_only
        user = User(self.reddit)
        with pytest.raises(RuntimeError):
            user.me()
