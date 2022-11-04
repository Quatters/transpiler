from transpiler.tree import SyntaxTree, Node
from transpiler.settings import Tag, NT
from transpiler.base import TranspilerError
from abc import ABC


class SemanticError(TranspilerError):
    pass


class BaseType(ABC):
    @staticmethod
    def get_error_data(node: Node, expected_type: str):
        return {
            'node': node,
            'message': f'{node.token.value} is not compatible with type {expected_type}'
        }

    @classmethod
    def assert_(cls, expr: list[Node], vars_dict: dict):
        cls.expr = expr
        cls.vars_dict = vars_dict
        for node in expr:
            cls.check_node(node)

    @classmethod
    def check_node(cls, node: Node):
        raise NotImplementedError

    @classmethod
    def is_type(cls, node: Node, types: list[str]) -> bool:
        return cls.vars_dict[node.token.value]["type"].token.value in types


class IntType(BaseType):
    # учесть деление
    @classmethod
    def check_node(cls, node: Node):
        assert (node.tag == Tag.ID and cls.is_type(node, ["integer"])) \
            or (node.tag == Tag.NUMBER_INT) \
            or (node.tag == Tag.MATH_OPERATOR) \
            or (node.tag in [Tag.LBRACKET, Tag.RBRACKET]), \
                cls.get_error_data(node, 'integer')


class RealType(BaseType):
    @classmethod
    def check_node(cls, node: Node):
        assert (node.tag == Tag.ID and cls.is_type(node, ["integer", "real"])) \
            or (node.tag in [Tag.NUMBER_INT, Tag.NUMBER_FLOAT]) \
            or (node.tag == Tag.MATH_OPERATOR) \
            or (node.tag in [Tag.LBRACKET, Tag.RBRACKET]), \
                cls.get_error_data(node, 'real')


class CharType(BaseType):
    @classmethod
    def assert_(cls, expr: list[Node], vars_dict: dict):
        cls.vars_dict = vars_dict

        if expr[0].tag == Tag.ID:
            assert cls.is_type(expr[0], ["char"]), cls.get_error_data(expr[0], 'char')
        else:
            assert expr[0].tag == Tag.QUOTE, cls.get_error_data(expr[0], 'char')
            assert expr[-1].tag == Tag.QUOTE, cls.get_error_data(expr[0], 'char')
            assert len(expr) > 2 and len(expr[1].token.value) == 1, {
                'node': expr[1],
                'message': 'invalid char, ensure value length is strictly 1'
            }


class StringType(BaseType):
    @classmethod
    def assert_(cls, expr: list[Node], vars_dict: dict):
        cls.is_string = False
        super().assert_(expr, vars_dict)

    @classmethod
    def check_node(cls, node: Node):
        if node.tag == Tag.QUOTE:
            cls.is_string = not cls.is_string
        elif not cls.is_string:
            assert (node.tag == Tag.ID and cls.is_type(node, ["char", "string"])) \
                or (node.token.value == "+"), cls.get_error_data(node, 'string')

class BooleanType(BaseType):
    @classmethod
    def check_node(cls, node: Node):
        if node.tag is Tag.ID:
            assert cls.is_type(node, ['boolean']), cls.get_error_data(node, 'boolean')

    @classmethod
    def assert_(cls, expr: list[Node], vars_dict: dict):
        super().assert_(expr, vars_dict)
        cls._parse_expr()

    @classmethod
    def _parse_expr(cls):
        def parse_node(node: Node):
            if node.tag in [Tag.BOOLEAN_VALUE, Tag.ID]:
                return 'True'
            if node.tag is Tag.NUMBER_INT:
                return '1'
            if node.tag is Tag.NUMBER_FLOAT:
                return '1.0'
            if node.token.value == '=':
                return '=='

            return node.token.value
        pseudo_literal_expr = ' '.join(map(parse_node, cls.expr))
        error_data = cls.get_error_data(cls.expr[0], 'boolean')
        try:
            result = eval(pseudo_literal_expr)
            assert isinstance(result, bool), error_data
        except TypeError:
            raise AssertionError(error_data)




class SemanticAnalyzer:

    def __init__(self, tree: SyntaxTree, filepath: str | None = None):
        self.tree = tree
        self.filepath = filepath
        self.vars_dict = {}
        self._we_are_in_string = False
        self._visited_nodes = {}

    def parse(self, root: Node):
        try:
            self.dfs(root, callback=self._check)
        except AssertionError as error:
            node = error.args[0]["node"]
            if not isinstance(node.tag, Tag):
                raise ValueError(f'got unexpected non-terminal token: {node.tag}')
            msg = f"{node.token.value} at line {node.token.line}"
            additional_msg = error.args[0]["message"]
            msg += f' - {additional_msg}'
            if self.filepath is not None:
                msg += f" ({self.filepath}:{node.token.line})"
            raise SemanticError(msg)

    def dfs(self, node: Node, children: list[Node] = None, callback=None):
        children = children or []
        # setattr(node, "visited", True)
        callback_name = callback.__name__ if callback is not None else 'default'
        visited = self._visited_nodes.get(callback_name)
        if visited is None:
            self._visited_nodes[callback_name] = {node.__hash__()}
        else:
            self._visited_nodes[callback_name].add(node.__hash__())

        if callback is not None:
            callback(node, children)

        for child in node.children:
            if child not in self._visited_nodes[callback_name]:
                self.dfs(child, node.children, callback)

    def _check(self, node: Node, children: list[Node] = None):
        if self._we_are_in_string and node.tag == Tag.QUOTE:
            self._we_are_in_string = False
        elif not self._we_are_in_string:
            if node.token.tag == Tag.MATH_OPERATOR:
                pass

            # if node.tag == Tag.ID:
                # if self.is_left(node, children):
                    # self.assert_var_is_not_defined(node)
                    # self.vars_dict[node.token.value] = {
                    #     "type": children[3]
                    # }

        if node.tag in [NT.DEFINE_VAR, NT.ABSTRACT_STATEMENT]:
            self.assert_type_of_right_expression(node)

            # right_tags = [Tag.NUMBER_INT,
            #               Tag.NUMBER_FLOAT,
            #               Tag.BOOLEAN_VALUE,
            #               Tag.QUOTE,
            #               Tag.MATH_OPERATOR,
            #               Tag.BOOLEAN_OPERATOR,
            #               Tag.BOOLEAN_NOT,
            #               Tag.COMPARE]

            # if node.tag in right_tags or (node.tag == Tag.ID and not self.is_left(node, children)):
            #     if node.tag == Tag.QUOTE:
            #         self._we_are_in_string = True
            #
            #     deep_parent = self.get_deep_parent(node)
            #     self.assert_type_of_right_expression(deep_parent)

                # if deep_parent.tag == NT.DEFINE_VAR:
                #     id_node: Node = [child for child in deep_parent.children if child.tag == Tag.ID][0]
                #     id_type: Node = [child for child in deep_parent.children if child.tag == Tag.TYPE_HINT][0]
                #     self.assert_var_type(id_type, node)
                # elif deep_parent.tag == NT.ABSTRACT_STATEMENT:
                #     id_node = deep_parent.children[0]
                #     self.assert_var_is_defined(id_node)
                #
                #     id_type = self.vars_dict[id_node.token.value]["type"]
                #     self.assert_var_type(id_type, node)
                #
                # if "values" in self.vars_dict[id_node.token.value]:
                #     self.vars_dict[id_node.token.value]["values"].append(node.token.value)
                # else:
                #     self.vars_dict[id_node.token.value]["values"] = [node.token.value]

    def get_child_id(self):
        pass

    def get_deep_parent(self, node: Node):
        current = node
        while current is not None and current.tag != NT.DEFINE_VAR and current.tag != NT.ABSTRACT_STATEMENT:
            current = current.parent

        return current

    def assert_type_of_right_expression(self, deep_parent: Node): # переименовать в node
        if deep_parent.tag == NT.DEFINE_VAR:
            self._assert_type_of_define_var(deep_parent)
        elif deep_parent.tag == NT.ABSTRACT_STATEMENT:
            self._assert_type_of_abstract_statement(deep_parent)

    def _assert_type_of_define_var(self, node: Node):
        left_var = node.children[1]
        self.assert_var_is_not_defined(left_var)
        self.vars_dict[left_var.token.value] = {
            "type": node.children[3]
        }

        optional_define_var_assignment_node = node.children[4]
        self.right_terminals = []
        self._visited_nodes[self._collect_right_terminals.__name__] = set()
        self.dfs(optional_define_var_assignment_node, callback=self._collect_right_terminals)

        self.assert_expr_type(left_var)

    def _assert_type_of_abstract_statement(self, node: Node):
        left_var = node.children[0]
        self.assert_var_is_defined(left_var)
        abstract_statement_node = node.children[1]

        self.right_terminals = []
        self._visited_nodes[self._collect_right_terminals.__name__] = set()
        self.dfs(abstract_statement_node, callback=self._collect_right_terminals)

        self.assert_expr_type(left_var)

    def _collect_right_terminals(self, node: Node, siblings: list[Node] = None):
        if isinstance(node.tag, Tag) and node.tag is not Tag.ASSIGN:
            self.right_terminals.append(node)
            if node.tag is Tag.ID and not (len(siblings) > 1 and siblings[1].tag is NT.STRING_PART):
                self.assert_var_is_defined(node)

    def assert_expr_type(self, node: Node):
        id_type = self.get_id_type(node)
        if id_type == "integer":
            IntType.assert_(self.right_terminals, self.vars_dict)
        elif id_type == "real":
            RealType.assert_(self.right_terminals, self.vars_dict)
        elif id_type == "char":
            CharType.assert_(self.right_terminals, self.vars_dict)
        elif id_type == "string":
            StringType.assert_(self.right_terminals, self.vars_dict)
        elif id_type == "boolean":
            BooleanType.assert_(self.right_terminals, self.vars_dict)
        else:
            raise ValueError(f'unknown type: {id_type}')
    #     if node_value.tag == Tag.ID:
    #         self.assert_var_is_defined(node_value)
    #         type_node_value = self.vars_dict[node_value.token.value]["type"]
    #         types_are_equal = node_type.token.value == type_node_value.token.value
    #         types_left_is_real_right_is_int = node_type.token.value.lower() == "real" and \
    #                                           type_node_value.token.value.lower() == "integer"
    #         assert types_are_equal or types_left_is_real_right_is_int, \
    #                 {"node": node_value, "message": f"type {type_node_value.token.value} of {node_value.token.value} is not assignable to {node_type.token.value}"}
    #     elif node_value.tag == Tag.NUMBER_INT:
    #         assert node_type.token.value.lower() in ["integer", "real"], {"node": node_value, "message": f"{node_value.token.value} is not assignable to type {node_type.token.value}"}
    #     elif node_value.tag == Tag.NUMBER_FLOAT:
    #         assert node_type.token.value.lower() == "real", {"node": node_value, "message": f"{node_value.token.value} is not assignable to type {node_type.token.value}"}
    #     elif node_value.tag == Tag.BOOLEAN_VALUE:
    #         assert node_type.token.value.lower() == "boolean", {"node": node_value, "message": f"{node_value.token.value} is not assignable to type {node_type.token.value}"}
    #     elif node_value.tag == Tag.QUOTE:
    #         if node_type.token.value.lower() == "char" and self._we_are_in_string:
    #             siblings = node_value.parent.children
    #             only_one_child = not siblings[1].children[1].children
    #             is_single_char = len(siblings[1].children[0].token.value) == 1
    #             assert only_one_child and is_single_char, {"node": node_value, "message": f"type string is not assignable to type char"}
    #         else:
    #             assert node_type.token.value.lower() == "string", {"node": node_value, "message": f"type string is not assignable to type {node_type.token.value}"}
    #     elif node_value.tag == Tag.MATH_OPERATOR:
    #         left_type_value = node_type.token.value.lower()
    #         if node_value.token.value == '+':
    #             assert left_type_value in ["integer", "real", "string"], {"node": node_value,
    #                                                             "message": f"operator {node_value.token.value} cannot be applied to type {left_type_value}"}
    #         else:
    #             assert left_type_value in ["integer", "real"], {"node": node_value, "message": f"operator {node_value.token.value} cannot be applied to type {left_type_value}"}
    #     elif node_value.tag in [Tag.BOOLEAN_OPERATOR, Tag.BOOLEAN_NOT]:
    #         left_type_value = node_type.token.value.lower()
    #         assert left_type_value == "boolean", {"node": node_value,
    #                                                         "message": f"operator {node_value.token.value} cannot be applied to type {left_type_value}"}
    #     elif node_value.tag == Tag.COMPARE:
    #         pass

    def assert_var_is_defined(self, node_id):
        assert node_id.token.value in self.vars_dict, {"node": node_id, "message": "variable is not defined"}

    def assert_var_is_not_defined(self, node_id):
        assert node_id.token.value not in self.vars_dict, {"node": node_id, "message": "variable is already defined"}

    def is_left(self, node_cur: Node, children: list[Node]) -> bool:
        if [child for child in children if child.tag == NT.OPTIONAL_DEFINE_VAR_ASSIGNMENT]:
            return True

        return False

    def get_id_type(self, node: Node) -> str:
        return self.vars_dict[node.token.value]["type"].token.value



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
