import abc
from typing import List

from clismo.compiler.generic_ast import AST
from clismo.compiler.grammar import Grammar
from clismo.compiler.tokenizer import Token


class Parser(metaclass=abc.ABCMeta):
    def __init__(self, grammar: Grammar):
        self.grammar = grammar

    @abc.abstractmethod
    def parse(self, tokens: List[Token]) -> AST:
        pass
