from pathlib import Path

import typer

from clismo.compiler import Grammar, LR1Parser, ParserManager
from clismo.cs_builders import builders
from clismo.cs_tokenizer import tknz
from clismo.visitors.eval_visitor import EvalVisitor
from clismo.visitors.semantic_checker import SemanticChecker
from clismo.visitors.type_builder import TypeBuilder

app = typer.Typer(add_completion=False)


def echo(msg, verbose):
    if verbose:
        typer.echo(msg)


def get_ast(file_path: str, verbose: bool = False):
    # Load grammar
    echo("Loading grammar", verbose)
    grammar = Grammar.open(str(Path(__file__).parent / "cs_grammar.gm"))
    echo("Assigning builders", verbose)
    grammar.assign_builders(builders)

    # Create LR1Parser
    echo("Loading parser table", verbose)
    parser = LR1Parser(grammar, str(Path(__file__).parent / "cs_lr1_table"))

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

    type_builder = TypeBuilder()
    type_builder.visit(program)

    semantic_checker = SemanticChecker(type_builder.types)
    semantic_checker.visit(program)

    evaluator = EvalVisitor(semantic_checker.objects)
    evaluator.visit(program)


if __name__ == "__main__":
    app()
