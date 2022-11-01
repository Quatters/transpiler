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
        self._we_are_in_string = False

    def parse(self, root: Node):
        try:
            self.dfs(root)
        except AssertionError as error:
            node = error.args[0]["node"]
            msg = f"{node.token.value} at line {node.token.line}"
            additional_msg = error.args[0]["message"]
            msg += f' - {additional_msg}'
            if self.filepath is not None:
                msg += f" ({self.filepath}:{node.token.line})"
            raise SemanticError(msg)

    def dfs(self, node: Node, counter: int = 0, children: list[Node] = None ):
        children = children or []
        setattr(node, "visited", True)

        if self._we_are_in_string and node.tag == Tag.QUOTE:
            self._we_are_in_string = False
        elif not self._we_are_in_string:
            if node.token.tag == Tag.MATH_OPERATOR:
                pass

            if node.tag == Tag.ID:
                if self.is_left(node, children):
                    self.assert_var_is_not_defined(node)
                    self.vars_dict[node.token.value] = {
                        "type": children[3]
                    }

            right_tags = [Tag.NUMBER_INT,
                          Tag.NUMBER_FLOAT,
                          Tag.BOOLEAN_VALUE,
                          Tag.QUOTE,
                          Tag.MATH_OPERATOR,
                          Tag.BOOLEAN_OPERATOR,
                          Tag.BOOLEAN_NOT]

            if node.tag in right_tags or (node.tag == Tag.ID and not self.is_left(node, children)):
                if node.tag == Tag.QUOTE:
                    self._we_are_in_string = True

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
            types_are_equal = node_type.token.value == type_node_value.token.value
            types_left_is_real_right_is_int = node_type.token.value.lower() == "real" and \
                                              type_node_value.token.value.lower() == "integer"
            assert types_are_equal or types_left_is_real_right_is_int, \
                    {"node": node_value, "message": f"type {type_node_value.token.value} of {node_value.token.value} is not assignable to {node_type.token.value}"}
        elif node_value.tag == Tag.NUMBER_INT:
            assert node_type.token.value.lower() in ["integer", "real"], {"node": node_value, "message": f"{node_value.token.value} is not assignable to type {node_type.token.value}"}
        elif node_value.tag == Tag.NUMBER_FLOAT:
            assert node_type.token.value.lower() == "real", {"node": node_value, "message": f"{node_value.token.value} is not assignable to type {node_type.token.value}"}
        elif node_value.tag == Tag.BOOLEAN_VALUE:
            assert node_type.token.value.lower() == "boolean", {"node": node_value, "message": f"{node_value.token.value} is not assignable to type {node_type.token.value}"}
        elif node_value.tag == Tag.QUOTE:
            if node_type.token.value.lower() == "char" and self._we_are_in_string:
                siblings = node_value.parent.children
                only_one_child = not siblings[1].children[1].children
                is_single_char = len(siblings[1].children[0].token.value) == 1
                assert only_one_child and is_single_char, {"node": node_value, "message": f"type string is not assignable to type char"}
            else:
                assert node_type.token.value.lower() == "string", {"node": node_value, "message": f"type string is not assignable to type {node_type.token.value}"}
        elif node_value.tag == Tag.MATH_OPERATOR:
            left_type_value = node_type.token.value.lower()
            if node_value.token.value == '+':
                assert left_type_value in ["integer", "real", "string"], {"node": node_value,
                                                                "message": f"operator {node_value.token.value} cannot be applied to type {left_type_value}"}
            else:
                assert left_type_value in ["integer", "real"], {"node": node_value, "message": f"operator {node_value.token.value} cannot be applied to type {left_type_value}"}
        elif node_value.tag in [Tag.BOOLEAN_OPERATOR, Tag.BOOLEAN_NOT]:
            left_type_value = node_type.token.value.lower()
            assert left_type_value == "boolean", {"node": node_value,
                                                            "message": f"operator {node_value.token.value} cannot be applied to type {left_type_value}"}

    def assert_var_is_defined(self, node_id):
        assert node_id.token.value in self.vars_dict, {"node": node_id, "message": "variable is not defined"}

    def assert_var_is_not_defined(self, node_id):
        assert node_id.token.value not in self.vars_dict, {"node": node_id, "message": "variable is already defined"}

    def is_left(self, node_cur: Node, children: list[Node]) -> bool:
        if [child for child in children if child.tag == NT.OPTIONAL_DEFINE_VAR_ASSIGNMENT]:
            return True

        return False


"""
    
                s := '- / + * false true'
                s1 := s; -- Сем еррор

    ТЕСТИКИ 
        если все норм, то делаем сравнения

        Проверка на то чтобы внутри кавычек ничего не обрабатывалось

        Если в выражении есть деление, то оно будет real
      
      По умолчанию интовые переменные имеют значение 0
      
      d - оказывается в values для себя самого
      var d: integer := 10;
      d := 15;

                этот код рабочий
                var a: integer;
                var b: integer := a + (20 - 2) * 6;

                undefined vars


Значения по умолчанию:
    int 0
    real 0
    bool false
    char ничего
    string ничего


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
