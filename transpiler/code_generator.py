from transpiler.base import TranspilerEnum
from transpiler.tree import Node
from transpiler.settings import Tag, NT, SHARP_TOKENS


class SharpVarType(TranspilerEnum):
    INT = "int"
    DOUBLE = "double"
    CHAR = "char"
    STRING = "string"
    BOOL = "bool"

    @classmethod
    def type_to_sharp(cls, pas_type):
        if pas_type == "integer":
            return cls.INT
        if pas_type == "real":
            return cls.DOUBLE
        if pas_type == "char":
            return cls.CHAR
        if pas_type == "string":
            return cls.STRING
        if pas_type == "boolean":
            return cls.BOOL


class CodeGenerator:

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.node = None
        self.vars_dict = {}
        self.siblings = []
        self.current_scope = 0
        self.current_call_args_scope = 0
        self.tabs = ""

        self.libs = "using System;\n"
        self.global_vars = ""
        self.main_code = ""

        self.for_statement = ""
        self.for_parts = {
            "first": "",
            "second": "",
            "third": ""
        }

        self.until_expr = ""

        self.is_global_vars = True
        self.is_inside_command = False
        self.is_inside_for_declaration = False
        self.is_char_declaration = False
        self.is_in_string = False

        self.main_template = """
{0}
namespace Transpiler
{{
    internal class Program
    {{
{1}
        public static void Main(string[] args)
{2}
    }}
}}
"""

    def add_token(self, node: Node,
                  siblings: list[Node],
                  vars_dict,
                  current_scope,
                  right_terminals):
        self.node = node
        self.siblings = siblings
        self.vars_dict = vars_dict
        self.current_scope = current_scope
        self.tabs = " " * 8 + (" " * 4) * current_scope

        if node.tag is Tag.QUOTE:
            self.is_in_string = not self.is_in_string

        if node.tag in [Tag.SEMICOLON, Tag.THEN, Tag.DO]\
                and not self.is_in_string:
            self.is_inside_command = False
            self.is_char_declaration = False
            if node.tag is Tag.SEMICOLON:
                if self.is_global_vars:
                    self.global_vars += ";\n"
                else:
                    if self.main_code[-2] != "}":
                        self.main_code += ";\n"
            if node.tag is Tag.DO and self.is_inside_for_declaration:
                self.is_inside_for_declaration = False
                self.main_code += \
                    self.for_statement.format(self.for_parts["first"],
                                              self.for_parts["second"],
                                              self.for_parts["third"])

        if node.tag is Tag.BEGIN and not self.is_in_string:
            self.is_global_vars = False
            self.main_code += self.tabs + "{\n"

        if node.tag is Tag.END and not self.is_in_string:
            self.main_code += self.tabs + "}\n"

        if node.tag is Tag.VAR and not self.is_in_string:
            if self.is_inside_for_declaration:
                var_name = self.siblings[1].token.value
                right_terminals = \
                    self.vars_dict[current_scope][var_name]['expr']
            self.var_handling(right_terminals)

        if node.tag is Tag.IF and not self.is_in_string:
            self.if_handling(right_terminals)

        if node.tag is Tag.ELSE and not self.is_in_string:
            self.else_handling()

        if node.tag is Tag.FOR and not self.is_in_string:
            self.for_handling()

        if node.tag in [Tag.TO, Tag.DOWNTO] and not self.is_in_string:
            expression_string = self.parse_expression(right_terminals)
            self.for_parts["second"] += expression_string

        if node.tag is Tag.WHILE and not self.is_in_string:
            self.while_handling(right_terminals)

        if node.tag is Tag.REPEAT and not self.is_in_string:
            self.repeat_handling(right_terminals)

        if node.tag is Tag.UNTIL and not self.is_in_string:
            self.until_handling()

        if node.tag is Tag.ID \
                and not self.is_in_string \
                and not self.is_inside_command:
            if self.is_func():
                self.function_handling(right_terminals)
            else:
                self.id_handling(right_terminals)

    def is_func(self) -> bool:
        try:
            return self.siblings[1].children[0].tag is NT.CALL
        except IndexError:
            return False

    def var_handling(self, right_terminals):
        self.is_inside_command = True
        var_type = self.siblings[3].token.value
        var_name = self.siblings[1].token.value
        var_expr = right_terminals

        if var_type == "char":
            self.is_char_declaration = True

        if self.is_inside_for_declaration:
            self.for_parts["first"] = \
                self.define_var_with_value(var_type,
                                           var_name,
                                           right_terminals)

        elif self.is_global_vars:
            if len(var_expr) == 0:
                self.global_vars += " " * 8 + \
                                    "static " + \
                                    self.define_var_without_value(var_type,
                                                                  var_name)
            else:
                self.global_vars += " " * 8 + \
                                    "static " + \
                                    self.define_var_with_value(var_type,
                                                               var_name,
                                                               right_terminals)
        else:
            if len(var_expr) == 0:
                self.main_code += self.tabs + " " * 4 \
                    + self.define_var_without_value(
                        var_type,
                        var_name
                    )
            else:
                self.main_code += self.tabs + " " * 4 \
                    + self.define_var_with_value(
                        var_type,
                        var_name,
                        right_terminals
                    )

    def if_handling(self, right_terminals):
        self.is_inside_command = True
        if_statement = "if ({0})\n"
        if len(self.siblings) != 2:
            if_statement = self.tabs + if_statement
        expression_string = self.parse_expression(right_terminals)
        self.main_code += if_statement.format(expression_string)

    def else_handling(self):
        self.is_inside_command = False
        if self.main_code[-1] != "\n":
            self.main_code += ";\n"

        self.main_code += self.tabs + "else"
        if self.siblings[1].children[0].tag is not Tag.IF:
            self.main_code += '\n'
        else:
            self.main_code += ' '

    def for_handling(self):
        self.is_inside_command = True
        self.is_inside_for_declaration = True
        self.for_statement = self.tabs + "for ({0}; {1}; {2})\n"
        var_name = self.siblings[1].children[1].token.value
        if self.siblings[2].children[0].token.value == "to":
            self.for_parts["third"] = var_name + "++"
            self.for_parts["second"] = var_name + " <= "
        else:
            self.for_parts["third"] = var_name + "--"
            self.for_parts["second"] = var_name + " >= "

    def id_handling(self, right_terminals):
        self.is_inside_command = True

        for i in range(self.current_scope, -1, -1):
            scoped_vars = self.vars_dict.get(i)
            if not scoped_vars:
                continue
            var_data = scoped_vars.get(self.node.token.value)
            if not var_data:
                continue
            else:
                if var_data["type"].value == "char":
                    self.is_char_declaration = True

        assign_var = self.tabs + " " * 4 + "{0} = {1}"
        var_name = self.node.token.value
        expression_string = self.parse_expression(right_terminals)
        self.main_code += assign_var.format(var_name, expression_string)

    def function_handling(self, right_terminals):
        self.is_inside_command = True
        func_args = self.parse_expression(right_terminals)
        func_name = SHARP_TOKENS.get(self.node.token.value,
                                     self.node.token.value)
        self.main_code += self.tabs + 4 * ' ' + f'{func_name}{func_args}'

    def while_handling(self, right_terminals):
        self.is_inside_command = True
        while_statement = self.tabs + "while ({0})\n"
        expression_string = self.parse_expression(right_terminals)
        self.main_code += while_statement.format(expression_string)

    def repeat_handling(self, right_terminals):
        self.main_code += self.tabs + "do {\n"
        self.until_expr = self.tabs + "}} while ({0})"

        expression_string = self.parse_expression(right_terminals)
        self.until_expr = self.until_expr.format(expression_string)

    def until_handling(self):
        self.is_inside_command = True
        self.main_code += self.until_expr

    def define_var_without_value(self, var_type, var_name):
        define_var = "{0} {1}"
        sharp_type = SharpVarType.type_to_sharp(var_type)
        define_var = define_var.format(sharp_type, var_name)
        return define_var

    def define_var_with_value(self, var_type, var_name, right_terminals):
        define_var = "{0} {1} = {2}"
        expression_string = self.parse_expression(right_terminals)

        sharp_type = SharpVarType.type_to_sharp(var_type)
        if self.is_inside_for_declaration:
            define_var = define_var.format(sharp_type,
                                           var_name,
                                           expression_string)
        else:
            define_var = define_var.format(sharp_type,
                                           var_name,
                                           expression_string)
        return define_var

    def parse_expression(self, right_terminals) -> str:
        quote_flag = False
        result = []
        for i, terminal in enumerate(right_terminals):
            if quote_flag:
                if terminal.tag is Tag.QUOTE:
                    quote_flag = False
                continue
            if terminal.tag is Tag.QUOTE:
                result.append(self.get_string(terminal))
                quote_flag = True
            else:
                result.append(self.to_sharp(terminal))

        return "".join(result)

    def to_sharp(self, node: Node) -> str:
        if node.tag in [Tag.MATH_OPERATOR, Tag.BOOLEAN_OPERATOR, Tag.COMPARE]:
            value = SHARP_TOKENS.get(node.token.value, node.token.value)
            return f" {value} "
        elif node.tag is Tag.BOOLEAN_NOT:
            value = SHARP_TOKENS.get(node.token.value, node.token.value)
            if self.main_code[-1] != ' ':
                return f"{value}"
            return f" {value}"
        elif node.tag is Tag.COMMA:
            return f"{node.token.value} "
        elif node.tag is Tag.BOOLEAN_VALUE:
            return node.token.value.lower()
        else:
            value = SHARP_TOKENS.get(node.token.value, node.token.value)
            return value

    def get_string(self, node: Node) -> str:
        pos = node.token.pos
        string = self.source_code[pos:self.source_code.index("'",
                                                             node.token.pos)]
        if self.is_char_declaration:
            return f"'{string}'"
        return f'"{string}"'

    def get_result(self):
        return self.main_template.format(self.libs,
                                         self.global_vars,
                                         self.main_code)

    def get_libs(self):
        return self.libs

    def get_global_vars(self):
        return self.global_vars

    def get_main_code(self):
        return self.main_code
