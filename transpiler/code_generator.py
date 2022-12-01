from transpiler.tree import Node
from transpiler.base import TranspilerEnum


class SharpVarType(TranspilerEnum):
    INT = "int"
    DOUBLE = "double"
    CHAR = "char"
    STRING = "string"
    BOOL = "bool"

    #переделать под TranspilerEnum
    @classmethod
    def type_to_sharp(cls, pas_type):
        if pas_type.value == "integer":
            return cls.INT
        if pas_type.value == "real":
            return cls.DOUBLE
        if pas_type.value == "char":
            return cls.CHAR
        if pas_type.value == "string":
            return cls.STRING
        if pas_type.value == "boolean":
            return cls.BOOL


class CodeGenerator:

    def __init__(self):
        self.code = ""

        self.libs = "lib"
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


                string_token_values = ''.join(token_values)
                # string_token_values = ' '.join(token_values)

                sharp_type = SharpVarType.type_to_sharp(vars_dict[current_scope][siblings[1].token.value]['type'])
                define_var = define_var.format(sharp_type,
                                               siblings[1].token.value,
                                               string_token_values)
                self.main_code += define_var

        if node.tag.value == "for":
            pass

        if node.tag.value == "id":
            pass

    def get_result(self):
        return self.main_template.format(self.libs, self.global_vars, self.main_code).strip()

    def find_char(self, terminals):
        pass