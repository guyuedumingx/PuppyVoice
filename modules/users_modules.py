from assistantlib.build_in import *


class Light(HttpDevice):
    """
    灯
    """

    def open(self, handler):
        return self.send(handler,{'operaName':'open'})

    def close(self, handler):
        return self.send(handler,{'operaName':'close'})