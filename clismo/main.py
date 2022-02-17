import json
import logging
from random import choice

import typer

from clismo.compiler import Grammar, LR1Parser, ParserManager
# from clismo.lang.context import Context
from clismo.cs_builders import builders
from clismo.cs_tokenizer import tknz
from clismo.optimization.client_server_optimizer import ModelOptimizer
from clismo.sim.client import Client
from clismo.sim.server import Server
from clismo.sim.simulation import Simulation
from clismo.sim.step import Step

# Set logging level to DEBUG
# logging.basicConfig(level=logging.DEBUG)

app = typer.Typer(add_completion=False)


def echo(msg, verbose):
    if verbose:
        typer.echo(msg)


def get_ast(file_path: str, verbose: bool = False):
    # Load grammar
    echo("Loading grammar", verbose)
    grammar = Grammar.open("clismo/cs_grammar.gm")
    echo("Assigning builders", verbose)
    grammar.assign_builders(builders)

    # Create LR1Parser
    echo("Loading parser table", verbose)
    parser = LR1Parser(grammar, "clismo/cs_lr1_table")

    # Create parser
    parser_man = ParserManager(grammar, tknz, parser)

    # Parse file
    echo("Parsing script", verbose)
    program = parser_man.parse_file(file_path)
    return program


@app.command()
def run(
    input_path: str = typer.Argument(..., help="Input file"),
    dump: bool = typer.Option(False, "--dump", "-d", help="Dump AST"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode"),
):
    program = get_ast(input_path, verbose)
    if dump:
        program.dump()

    # # Evaluate
    # echo("Program output:", verbose)


if __name__ == "__main__":
    app()
