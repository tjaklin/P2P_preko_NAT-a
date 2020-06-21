class Host:
    def __init__(self, name, adr = None):
        self.name = name
        self.address(adr)

    def address(self, adr):
        # parametar adr je tuple formatiran ovako: ( '127.0.0.1', 12345)
        self.address = adr
