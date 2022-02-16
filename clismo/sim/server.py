class Server:
    def __init__(self, name, func, **attrs):
        self.name = name
        self.func = func
        self.attrs = attrs
        self.total_clients = 0
        self.in_use = False

    def attend_client(self, client):
        self.in_use = True
        return self.func(self, client)

    @staticmethod
    def ghost():
        return Server("ghost", lambda s, c: None)

    def __lt__(self, other):
        return self.name < other.name
