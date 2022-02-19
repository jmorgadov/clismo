from clismo.sim.optimizable_obj import OptimizableObject


class Server(OptimizableObject):
    def __init__(self, name, func, **attrs):
        super().__init__()
        self.name = name
        self.func = func
        self.attrs = attrs
        self.in_use = False

    def attend_client(self, client):
        self.in_use = True
        return self.func(self, client)

    @staticmethod
    def ghost():
        return Server("ghost", lambda s, c: None)

    def __lt__(self, other):
        return self.name < other.name

    def get(self):
        return Server(self.name, self.func, **self.attrs)

    def __repr__(self):
        return self.name
