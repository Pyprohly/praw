from ... import UnitTest

from praw.models import Redditor


class TestAttributeAccess(UnitTest):
    def test_attribute_accelerator(self):
        redditor = Redditor(self.reddit, _data={"name": "smarty1", "m": 5})
        assert redditor.name == "smarty1"
        assert redditor.m == 5
        assert len(redditor.a) == 2

    def test_attribute_namespace(self):
        redditor = Redditor(self.reddit, _data={"name": "smarty1", "m": 5})
        assert redditor.a.name == "smarty1"
        assert redditor.a.m == 5
        assert len(redditor.a) == 2
