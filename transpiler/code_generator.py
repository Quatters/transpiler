from transpiler.tree import Node
from transpiler.settings import Tag, NT, SHARP_TOKENS


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

class CodeGenerator:

    def __init__(self, source_code: str):
        self.source_code = source_code
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
        self.is_in_string = False
        self.is_in_string_arg = False

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
        if node.tag is Tag.QUOTE and not self.is_inside_args:
            self.is_in_string = not self.is_in_string

        if node.tag is Tag.LBRACKET and node.parent.tag is NT.CALL:
            self.current_call_args_scope += 1
            self.is_inside_args = True

        if node.token.value in [";", "then", "do"] and not self.is_inside_args and not self.is_in_string:
            self.is_inside_command = False
            self.is_char_declaration = False
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

        if node.token.value == "begin" and not self.is_inside_args and not self.is_inside_command:
            self.is_global_vars = False
            self.main_code += self.tabs + "{\n"

        if node.token.value == "end" and not self.is_inside_args and not self.is_inside_command:
            self.main_code += self.tabs + "}\n"

        if node.tag.value == "var" and not self.is_inside_args and not self.is_inside_command:
            self.var_handling()

        if node.tag.value == "if" and not self.is_inside_args and not self.is_inside_command:
            self.if_handling()

        if node.tag.value == "else" and not self.is_inside_args and not self.is_inside_command:
            self.else_handling()

        if node.tag.value == "for" and not self.is_inside_args and not self.is_inside_command:
            self.for_handling()

        if node.tag.value in ["to", "downto"] and not self.is_inside_args and not self.is_inside_command:
            expression_string = self.parse_expression(right_terminals)
            self.for_parts["second"] += expression_string

        if node.tag.value == "while" and not self.is_inside_args and not self.is_inside_command:
            self.is_inside_command = True
            self.while_handling()

        if node.tag.value == "repeat" and not self.is_inside_args and not self.is_inside_command:
            self.repeat_handling()

        if node.tag.value == "until" and not self.is_inside_args and not self.is_inside_command:
            self.until_handling()

        if node.tag.value == "id" and not self.is_inside_command:
            if self.is_inside_args or self.is_func():
                id_name = node.token.value
                if self.is_func():
                    self.function_handling()
                    # id_name = SHARP_TOKENS.get(node.token.value, node.token.value)
                if self.current_call_args_scope == 0:
                    self.main_code += self.tabs + ' ' * 4
            else:
                self.id_handling()

        if self.is_in_string_arg and node.tag is Tag.QUOTE:
            self.is_in_string_arg = False

        # if (self.is_inside_args or self.is_func()) and not self.is_in_string_arg:
        #     if node.tag is Tag.QUOTE and not self.is_inside_command:
        #         self.is_in_string_arg = True
        #         return

        #     self.main_code += self.to_sharp(node)

        # if node.tag is Tag.RBRACKET and node.parent.tag is NT.CALL:
        #     self.current_call_args_scope -= 1
        #     if self.current_call_args_scope == 0:
        #         self.is_inside_args = False

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
            self.is_char_declaration = True

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

    def entered_func(self, node: Node) -> bool:
        return node.tag is Tag.LBRACKET and node.parent.tag is NT.CALL

    def left_func(self, node: Node) -> bool:
        return node.tag is Tag.RBRACKET and node.parent.tag is NT.CALL

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
        func_args = self.parse_expression(self.right_terminals)
        func_name = SHARP_TOKENS.get(self.node.token.value, self.node.token.value)
        self.main_code += self.tabs + 4 * ' ' + f'{func_name}{func_args}'


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

        # indexes = []
        # slices = []
        # counter = 0
        #
        # # добавить игнор для строк
        # terminals = []
        # for terminal in var_expr:
        #     if terminal.token.value in SHARP_FUNCTIONS:
        #         terminals.append(SHARP_FUNCTIONS[terminal.token.value])
        #     elif terminal.token.value.lower() in ['true', 'false']:
        #         terminals.append(terminal.token.value.lower())
        #     else:
        #         terminals.append(terminal.token.value)
        #
        # for i in range(len(terminals)):
        #     if terminals[i] == "'":
        #         indexes.append(i)
        #         counter += 1
        #
        #     if counter == 2:
        #         counter = 0
        #         slices.append(terminals[indexes[-2] + 1:indexes[-1]])
        #
        #     if counter == 0 and terminals[i] != "'":
        #         slices.append(terminals[i])
        #
        # for i in range(len(slices)):
        #     if isinstance(slices[i], str):
        #         # if slices[i] == ""
        #
        #         if slices[i] == ",":
        #             slices[i] = "".join(slices[i] + " ")
        #         elif slices[i] in ['-', '+', '/', '*', 'and', 'or', 'not', '>', '<', '>=', '<=', '=', '<>']:
        #             if slices[i] == 'not':
        #                 slices[i] = SharpOperators.operator_to_sharp(slices[i])
        #             else:
        #                 slices[i] = " " + SharpOperators.operator_to_sharp(slices[i]) + " "
        #         slices[i] = "".join(slices[i])
        #     elif self.is_char_declaration:
        #         self.is_char_declaration = False
        #         slices[i] = "\'" + " ".join(slices[i]) + "\'"
        #     else:
        #         slices[i] = "\"" + " ".join(slices[i]) + "\""
        #
        # return "".join(slices)

        # добавить игнор для строк
        # terminals = []
        # for terminal in var_expr:
        #     if terminal.token.value in SHARP_FUNCTIONS:
        #         terminals.append(SHARP_FUNCTIONS[terminal.token.value])
        #     elif terminal.token.value.lower() in ['true', 'false']:
        #         terminals.append(terminal.token.value.lower())
        #     else:
        #         terminals.append(terminal.token.value)

        # for i in range(len(terminals)):
        #     if terminals[i] == "'":
        #         indexes.append(i)
        #         counter += 1
        #
        #     if counter == 2:
        #         counter = 0
        #         slices.append(terminals[indexes[-2] + 1:indexes[-1]])
        #
        #     if counter == 0 and terminals[i] != "'":
        #         slices.append(terminals[i])

        quote_flag = False
        result = []
        for i, terminal in enumerate(self.right_terminals):
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
            return f" {value}"
        elif node.tag is Tag.COMMA:
            return f"{node.token.value} "
        else:
            value = SHARP_TOKENS.get(node.token.value, node.token.value)
            return value

    def get_string(self, node: Node) -> str:
        string = self.source_code[node.token.pos:self.source_code.index("'", node.token.pos)]
        if self.is_char_declaration:
            return f"'{string}'"
        return f'"{string}"'

    def get_result(self):
        return self.main_template.format(self.libs, self.global_vars, self.main_code)

    def get_libs(self):
        return self.libs

    def get_global_vars(self):
        return self.global_vars

    def get_main_code(self):
        return self.main_code
