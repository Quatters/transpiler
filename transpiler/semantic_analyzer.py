from transpiler.tree import SyntaxTree, Node
from transpiler.settings import Tag, NT
from transpiler.base import TranspilerError, TranspilerEnum
from abc import ABC


class VarType(TranspilerEnum):
    INTEGER = 'integer'
    REAL = 'real'
    BOOLEAN = 'boolean'
    CHAR = 'char'
    STRING = 'string'

    @classmethod
    def from_str(cls, str_type):
        if str_type.lower() == 'integer':
            return cls.INTEGER
        if str_type.lower() == 'real':
            return cls.REAL
        if str_type.lower() == 'boolean':
            return cls.BOOLEAN
        if str_type.lower() == 'char':
            return cls.CHAR
        if str_type.lower() == 'string':
            return cls.STRING


class SemanticError(TranspilerError):
    pass


class PascalAnyComparable:
    def __init__(self, *args):
        pass

    def __eq__(self, *args):
        return True

    def __lt__(self, *args):
        return True

    def __gt__(self, *args):
        return True

    def __le__(self, *args):
        return True

    def __ge__(self, *args):
        return True

    def __ne__(self, *args):
        return True


class PascalEntity:
    def __bool__(self):
        raise TypeError


class PascalNumber(PascalEntity):
    def __add__(self, other):
        if not isinstance(other, (PascalAnyComparable, PascalNumber)):
            raise TypeError
        return PascalNumber()

    def __sub__(self, other):
        if not isinstance(other, (PascalAnyComparable, PascalNumber)):
            raise TypeError
        return PascalNumber()

    def __mul__(self, other):
        if not isinstance(other, (PascalAnyComparable, PascalNumber)):
            raise TypeError
        return PascalNumber()

    def __truediv__(self, other):
        if not isinstance(other, (PascalAnyComparable, PascalNumber)):
            raise TypeError
        return PascalNumber()

    def __eq__(self, other, *args):
        if isinstance(other, (PascalAnyComparable, PascalNumber)):
            return True
        raise TypeError

    def __lt__(self, other, *args):
        if isinstance(other, (PascalAnyComparable, PascalNumber)):
            return True
        raise TypeError

    def __gt__(self, other, *args):
        if isinstance(other, (PascalAnyComparable, PascalNumber)):
            return True
        raise TypeError

    def __le__(self, other, *args):
        if isinstance(other, (PascalAnyComparable, PascalNumber)):
            return True
        raise TypeError

    def __ge__(self, other, *args):
        if isinstance(other, (PascalAnyComparable, PascalNumber)):
            return True
        raise TypeError

    def __ne__(self, other, *args):
        if isinstance(other, (PascalAnyComparable, PascalNumber)):
            return True
        raise TypeError


class PascalInt(PascalNumber):
    pass


class PascalReal(PascalNumber):
    pass


class PascalString(PascalEntity):
    def __add__(self, other):
        if not isinstance(other, (PascalAnyComparable, PascalString)):
            raise TypeError

    def __sub__(self, other):
        raise TypeError

    def __mul__(self, other):
        raise TypeError

    def __truediv__(self, other):
        raise TypeError

    def __eq__(self, other, *args):
        if isinstance(other, (PascalAnyComparable, PascalString)):
            return True
        raise TypeError

    def __lt__(self, other, *args):
        if isinstance(other, (PascalAnyComparable, PascalString)):
            return True
        raise TypeError

    def __gt__(self, other, *args):
        if isinstance(other, (PascalAnyComparable, PascalString)):
            return True
        raise TypeError

    def __le__(self, other, *args):
        if isinstance(other, (PascalAnyComparable, PascalString)):
            return True
        raise TypeError

    def __ge__(self, other, *args):
        if isinstance(other, (PascalAnyComparable, PascalString)):
            return True
        raise TypeError

    def __ne__(self, other, *args):
        if isinstance(other, (PascalAnyComparable, PascalString)):
            return True
        raise TypeError


class PascalChar(PascalString):
    pass


class BaseType(ABC):
    @staticmethod
    def get_error_data(node: Node, expected_type: str):
        return {
            'node': node,
            'message':
                f'{node.token.value} '
                f'is not compatible with type {expected_type}'
        }

    @classmethod
    def assert_(cls, expr: list[Node], vars_dict: dict, current_scope: int):
        cls.expr = expr
        cls.vars_dict = vars_dict
        cls.current_scope = current_scope
        for node in expr:
            cls.check_node(node)

    @classmethod
    def check_node(cls, node: Node):
        raise NotImplementedError

    @classmethod
    def is_var(cls, node: Node):
        try:
            return node.parent.children[1].children[0].tag is not NT.CALL
        except (IndexError):
            return True

    @classmethod
    def get_var_type(cls, node: Node) -> VarType:
        for scope in range(cls.current_scope, -1, -1):
            scoped_vars = cls.vars_dict.get(scope)
            if not scoped_vars:
                continue
            var = scoped_vars.get(node.token.value)
            if not var:
                continue
            return var["type"]
        raise ValueError(f'cannot find variable: {node.token.value}')

    @classmethod
    def is_type(cls, node: Node, types: list[VarType]) -> bool:
        return cls.get_var_type(node) in types

    @classmethod
    def is_defined(cls, node_id: Node):
        try:
            cls.is_type(node_id, [])
            return True
        except ValueError:
            return False


class IntType(BaseType):
    # учесть деление
    @classmethod
    def check_node(cls, node: Node):
        acceptable = [
            Tag.NUMBER_INT,
            Tag.MATH_OPERATOR,
            Tag.LBRACKET,
            Tag.RBRACKET,
            Tag.COMMA,
        ]
        assert node.tag in acceptable \
            or node.tag is Tag.ID \
            and cls.is_var(node) and cls.is_type(node, [VarType.INTEGER]) \
            or node.tag is Tag.ID and not cls.is_var(node), \
            cls.get_error_data(node, VarType.INTEGER)


class RealType(BaseType):
    @classmethod
    def check_node(cls, node: Node):
        acceptable = [
            Tag.NUMBER_INT,
            Tag.NUMBER_FLOAT,
            Tag.MATH_OPERATOR,
            Tag.LBRACKET,
            Tag.RBRACKET,
            Tag.COMMA,
        ]
        assert node.tag in acceptable \
            or node.tag is Tag.ID \
            and cls.is_var(node) \
            and cls.is_type(node, [VarType.INTEGER, VarType.REAL]) \
            or node.tag is Tag.ID and not cls.is_var(node), \
            cls.get_error_data(node, VarType.REAL)


class CharType(BaseType):
    @classmethod
    def assert_(cls, expr: list[Node], vars_dict: dict, current_scope: int):
        cls.vars_dict = vars_dict
        cls.current_scope = current_scope

        if expr[0].tag is Tag.ID:
            assert cls.is_type(expr[0], [VarType.CHAR]) \
                or not cls.is_var(expr[0]), \
                cls.get_error_data(expr[0], VarType.CHAR)
        else:
            assert expr[0].tag == Tag.QUOTE, \
                cls.get_error_data(expr[0], VarType.CHAR)
            assert expr[-1].tag == Tag.QUOTE, \
                cls.get_error_data(expr[0], VarType.CHAR)
            assert len(expr) > 2 and len(expr[1].token.value) == 1, {
                'node': expr[1],
                'message': 'invalid char, ensure value length is strictly 1'
            }


class StringType(BaseType):
    @classmethod
    def assert_(cls, expr: list[Node], vars_dict: dict, current_scope: int):
        cls.is_string = False
        super().assert_(expr, vars_dict, current_scope)

    @classmethod
    def check_node(cls, node: Node):
        if node.tag == Tag.QUOTE:
            cls.is_string = not cls.is_string
        elif not cls.is_string:
            assert (node.token.value == "+") \
                or node.tag == Tag.ID \
                and cls.is_var(node) \
                and cls.is_type(node, [VarType.CHAR, VarType.STRING]) \
                or (node.tag is Tag.ID and not cls.is_var(node)), \
                cls.get_error_data(node, VarType.STRING)


class BooleanType(BaseType):
    @classmethod
    def check_node(cls, node: Node):
        if node.tag == Tag.QUOTE:
            cls.is_string = not cls.is_string
        if not cls.is_string and node.tag is Tag.ID:
            assert not cls.is_var(node) \
                or cls.is_defined(node), \
                cls.get_error_data(node, VarType.BOOLEAN)

    @classmethod
    def assert_(cls, expr: list[Node], vars_dict: dict, current_scope: int):
        cls.is_string = False
        super().assert_(expr, vars_dict, current_scope)
        cls._parse_expr()

    @classmethod
    def _parse_expr(cls):
        cls.is_string = False

        def parse_node(node: Node):
            if node.tag is Tag.QUOTE:
                if cls.is_string:
                    value = 'PascalString()'
                else:
                    value = ''
                cls.is_string = not cls.is_string
                return value
            if cls.is_string:
                return ''
            if node.tag in [Tag.BOOLEAN_VALUE]:
                return 'True'
            if node.tag is Tag.ID and not cls.is_string:
                if cls.is_var(node):
                    var_type = cls.get_var_type(node)
                    if var_type is VarType.BOOLEAN:
                        return 'True'
                    elif var_type is VarType.INTEGER:
                        return 'PascalInt()'
                    elif var_type is VarType.REAL:
                        return 'PascalReal()'
                    elif var_type is VarType.STRING:
                        return 'PascalString()'
                    elif var_type is VarType.CHAR:
                        return 'PascalChar()'
                return 'PascalAnyComparable'
            if node.tag is Tag.NUMBER_INT:
                return 'PascalInt()'
            if node.tag is Tag.NUMBER_FLOAT:
                return 'PascalReal()'
            if node.token.value == '=':
                return '=='
            if node.token.value == '<>':
                return '!='
            return node.token.value

        error_data = {
            'node': cls.expr[0],
            'message': 'expression is not compatible with type boolean'
        }
        try:
            str_expr = ' '.join(map(parse_node, cls.expr))
            internal_vars = {}
            exec(f'__mock_value__ = {str_expr}', globals(), internal_vars)
            assert isinstance(internal_vars['__mock_value__'], bool), error_data
        except TypeError:
            raise AssertionError(error_data)


class SemanticAnalyzer:
    def __init__(self, tree: SyntaxTree, filepath: str | None = None):
        self.tree = tree
        self.filepath = filepath
        self._visited_nodes = {}

        # 0 for global scope variables
        # 1 for nested if/for/while/until
        # 2 for subnested and so on
        self.current_scope = 0
        self.vars_dict = {self.current_scope: {}}
        self.__is_in_string = False

        self.__is_in_string_perform_assertions = False

    def parse(self):
        try:
            self.dfs(self.tree.root, callback=self.perform_assertions)
        except AssertionError as error:
            node = error.args[0]["node"]
            if not isinstance(node.tag, Tag):
                raise \
                    ValueError(f'got unexpected non-terminal token: {node.tag}')
            msg = f"{node.token.value} at line {node.token.line}"
            additional_msg = error.args[0]["message"]
            msg += f' - {additional_msg}'
            if self.filepath is not None:
                msg += f" ({self.filepath}:{node.token.line})"
            raise SemanticError(msg) from error

    def dfs(self, node: Node, siblings: list[Node] = None, callback=None):
        siblings = siblings or []
        callback_name = callback.__name__ if callback is not None else 'default'
        visited = self._visited_nodes.get(callback_name)
        if visited is None:
            self._visited_nodes[callback_name] = {node.__hash__()}
        else:
            self._visited_nodes[callback_name].add(node.__hash__())

        if callback is not None:
            callback(node, siblings)

        for child in node.children:
            if child not in self._visited_nodes[callback_name]:
                self.dfs(child, node.children, callback)

    def perform_assertions(self, node: Node, siblings: list[Node] | None):

        if node.tag is Tag.QUOTE:
            self.__is_in_string_perform_assertions = \
                not self.__is_in_string_perform_assertions
        elif not self.__is_in_string_perform_assertions:

            if node.tag is Tag.SEMICOLON \
                    and siblings[0].tag \
                    in [Tag.FOR, Tag.WHILE, Tag.UNTIL, Tag.IF]:
                self.vars_dict[self.current_scope] = {}
                self.current_scope -= 1
            elif node.tag in [Tag.FOR, Tag.IF, Tag.REPEAT, Tag.WHILE]:
                self.current_scope += 1
                if node.tag is Tag.IF:
                    abstract_expr_node = siblings[1].children[0]
                elif node.tag is Tag.REPEAT:
                    abstract_expr_node = siblings[3]
                elif node.tag is Tag.WHILE:
                    abstract_expr_node = siblings[1]

                if node.tag is not Tag.FOR:
                    self.assert_type_of_expression(abstract_expr_node)

            elif node.tag is Tag.ELSE and not self.__is_in_string:
                self.vars_dict[self.current_scope] = {}
                if siblings[1].children[0].tag is NT.COMPLEX_OP_BODY:
                    child_else_block = siblings[2]
                    assert not child_else_block.children, {
                        'node': child_else_block.children[0],
                        'message': 'multiple else blocks are not allowed'
                    }

            elif node.tag is NT.CALL_ARGS:
                self.check_call_args_for_vars(node)
            elif node.tag in [NT.DEFINE_VAR,
                              NT.DEFINE_VAR_WITHOUT_SEMICOLON,
                              NT.ABSTRACT_STATEMENT,
                              NT.DEFINE_INLINE_VAR]:
                self.assert_type_of_expression(node)

    def check_call_args_for_vars(self, call_args_node: Node):
        if call_args_node.children:
            abstract_expr_node = call_args_node.children[0]
            self.dfs(abstract_expr_node,
                     callback=self._perform_call_args_assertions)

    def _perform_call_args_assertions(self, node: Node, siblings: list[Node]):
        if node.tag is Tag.QUOTE:
            self.__is_in_string = not self.__is_in_string
        elif not self.__is_in_string \
                and node.tag is Tag.ID \
                and not self._is_func_call(node):
            self.assert_var_is_defined(node)
        elif node.tag is NT.CALL_ARGS:
            self.check_call_args_for_vars(node)

    def assert_type_of_expression(self, node: Node):
        assert_func = None
        kwargs = {}

        if node.tag in [NT.DEFINE_VAR, NT.DEFINE_VAR_WITHOUT_SEMICOLON]:
            assert_func = self._assert_type_of_define_var
        elif node.tag is NT.ABSTRACT_STATEMENT:
            abstract_statement_right_node: Node = node.children[1]
            if (manipulate_var_node :=
                abstract_statement_right_node.children[0]).tag \
                    is NT.MANIPULATE_VAR:
                assign_node = manipulate_var_node.children[0].children[0]
                if assign_node.tag is not Tag.ASSIGN:
                    raise \
                        NotImplementedError(f'operational assignments '
                                            f'are not yet implemented '
                                            f'({self.filepath}:'
                                            f'{assign_node.token.line})')
                assert_func = self._assert_type_of_abstract_statement
        elif node.tag is NT.DEFINE_INLINE_VAR:
            assert_func = self._assert_type_of_inline_define_var
        elif node.tag is NT.ABSTRACT_EXPR:
            assert_func = self._assert_abstract_expr_type
            kwargs = {'type': VarType.BOOLEAN}

        if assert_func is not None:
            assert_func(node, **kwargs)

    def _assert_abstract_expr_type(self,
                                   abstract_expr_node: Node,
                                   type: VarType):
        self.right_terminals = []
        self._visited_nodes[self._collect_right_terminals.__name__] = set()
        self.dfs(abstract_expr_node, callback=self._collect_right_terminals)
        self.assert_expr_type(abstract_expr_node, type)

    def _assert_type_of_define_var(self, node: Node):
        left_var = node.children[1]
        self.assert_var_is_not_defined(left_var)
        self.save_var(left_var, type=node.children[3].token.value)

        optional_define_var_assignment_node = node.children[4]
        self.right_terminals = []
        self._visited_nodes[self._collect_right_terminals.__name__] = set()
        self.dfs(optional_define_var_assignment_node,
                 callback=self._collect_right_terminals)

        self.assert_expr_type(left_var)

    def _assert_type_of_inline_define_var(self, node: Node):
        left_var = node.children[1]
        self.assert_var_is_not_defined(left_var)
        node_type = node.children[3].token.value
        assert VarType.from_str(node_type) in \
               [VarType.INTEGER, VarType.CHAR, VarType.BOOLEAN], {
            "node": left_var,
            "message": "iterator of for loop must be integer, char or boolean"
        }
        self.save_var(left_var, node_type)

        define_var_assignment_node = node.children[4]
        self.right_terminals = []
        self._visited_nodes[self._collect_right_terminals.__name__] = set()
        self.dfs(define_var_assignment_node,
                 callback=self._collect_right_terminals)

        self.assert_expr_type(left_var)

        abstract_expr_node = node.parent.children[3]
        self.right_terminals = []
        self._visited_nodes[self._collect_right_terminals.__name__] = set()
        self.dfs(abstract_expr_node, callback=self._collect_right_terminals)

        self.assert_expr_type(left_var)

    def _assert_type_of_abstract_statement(self, node: Node):
        left_var = node.children[0]
        self.assert_var_is_defined(left_var)
        abstract_statement_node = node.children[1]

        self.right_terminals = []
        self._visited_nodes[self._collect_right_terminals.__name__] = set()
        self.dfs(abstract_statement_node,
                 callback=self._collect_right_terminals)

        self.assert_expr_type(left_var)

    def _assert_type_of_abstract_expr(self, node: Node, left_var):
        self.right_terminals = []
        self._visited_nodes[self._collect_right_terminals.__name__] = set()
        self.dfs(node, callback=self._collect_right_terminals)

        self.assert_expr_type(left_var)

    def _collect_right_terminals(self, node: Node, siblings: list[Node] = None):
        if isinstance(node.tag, Tag) and node.tag is not Tag.ASSIGN:
            self.right_terminals.append(node)
            if node.tag is Tag.ID \
                    and not (len(siblings) > 1 and
                             siblings[1].tag is NT.STRING_PART):
                if not self._is_func_call(node):
                    self.assert_var_is_defined(node)

    def _is_func_call(self, id_node):
        try:
            return id_node.parent.children[1].children[0].tag is NT.CALL
        except IndexError:
            return False

    def assert_expr_type(self, node: Node, var_type: VarType = None):
        var_type = var_type or self.get_var_type(node)
        if var_type == VarType.INTEGER:
            IntType.assert_(self.right_terminals,
                            self.vars_dict, self.current_scope)
        elif var_type == VarType.REAL:
            RealType.assert_(self.right_terminals,
                             self.vars_dict, self.current_scope)
        elif var_type == VarType.CHAR:
            CharType.assert_(self.right_terminals,
                             self.vars_dict, self.current_scope)
        elif var_type == VarType.STRING:
            StringType.assert_(self.right_terminals,
                               self.vars_dict, self.current_scope)
        elif var_type == VarType.BOOLEAN:
            BooleanType.assert_(self.right_terminals,
                                self.vars_dict, self.current_scope)
        else:
            raise ValueError(f'unknown type: {var_type}')

    def assert_var_is_defined(self, node_id):
        try:
            self.get_var_type(node_id)
        except ValueError as error:
            raise AssertionError({
                "node": node_id,
                "message": "variable is not defined"
            }) from error

    def assert_var_is_not_defined(self, node_id):
        try:
            self.get_var_type(node_id)
            raise AssertionError({
                "node": node_id,
                "message": "variable is already defined"
            })
        except ValueError:
            pass

    def save_var(self, node, type):
        scoped_vars = self.vars_dict.get(self.current_scope, {})
        scoped_vars[node.token.value] = {'type': VarType.from_str(type)}
        self.vars_dict[self.current_scope] = scoped_vars

    def get_var_type(self, node: Node) -> VarType:
        for i in range(self.current_scope, -1, -1):
            scoped_vars = self.vars_dict.get(i)
            if not scoped_vars:
                continue
            var_data = scoped_vars.get(node.token.value)
            if not var_data:
                continue
            else:
                return var_data["type"]
        raise ValueError(f'variable is not defined: {node.token.value}')
