class TestDcosCli():
    def test_execute(self, dcos):
        # test a valid command
        cmd = "node"
        output, errors = dcos.execute(cmd)
        assert errors == '' or errors is None
        
        # test an invalid command
        cmd = "noSuchCommand"
        try:
            dcos.execute(cmd)
            assert False
        except:
            assert True
