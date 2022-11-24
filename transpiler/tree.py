from abc import ABC
from transpiler.base import Token, Symbol


class Node:
    def __init__(self, token: Token, parent=None):
        self.token = token
        self.parent = parent
        self.children = []

        if self.parent is not None:
            self.parent.children.insert(0, self)

    def __repr__(self) -> str:
        return f'Node({self.token})'

    @property
    def tag(self):
        return self.token.tag


class SyntaxTree(ABC):
    def __init__(self, root):
        self.root = self.get_node(root)
        self.is_semantically_correct = False
        self.vars_dict = {}

    @staticmethod
    def get_node(value: Node | Token | Symbol, parent: Node = None) -> Node:
        if isinstance(value, Symbol):
            value = Token(tag=value, value=value.value)
        if isinstance(value, Token):
            return Node(value, parent)
        return value

    def add(self, value, to: Node) -> Node:
        return self.get_node(value, to)


class ParseTree(SyntaxTree):
    pass
