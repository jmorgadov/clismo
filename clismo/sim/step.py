from random import choice

from clismo.sim.optimizable_obj import OptimizableObject


class Step(OptimizableObject):
    def __init__(self, name, servers=None):
        super().__init__("servers")
        self.name = name
        self.servers = servers or []
        self.clients_queue = []
        self.attrs = {}

    def add_server(self, server):
        self.servers.append(server)

    def assign_client_to_server(self, client):
        free_servers = [server for server in self.servers if not server.in_use]
        rand_server = choice(free_servers)
        rand_server.in_use = True
        return rand_server.attend_client(client), rand_server

    def receive_client(self, client):
        if self.clients_queue or all(server.in_use for server in self.servers):
            self.clients_queue.append(client)
            return None, None
        return self.assign_client_to_server(client)

    def next_client(self):
        if self.clients_queue:
            client = self.clients_queue.pop(0)
            return self.assign_client_to_server(client)
        return None, None

    def __repr__(self):
        return self.name
