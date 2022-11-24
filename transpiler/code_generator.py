from transpiler.tree import Node


class CodeGenerator:
    def add_token(self, node: Node, siblings: list[Node], **vars_dict):
        ...
