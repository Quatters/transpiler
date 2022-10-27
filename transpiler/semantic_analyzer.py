from transpiler.tree import SyntaxTree, Node
from transpiler.settings import Tag, NT
from transpiler.base import TranspilerError


class SemanticError(TranspilerError):
    pass

class SemanticAnalyzer:

    def __init__(self, tree: SyntaxTree, filepath: str | None = None):
        self.tree = tree
        self.filepath = filepath
        self.vars_dict = {}

    def parse(self, root: Node):
        try:
            self.dfs(root)
        except AssertionError as error:
            node = error.args[0]
            msg = f"'{node.token.value}' at line {node.token.line}"
            if self.filepath is not None:
                msg += f" ({self.filepath}:{node.token.line})"
            raise SemanticError(msg)

    def dfs(self, node: Node, counter: int = 0, children: list[Node] = None ):
        children = children or []
        setattr(node, "visited", True)

        if not node.children and isinstance(node.tag, Tag):
            print("Layer", counter, node, "Leave")
        elif isinstance(node.tag, Tag):
            print("Layer", counter, node)

        if isinstance(node.tag, Tag) and node.tag == Tag.ID:
            if self.is_left(node, children):
                print(children)
                self.vars_dict[node.token.value] = {
                    "type": children[3]
                }


        if isinstance(node.tag, Tag) and node.tag in [Tag.NUMBER_INT, Tag.NUMBER_FLOAT] or (node.tag == Tag.ID and not self.is_left(node, children)):
            deep_parent = self.get_deep_parent(node)

            if deep_parent.tag == NT.DEFINE_VAR:
                id_node: Node = [child for child in deep_parent.children if child.tag == Tag.ID][0]
                id_type: Node = [child for child in deep_parent.children if child.tag == Tag.TYPE_HINT][0]
                self.assert_var_type(id_type, node)
            elif deep_parent.tag == NT.ABSTRACT_STATEMENT:
                id_node = deep_parent.children[0]
                self.assert_var_is_defined(id_node)

                id_type = self.vars_dict[id_node.token.value]["type"]
                self.assert_var_type(id_type, node)

            if "values" in self.vars_dict[id_node.token.value]:
                self.vars_dict[id_node.token.value]["values"].append(node.token.value)
            else:
                self.vars_dict[id_node.token.value]["values"] = [node.token.value]

        for child in node.children:
            if not hasattr(child, "visited"):
                self.dfs(child, counter + 1, node.children)

    def get_child_id(self):
        pass

    def get_deep_parent(self, node: Node):
        current = node
        while current.tag != NT.DEFINE_VAR and current.tag != NT.ABSTRACT_STATEMENT:
            current = current.parent

        return current

    def assert_var_type(self, node_type: Node, node_value: Node):
        if node_value.tag == Tag.ID:
            self.assert_var_is_defined(node_value)
            type_node_value = self.vars_dict[node_value.token.value]["type"]
            assert node_type.token.value == type_node_value.token.value, node_value
        elif node_type.token.value.lower() == "integer":
            assert node_value.token.value.isdigit(), node_value
        elif node_type.token.value.lower() == "real":
            try:
                float(node_value.token.value)
            except ValueError:
                raise AssertionError(node_value)
        elif node_type.token.value.lower() == "boolean":
            bool_var = node_value.token.value.lower()
            assert bool_var in ["true", "false"], node_value
        else:
            pass # Доделать типы


    def assert_var_is_defined(self, node_id):
        assert node_id.token.value in self.vars_dict, node_id

    def is_left(self, node_cur: Node, children: list[Node]) -> bool:
        if [child for child in children if child.tag == NT.OPTIONAL_DEFINE_VAR_ASSIGNMENT]:
            return True

        return False




"""
                var a: integer;
                var b: integer := a + (20 - 2) * 6;
                
                undefined vars

True or False - строка или бул вар

преобразование CST в AST
в AST отсутствуют вспомогательные конструкции(скобки, комментарии)

надо реализовать обход дерева

таблица символов(туда будут попадать все переменные)
(var(здесь может быть токен со всей инфой), value)
строится для каждой области видимости
В ходе анализа таблицы символов складываются в стек, а после выхода из области видимости удаляются из него.

vars
неопределенные переменные
повторное объявление идентификатора
доступ к переменной вне области

! количество параметров в функции или процедуре


types
приведение типов
операции с разными типами

int <- int
   real <- int
char !- int
string !- int
bool !- int

int !- real
real <- real
char !- real
string !- real
bool !- real

int !- char
real !- char
char <- char
  string <- char
bool !- char

int !- string
real !- string
char !- string
string <- string
bool !- string

int !- bool
real !- bool
char !- bool
string !- bool
bool <- bool
"""