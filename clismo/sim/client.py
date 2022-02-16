class Client:
    def __init__(self, name, *attrs):
        self.name = name
        self.attrs = attrs
        self.on_server_out_funcs = {}

    def add_on_server_out_callback(self, func, server):
        func_list = self.on_server_out_funcs.get(server, [])
        func_list.append(func)

    def on_server_out(self, server):
        func_list = self.on_server_out_funcs.get(server, [])
        for func in func_list:
            func(self.attrs)
