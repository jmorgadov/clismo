from queue import PriorityQueue

from clismo.sim.server import Server


class Simulation:
    def __init__(self, arrival_func, steps, time_limit=None, client_limit=None):
        self.arrival_func = arrival_func
        self.steps = steps
        self.time = 0
        self.clients = 0
        self.events = PriorityQueue()
        if time_limit is None and client_limit is None:
            raise ValueError("Either time_limit or client_limit must be specified")
        self.time_limit = time_limit
        self.client_limit = client_limit

    def run(self):
        self.time = 0
        self.clients = 0
        self.events = PriorityQueue()
        while True:
            if self.events.empty():
                delta_time, client_type = self.arrival_func()
                client = client_type.get()
                self.events.put(
                    (self.time + delta_time, delta_time, client, Server.ghost(), 0)
                )
            time, delta_time, client, last_server, step = self.events.get()
            if step < len(self.steps):
                print(
                    f"{round(time, 3):>10} {client.name} "
                    f"arrived at {self.steps[step].name}",
                )
            else:
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
                if self.client_limit is not None and self.clients == self.client_limit:
                    break
                continue
            if step == 0:
                delta_time, client_type = self.arrival_func()
                client = client_type.get()
                self.events.put(
                    (self.time + delta_time, delta_time, client, Server.ghost(), 0)
                )
            event_time, server = self.steps[step].receive_client(client)
            if event_time is not None:
                self.events.put(
                    (self.time + event_time, event_time, client, server, step + 1)
                )
