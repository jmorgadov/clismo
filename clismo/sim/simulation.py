from queue import PriorityQueue

from clismo.sim.optimizable_obj import OptimizableObject
from clismo.sim.server import Server


class Simulation(OptimizableObject):
    def __init__(self, name, steps, time_limit=None, client_limit=None):
        super().__init__("steps", "client_types")
        self.name = name
        self.arrival_funcs = []
        self.client_types = []
        self.steps = steps
        self.time = 0
        self.clients = 0
        self.events = PriorityQueue()
        self.time_limit = time_limit
        self.client_limit = client_limit
        self.minimize_func = None
        self.attrs = {}

    def add_arrival_func(self, arrival_func, client):
        self.arrival_funcs.append((arrival_func, client))
        self.client_types.append(client)

    def __run_arrivals(self):
        for arrival_func, client_type in self.arrival_funcs:
            delta_time = arrival_func()
            client = client_type.get()
            self.events.put(
                (self.time + delta_time, delta_time, client, Server.ghost(), 0)
            )

    def run(self, verbose=False):
        if self.time_limit is None and self.client_limit is None:
            raise ValueError("Either time_limit or client_limit must be specified")
        if not self.arrival_funcs:
            raise ValueError("No arrival functions specified")
        self.time = 0
        self.clients = 0
        self.events = PriorityQueue()
        for step in self.steps:
            step.clients_queue = []
            for i, server in enumerate(step.servers):
                step.servers[i] = server.get()

        while True:
            if self.events.empty():
                self.__run_arrivals()
            time, delta_time, client, last_server, step = self.events.get()
            if step < len(self.steps) and verbose:
                print(
                    f"{round(time, 3):>10} {client.name} "
                    f"arrived at {self.steps[step].name}",
                )
            elif verbose:
                print(
                    f"{round(time, 3):>10} {client.name} out of system",
                )
            if self.time_limit is not None and time > self.time_limit:
                break
            self.time = time
            if step > 0:
                last_server.in_use = False
                client.on_server_out(last_server, delta_time)
                event_time, server = self.steps[step - 1].next_client()
                if event_time is not None:
                    self.events.put(
                        (self.time + event_time, event_time, client, server, step)
                    )
            if step == len(self.steps):
                self.clients += 1
                if self.client_limit is not None and self.clients >= self.client_limit:
                    break
                continue
            if step == 0:
                self.__run_arrivals()
            event_time, server = self.steps[step].receive_client(client)
            if event_time is not None:
                self.events.put(
                    (self.time + event_time, event_time, client, server, step + 1)
                )
        if verbose:
            print()

    def __repr__(self):
        return self.name
