import pytest
from clismo.sim.client import Client
from clismo.sim.server import Server
from clismo.sim.simulation import Simulation
from clismo.sim.step import Step


def test_client():
    client = Client(name="test_client")
    assert client.name == "test_client"

    client = Client(name="test_client", weight=1, capacity=10)
    assert client.attrs["weight"] == 1
    assert client.attrs["capacity"] == 10


def test_server():
    client = Client(name="test_client")
    cli = client.get()

    server = Server(name="test_server", func=lambda self, cli: 1)
    assert server.name == "test_server"
    assert server.attend_client(cli) == 1

    server = Server(
        name="test_server",
        func=lambda self, cli: self.attrs["speed"] * 2,
        speed=2,
    )
    assert server.attend_client(cli) == 4


def test_step():
    s1 = Server(name="test_server", func=lambda self, cli: 1)
    s2 = Server(name="test_server", func=lambda self, cli: 2)

    step = Step(name="test_step", servers=[s1])
    assert step.name == "test_step"
    assert step.servers == [s1]

    step.add_server(s2)
    assert step.servers == [s1, s2]


def test_simple_simulation():
    client = Client(name="client")

    s1 = Server(name="s1", func=lambda self, cli: 3)
    s2 = Server(name="s2", func=lambda self, cli: 1)
    step = Step(name="step 1", servers=[s1, s2])

    arrival_func = lambda: (1, client)

    sim = Simulation(
        arrival_func=arrival_func,
        steps=[step],
        client_limit=10,
    )
    assert sim.steps == [step]

    sim.run()
    assert sim.clients <= 10

    sim.client_limit = None
    sim.time_limit = 15

    sim.run()
    assert sim.time <= 15
