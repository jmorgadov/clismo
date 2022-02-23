from clismo.sim.optimizable_obj import OptimizableObject


class Client(OptimizableObject):
    def __init__(self, name, **attrs):
        super().__init__()
        self.name = name
        self.attrs = attrs
        self.on_server_out_funcs = {}
        self.init_func = None

    def add_on_server_out_callback(self, func, server: str):
        func_list = self.on_server_out_funcs.get(server, [])
        func_list.append(func)

    def on_server_out(self, server, time):
        func_list = self.on_server_out_funcs.get(server.name, [])
        for func in func_list:
            func(self, server, time)

    def get(self):
        if self.init_func is not None:
            self.init_func()
        cli = Client(self.name, **self.attrs.copy())
        cli.on_server_out_funcs = self.on_server_out_funcs
        cli.init_func = self.init_func
        return cli

    def __lt__(self, other):
        return self.name < other.name

    def __repr__(self):
        return self.name
