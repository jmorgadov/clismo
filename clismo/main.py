import json
import logging
from random import choice

import typer

from clismo.optimization.client_server_optimizer import ModelOptimizer
from clismo.sim.client import Client
from clismo.sim.server import Server
from clismo.sim.simulation import Simulation
from clismo.sim.step import Step

# import numlab
# from numlab.compiler import Grammar, LR1Parser, ParserManager
# from numlab.lang.context import Context
# from numlab.nl_builders import builders
# from numlab.nl_tokenizer import tknz

# Set logging level to DEBUG
# logging.basicConfig(level=logging.DEBUG)

app = typer.Typer(add_completion=False)


def echo(msg, verbose):
    if verbose:
        typer.echo(msg)


# def get_ast(file_path: str, verbose: bool = False):
#     # Load grammar
#     echo("Loading grammar", verbose)
#     grammar = Grammar.open("clismo/cs_grammar.gm")
#     echo("Assigning builders", verbose)
#     grammar.assign_builders(builders)

#     # Create LR1Parser
#     echo("Loading parser table", verbose)
#     parser = LR1Parser(grammar, "clismo/cs_lr1_table")

#     # Create parser
#     parser_man = ParserManager(grammar, tknz, parser)

#     # Parse file
#     echo("Parsing script", verbose)
#     program = parser_man.parse_file(file_path)
#     return program


@app.command()
def run(
    input_path: str = typer.Argument(..., help="Input file"),
    dump: bool = typer.Option(False, "--dump", "-d", help="Dump AST"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode"),
):
    """Run the program given in the input file"""

    client = Client(name="client")
    s1 = Server(name="s1", func=lambda self, cli: 1)
    s2 = Server(name="s2", func=lambda self, cli: 3)
    step = Step(name="test_step", servers=[s2, s2, s1])

    def step_possible_servers():
        servers = [s1, s2]
        return [choice(servers) for _ in range(3)]

    step.add_possible_change(step_possible_servers, "servers")

    sim = Simulation(
        steps=[step],
        client_limit=3,
    )
    sim.add_arrival_func(lambda: 1, client)
    sim.minimize_func = lambda: sim.time
    opt = ModelOptimizer(sim)
    opt.run()
    print(sim.steps[0].servers)
    # program = get_ast(input_path, verbose)
    # if dump:
    #     program.dump()

    # # Evaluate
    # echo("Program output:", verbose)


if __name__ == "__main__":
    app()
