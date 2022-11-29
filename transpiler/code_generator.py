from transpiler.tree import Node


class CodeGenerator:

    def __init__(self):
        self.code = ""

    def add_token(self, node: Node, siblings: list[Node]):
        print(node.token.value)
