from transpiler.tree import Node
from transpiler.base import TranspilerEnum


class SharpVarType:
    INT = "int"
    DOUBLE = "double"
    CHAR = "char"
    STRING = "string"
    BOOL = "bool"

    #переделать под TranspilerEnum
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
        self.code = ""

        self.libs = ""
        self.global_vars = ""
        self.main_code = ""

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

    def add_token(self, node: Node, siblings: list[Node], vars_dict, current_scope):

        if node.token.value == "begin":
            self.main_code += "{\n"
            # self.main_code = tw.fill(self.main_code)

        if node.token.value == "end":
            self.main_code += "}\n"
            # self.main_code = tw.fill(self.main_code)

        if node.tag.value == "var":
            # добавить флаг для for
            # для id
            if len(vars_dict[current_scope][siblings[1].token.value]['expr']) == 0:
                define_var = "{0} {1};\n"
                sharp_type = SharpVarType.type_to_sharp(vars_dict[current_scope][siblings[1].token.value]['type'])
                define_var = define_var.format(sharp_type,
                                               siblings[1].token.value)
                self.main_code += define_var

            else:
                define_var = "{0} {1} = {2};\n"
                token_values = []
                for terminal in vars_dict[current_scope][siblings[1].token.value]['expr']:
                    token_values.append(terminal.token.value)

                expression_string = self.parse_expression(token_values)

                sharp_type = SharpVarType.type_to_sharp(vars_dict[current_scope][siblings[1].token.value]['type'].value)
                define_var = define_var.format(sharp_type,
                                               siblings[1].token.value,
                                               expression_string)
                self.main_code += define_var

        if node.tag.value == "for":
            pass

        if node.tag.value == "id":
            pass

    def get_result(self):
        return self.main_template.format(self.libs, self.global_vars, self.main_code)

    def get_libs(self):
        return self.libs

    def get_global_vars(self):
        return self.global_vars

    def get_main_code(self):
        return self.main_code

    def parse_expression(self, terminals: list[Node]) -> str:
        indexes = []
        slices = []
        counter = 0

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
