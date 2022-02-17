"""
This module contains the basic structures for parsing.
"""

from __future__ import annotations

from typing import List

from clismo.compiler.generic_ast import AST
from clismo.compiler.grammar import Grammar
from clismo.compiler.parsers.lr1_parser import LR1Parser
from clismo.compiler.parsers.parser import Parser
from clismo.compiler.tokenizer import Token, Tokenizer


class ParserManager:
    """Structure used for parsing a file, text or token list given a
    grammar and a tokenizer.

    Parameters
    ----------
    grammar : Grammar
        Grammar that will be use for parsing.
    tokenizer : Tokenizer
        Tokenizer that will be use for tokenize a given txt.
    parser : Parser
        Parser that will be use for parsing a given list of tokens.
    """

    def __init__(
        self, grammar: Grammar, tokenizer: Tokenizer = None, parser: Parser = None
    ):
        self.grammar = grammar
        self.tokenizer = tokenizer
        self.parser = LR1Parser(grammar) if parser is None else parser

    def parse_file(self, file_path: str) -> AST:
        """Opens a file and parses it contents.

        Parameters
        ----------
        file_path : str
            File path.

        Returns
        -------
        AST
            AST generated by the parser.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        return self.parse(text)

    def parse(self, text: str) -> AST:
        """Parses a text.

        Parameters
        ----------
        text : str
            Text to be parsed.

        Returns
        -------
        AST
            AST generated by the parser.
        """
        tokens = self.tokenizer.tokenize(text)
        return self.parse_tokens(tokens)

    def parse_tokens(self, tokens: List[Token]) -> AST:
        """Parses a list of tokens.

        Parameters
        ----------
        tokens : List[Token]
            List of tokens to be parsed.
        method : str
            Method used for parsing.

        Returns
        -------
        AST
            AST generated by the parser.
        """
        tokens += [Token("$", "$")]
        return self.parser.parse(tokens)
