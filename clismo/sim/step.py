from random import choice


class Step:
    def __init__(self, name, servers):
        self.name = name
        self.servers = servers
        self.clients_queue = []

    def assign_client_to_server(self, client):
        free_servers = [server for server in self.servers if not server.in_use]
        rand_server = choice(free_servers)
        rand_server.in_use = True
        rand_server.attend_client(client)

    def receive_client(self, client):
        if self.clients_queue:
            self.clients_queue.append(client)
        else:
            self.assign_client_to_server(client)

    def next_client(self):
        if self.clients_queue:
            client = self.clients_queue.pop(0)
            self.assign_client_to_server(client)
