
from platform import node


class TACGenerator:

    def __init__(self, array_info):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0
        self.array_info = array_info

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instruction):
        self.instructions.append(instruction)

    def generate(self, ast):
        self.generate_statement(ast)
        return self.instructions

    def generate_statement(self, node):

        if node is None:
            return

        node_type = node["type"]

        if node_type == "program":
            for statement in node["body"]:
                self.generate_statement(statement)

        elif node_type == "declaration":
            if node["name"] not in self.array_info:
                self.array_info[node["name"]] = {
                    "type": node["data_type"],
                    "dimensions": node["dimensions"]
                }   

            self.emit(
                f"DECLARE {node['name']} {node['dimensions']}"
            )

        elif node_type == "block":
            for statement in node["body"]:
                self.generate_statement(statement)

        elif node_type == "assignment":
            value = self.generate_expression(node["value"])
            target = self.generate_array_address(node["target"])

            if target["type"] == "scalar":
                self.emit(f"{target['name']} = {value}")
            else:
                self.emit(f"STORE {target['address']}, {value}")

        elif node_type == "variable_declaration":
            value = self.generate_expression(node["value"])
            self.emit(f"{node['name']} = {value}")

        elif node_type == "increment":
            self.emit(f"{node['name']} = {node['name']} + 1")

        elif node_type == "for_loop":
            self.generate_for_loop(node)

    def generate_for_loop(self, node):

        self.generate_statement(node["init"])

        start_label = self.new_label()
        end_label = self.new_label()

        self.emit(f"{start_label}:")

        condition = self.generate_expression(node["condition"])

        self.emit(
            f"IF_FALSE {condition} GOTO {end_label}"
        )

        self.generate_statement(node["body"])

        self.generate_statement(node["update"])

        self.emit(f"GOTO {start_label}")
        self.emit(f"{end_label}:")

    def generate_expression(self, node):

        node_type = node["type"]

        if node_type == "number":
            return str(node["value"])

        if node_type == "identifier":
            return node["name"]

        if node_type == "array_access":
            result = self.generate_array_address(node)
            temp = self.new_temp()

            self.emit(f"{temp} = LOAD {result['address']}")
            return temp

        if node_type == "binary":
            left = self.generate_expression(node["left"])
            right = self.generate_expression(node["right"])

            temp = self.new_temp()

            self.emit(
                f"{temp} = {left} {node['operator']} {right}"
            )

            return temp

        if node_type == "unary":
            operand = self.generate_expression(node["operand"])
            temp = self.new_temp()

            self.emit(f"{temp} = -{operand}")
            return temp

        raise ValueError(f"Unsupported expression: {node_type}")

    def generate_array_address(self, node):

        if node["type"] == "identifier":
            return {
                "type": "scalar",
                "name": node["name"]
            }

        name = node["name"]
        indices = node["indices"]

        if name not in self.array_info:
            raise ValueError(f"Unknown array: {name}")

        dimensions = self.array_info[name]["dimensions"]

        if len(indices) != len(dimensions):
            raise ValueError(
                f"Incorrect number of indices for array {name}"
            )

        linear_index = None

        for index, dimension in zip(indices, dimensions):
            index_value = self.generate_expression(index)

            if linear_index is None:
                linear_index = index_value
            else:
                temp = self.new_temp()
                self.emit(
                    f"{temp} = {linear_index} * {dimension}"
                )

                result = self.new_temp()
                self.emit(
                    f"{result} = {temp} + {index_value}"
                )

                linear_index = result

        element_size = 4

        offset = self.new_temp()
        self.emit(
            f"{offset} = {linear_index} * {element_size}"
        )

        address = self.new_temp()
        self.emit(
            f"{address} = BASE_{name} + {offset}"
        )

        return {
            "type": "array",
            "address": address
        }

    def generate_statement_update(self, node):
        pass
