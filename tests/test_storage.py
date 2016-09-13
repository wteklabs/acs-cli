class TestStorage():
    def test_create(self, storage):
        key = storage.create("acsteststorage")
        assert key
