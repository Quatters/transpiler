from transpiler.tree import Node
from transpiler.base import TranspilerEnum


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

        self.libs = ""
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

    # каррент скоуп возможно понадобится для расстановки табов
    def add_token(self, node: Node, siblings: list[Node], vars_dict, current_scope, right_terminals):
        self.node = node
        self.siblings = siblings
        self.vars_dict = vars_dict
        self.current_scope = current_scope
        self.right_terminals = right_terminals

        if node.token.value in [";", "then", "do"]:
            self.is_inside_command = False
            if node.token.value == ";":
                self.main_code += ";\n"
            if node.token.value == "do" and self.is_inside_for_declaration:
                self.is_inside_for_declaration = False
                self.main_code += self.for_statement.format(self.for_parts["first"],
                                                            self.for_parts["second"],
                                                            self.for_parts["third"])

        if node.token.value == "begin":
            self.is_global_vars = False
            self.main_code += "{\n"

        if node.token.value == "end":
            self.main_code += "}\n"

        if node.tag.value == "var":
            self.var_handling()

        if node.tag.value == "if":
            self.if_handling()

        if node.tag.value == "else":
            self.else_handling()

        if node.tag.value == "for":
            self.for_handling()

        if node.tag.value == "to":
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
            self.id_handling()

    def var_handling(self):
        self.is_inside_command = True
        var_type = self.siblings[3].token.value
        # var_type = vars_dict[current_scope][siblings[1].token.value]['type'].value
        var_name = self.siblings[1].token.value
        var_expr = self.right_terminals
        # var_expr = vars_dict[current_scope][siblings[1].token.value]['expr']
        if self.is_inside_for_declaration:
            var_expr = self.vars_dict[self.current_scope][self.siblings[1].token.value]['expr']
            self.for_parts["first"] = self.define_var_with_value(var_type,
                                                                 var_name,
                                                                 var_expr)

        elif self.is_global_vars:
            if len(var_expr) == 0:
                self.global_vars += self.define_var_without_value(var_type, var_name)
            else:
                self.global_vars += self.define_var_with_value(var_type,
                                                               var_name,
                                                               var_expr)
        else:
            if len(var_expr) == 0:
                self.main_code += self.define_var_without_value(var_type, var_name)
            else:
                self.main_code += self.define_var_with_value(var_type,
                                                             var_name,
                                                             var_expr)

    def if_handling(self):
        self.is_inside_command = True
        if_statement = "if ({0})\n"
        expression_string = self.parse_expression(self.right_terminals)
        self.main_code += if_statement.format(expression_string)

    def else_handling(self):
        self.main_code += "else "

    def for_handling(self):
        self.is_inside_command = True
        self.is_inside_for_declaration = True
        self.for_statement = "for ({0}; {1}; {2})\n"
        var_name = self.siblings[1].children[1].token.value
        if self.siblings[2].children[0].token.value == "to":
            self.for_parts["third"] = var_name + "++"
            self.for_parts["second"] = var_name + " <= "
        else:
            self.for_parts["third"] = var_name + "--"
            self.for_parts["second"] = var_name + " >= "

    def id_handling(self):
        self.is_inside_command = True

        assign_var = "{0} = {1}\n"
        var_name = self.node.token.value
        var_expr = self.right_terminals
        expression_string = self.parse_expression(var_expr)
        self.main_code += assign_var.format(var_name, expression_string)

    def while_handling(self):
        while_statement = "while ({0})\n"
        expression_string = self.parse_expression(self.right_terminals)
        self.main_code += while_statement.format(expression_string)

    def repeat_handling(self):
        self.main_code += "do {\n"
        self.until_expr = "}} while ({0})\n"

        expression_string = self.parse_expression(self.right_terminals)
        self.until_expr = self.until_expr.format(expression_string)

    def until_handling(self):
        self.is_inside_command = True
        self.main_code += self.until_expr

    def define_var_without_value(self, var_type, var_name):
        define_var = "{0} {1}"
        # if len(self.siblings) < 4:
        #     define_var += "\n"
        sharp_type = SharpVarType.type_to_sharp(var_type)
        define_var = define_var.format(sharp_type, var_name)
        return define_var

    def define_var_with_value(self, var_type, var_name, var_expr):
        define_var = "{0} {1} = {2}"
        # if len(self.siblings) < 6 and not self.is_inside_for_declaration:
        #     define_var += "\n"
        expression_string = self.parse_expression(var_expr)

        sharp_type = SharpVarType.type_to_sharp(var_type)
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
                slices[i] = SharpOperators.operator_to_sharp(slices[i])
                slices[i] = "".join(slices[i])
            elif len(slices[i]) == 1 and len(slices[i][0]) == 1:
                slices[i] = "\'" + " ".join(slices[i]) + "\'"
            else:
                slices[i] = "\"" + " ".join(slices[i]) + "\""

        return " ".join(slices)

    def get_result(self):
        return self.main_template.format(self.libs, self.global_vars, self.main_code)

    def get_libs(self):
        return self.libs

    def get_global_vars(self):
        return self.global_vars

    def get_main_code(self):
        return self.main_code


# заметки: возможно не понадобится использовать варс дикт