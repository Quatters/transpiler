from transpiler.tree import Node
from transpiler.settings import Tag, NT, SHARP_FUNCTIONS


class SharpVarType:
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


class SharpOperators:
    COMPARE = "=="
    NOTCOMPARE = "!="
    AND = "&&"
    OR = "||"
    NOT = "!"

    @classmethod
    def operator_to_sharp(cls, pas_operator):
        if pas_operator == "=":
            return cls.COMPARE
        if pas_operator == "<>":
            return cls.NOTCOMPARE
        if pas_operator == "and":
            return cls.AND
        if pas_operator == "or":
            return cls.OR
        if pas_operator == "not":
            return cls.NOT
        else:
            return pas_operator


class CodeGenerator:

    def __init__(self):
        self.node = None
        self.vars_dict = {}
        self.siblings = []
        self.right_terminals = []
        self.current_scope = 0
        self.current_call_args_scope = 0
        self.tabs = ""

        self.libs = "using System;\nusing static System.Math;\n"
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
        self.is_inside_args = False
        self.is_inside_for_declaration = False
        self.is_inline_if = False
        self.is_char_declaration = False

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

    def add_token(self, node: Node, siblings: list[Node], vars_dict, current_scope, right_terminals):
        self.node = node
        self.siblings = siblings
        self.vars_dict = vars_dict
        self.current_scope = current_scope
        self.right_terminals = right_terminals
        self.tabs = " " * 8 + (" " * 4) * current_scope
        if node.tag is Tag.LBRACKET and node.parent.tag is NT.CALL:
            self.current_call_args_scope += 1
            self.is_inside_args = True

        if node.token.value in [";", "then", "do"]:
            self.is_inside_command = False
            if node.token.value == ";":
                if self.is_global_vars:
                    self.global_vars += ";\n"
                else:
                    if self.main_code[-2] != "}":
                        self.main_code += ";\n"
            if node.token.value == "do" and self.is_inside_for_declaration:
                self.is_inside_for_declaration = False
                self.main_code += self.for_statement.format(self.for_parts["first"],
                                                            self.for_parts["second"],
                                                            self.for_parts["third"])

        if node.token.value == "begin":
            self.is_global_vars = False
            self.main_code += self.tabs + "{\n"

        if node.token.value == "end":
            self.main_code += self.tabs + "}\n"

        if node.tag.value == "var":
            self.var_handling()

        if node.tag.value == "if":
            self.if_handling()

        if node.tag.value == "else":
            self.else_handling()

        if node.tag.value == "for":
            self.for_handling()

        if node.tag.value in ["to", "downto"]:
            expression_string = self.parse_expression(right_terminals)
            self.for_parts["second"] += expression_string

        if node.tag.value == "while":
            self.is_inside_command = True
            self.while_handling()

        if node.tag.value == "repeat":
            self.repeat_handling()

        if node.tag.value == "until":
            self.until_handling()

        if node.tag.value == "id" and not self.is_inside_command:
            if self.is_inside_args or self.is_func():
                id_name = node.token.value
                if self.is_func():
                    id_name = SHARP_FUNCTIONS[node.token.value]
                if self.current_call_args_scope == 0:
                    self.main_code += self.tabs + ' ' * 4
                self.main_code += id_name
            else:
                self.id_handling()

        if self.is_inside_args or self.is_func():
            if node.tag is Tag.QUOTE and not self.is_inside_command:
                self.main_code += "\""

            if node.tag is Tag.COMMA and not self.is_inside_command:
                self.main_code += ', '

            if node.tag in [Tag.MATH_OPERATOR] and not self.is_inside_command:
                self.main_code += f' {node.token.value} '

            if node.tag in [Tag.BOOLEAN_OPERATOR] and not self.is_inside_command:
                sharp_operator = SharpOperators.operator_to_sharp(node.token.value)
                self.main_code += f' {sharp_operator} '

            if not self.is_inside_command and node.tag in [Tag.LBRACKET, Tag.RBRACKET, Tag.NUMBER_FLOAT, Tag.NUMBER_INT, Tag.BOOLEAN_VALUE]:
                self.main_code += node.token.value

        if node.tag is Tag.RBRACKET and node.parent.tag is NT.CALL:
            self.current_call_args_scope -= 1
            if self.current_call_args_scope == 0:
                self.is_inside_args = False

    def is_func(self) -> bool:
        try:
            return self.siblings[1].children[0].tag is NT.CALL
        except IndexError:
            return False

    def var_handling(self):
        self.is_inside_command = True
        var_type = self.siblings[3].token.value
        var_name = self.siblings[1].token.value
        var_expr = self.right_terminals

        if var_type == "char":
            self.is_char_declaration = True;

        if self.is_inside_for_declaration:
            var_expr = self.vars_dict[self.current_scope][self.siblings[1].token.value]['expr']
            self.for_parts["first"] = self.define_var_with_value(var_type,
                                                                 var_name,
                                                                 var_expr)

        elif self.is_global_vars:
            if len(var_expr) == 0:
                self.global_vars += " " * 8 + self.define_var_without_value(var_type, var_name)
            else:
                self.global_vars += " " * 8 + self.define_var_with_value(var_type,
                                                                        var_name,
                                                                        var_expr)
        else:
            if len(var_expr) == 0:
                self.main_code += self.tabs + " " * 4 + self.define_var_without_value(var_type, var_name)
            else:
                self.main_code += self.tabs + " " * 4 + self.define_var_with_value(var_type,
                                                             var_name,
                                                             var_expr)

    def if_handling(self):
        self.is_inside_command = True
        if_statement = self.tabs + "if ({0})\n"
        expression_string = self.parse_expression(self.right_terminals)
        self.main_code += if_statement.format(expression_string)

    def else_handling(self):
        self.is_inside_command = False
        self.is_inline_if = False
        if self.main_code[-1] != "\n":
            self.main_code += ";\n"
        self.main_code += self.tabs + "else\n"

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

    def id_handling(self):
        self.is_inside_command = True

        assign_var = self.tabs + " " * 4 + "{0} = {1}"
        var_name = self.node.token.value
        var_expr = self.right_terminals
        expression_string = self.parse_expression(var_expr)
        self.main_code += assign_var.format(var_name, expression_string)

    def function_handling(self):
        self.is_inside_command = True
        function_call = "{0}({1})"
        function_name = self.node.token.value


        # function_args =

    def while_handling(self):
        while_statement = self.tabs + "while ({0})\n"
        expression_string = self.parse_expression(self.right_terminals)
        self.main_code += while_statement.format(expression_string)

    def repeat_handling(self):
        self.main_code += self.tabs + "do {\n"
        self.until_expr = self.tabs + "}} while ({0})"

        expression_string = self.parse_expression(self.right_terminals)
        self.until_expr = self.until_expr.format(expression_string)

    def until_handling(self):
        self.is_inside_command = True
        self.main_code += self.until_expr

    def define_var_without_value(self, var_type, var_name):
        define_var = "{0} {1}"
        sharp_type = SharpVarType.type_to_sharp(var_type)
        define_var = define_var.format(sharp_type, var_name)
        return define_var

    def define_var_with_value(self, var_type, var_name, var_expr):
        define_var = "{0} {1} = {2}"
        expression_string = self.parse_expression(var_expr)

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

    def parse_expression(self, var_expr) -> str:

        indexes = []
        slices = []
        counter = 0

        terminals = []
        for terminal in var_expr:
            if terminal.token.value in SHARP_FUNCTIONS:
                terminals.append(SHARP_FUNCTIONS[terminal.token.value])
            elif terminal.token.value.lower() in ['true', 'false']:
                terminals.append(terminal.token.value.lower())
            else:
                terminals.append(terminal.token.value)

        for i in range(len(terminals)):
            if terminals[i] == "'":
                indexes.append(i)
                counter += 1

            if counter == 2:
                counter = 0
                slices.append(terminals[indexes[-2] + 1:indexes[-1]])

            if counter == 0 and terminals[i] != "'":
                slices.append(terminals[i])

        for i in range(len(slices)):
            if isinstance(slices[i], str):
                # if slices[i] == ""

                if slices[i] == ",":
                    slices[i] = "".join(slices[i] + " ")
                elif slices[i] in ['-', '+', '/', '*', 'and', 'or', '>', '<', '>=', '<=', '=', '<>']:
                    slices[i] = " " + SharpOperators.operator_to_sharp(slices[i]) + " "
                slices[i] = "".join(slices[i])
            elif self.is_char_declaration:
                self.is_char_declaration = False
                slices[i] = "\'" + " ".join(slices[i]) + "\'"
            else:
                slices[i] = "\"" + " ".join(slices[i]) + "\""

        return "".join(slices)

    def get_result(self):
        return self.main_template.format(self.libs, self.global_vars, self.main_code)

    def get_libs(self):
        return self.libs

    def get_global_vars(self):
        return self.global_vars

    def get_main_code(self):
        return self.main_code
