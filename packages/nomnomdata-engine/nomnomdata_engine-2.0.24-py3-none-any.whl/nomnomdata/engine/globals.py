from wrapt import ObjectProxy


class LocalProxy(ObjectProxy):
    def __init__(self, name):
        super().__init__(None)

    def _set(self, proxy_obj):
        super().__init__(proxy_obj)


current_engine = LocalProxy("Engine Context")
current_nominode = LocalProxy("Nominode Context")
