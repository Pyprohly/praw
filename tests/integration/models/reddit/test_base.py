from ... import IntegrationTest


class TestFetch(IntegrationTest):
    def test_implicit_fetch__accelerator(self):
        redditor = self.reddit.redditor("spez")
        assert len(redditor.a) == 1
        assert not redditor._fetched

        with self.recorder.use_cassette(
            "TestFetch.test_implicit_fetch__accelerator"
        ):
            assert redditor.created_utc == 1118030400

        assert len(redditor.a) > 5
        assert redditor._fetched

    def test_implicit_fetch__namespace(self):
        redditor = self.reddit.redditor("spez")
        assert len(redditor.a) == 1
        assert not redditor._fetched
        assert "created_utc" not in redditor.a
        assert not redditor._fetched

        with self.recorder.use_cassette(
            "TestFetch.test_implicit_fetch__namespace"
        ):
            assert redditor.a.created_utc == 1118030400

        assert len(redditor.a) > 5
        assert redditor._fetched

    # def test_explicit_fetch(self):
    #     redditor = self.reddit.redditor("spez")
    #     assert len(redditor.a) == 1
    #     assert not redditor.fetched

    #     with self.recorder.use_cassette("TestFetch.test_explicit_fetch"):
    #         redditor.fetch()

    #     assert redditor.fetched
    #     assert "created_utc" in redditor.a

    # def test_refetch(self):
    #     redditor = self.reddit.redditor("spez")

    #     with self.recorder.use_cassette("TestFetch.test_refetch-0"):
    #         redditor.fetch()

    #     assert redditor.a.created_utc == 1118030400
    #     redditor.data["created_utc"] = 10
    #     assert redditor.a.created_utc == 10

    #     with self.recorder.use_cassette("TestFetch.test_refetch-1"):
    #         redditor.fetch()

    #     assert redditor.a.created_utc == 10

    #     with self.recorder.use_cassette("TestFetch.test_refetch-2"):
    #         redditor.fetch(True)

    #     assert redditor.fetched
    #     assert redditor.a.created_utc == 1118030400

    # def test_return(self):
    #     with self.recorder.use_cassette("TestFetch.test_return"):
    #         redditor.fetch().fetch(True)
