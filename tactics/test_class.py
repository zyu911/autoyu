from tactics.interface import Interface


class TestClass(Interface):
    def get_data(self):
        print('get data!')

    def ret_tactics(self):
        print('return tactics')