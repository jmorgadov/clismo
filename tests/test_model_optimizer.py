from random import choice

import pytest
from clismo.optimization.client_server_optimizer import ModelOptimizer
from clismo.sim.client import Client
from clismo.sim.server import Server
from clismo.sim.simulation import Simulation
from clismo.sim.step import Step


def test_optimizer():
    client = Client(name="client")
    s1 = Server(name="s1", func=lambda self, cli: 1)
    s2 = Server(name="s2", func=lambda self, cli: 50)
    step = Step(name="test_step", servers=[s2, s2, s1])

    def step_possible_servers():
        servers = [s1, s2]
        return [choice(servers) for _ in range(3)]

    step.add_possible_change(step_possible_servers, "servers")

    sim = Simulation(
        "test",
        steps=[step],
        client_limit=10,
    )
    sim.add_arrival_func(lambda: 1, client)
    sim.minimize_func = lambda: sim.time
    opt = ModelOptimizer(sim)
    opt.run()
    print(sim.steps[0].servers)
    assert all(s.name == "s1" for s in sim.steps[0].servers)
