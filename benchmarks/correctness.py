
class CorrectnessTester:

    def __init__(self, array_info):
        self.array_info = array_info

    def test(self, array_name, rows, cols, expression_ast,
             row_variable, column_variable):

        info = self.array_info[array_name]

        if info["dimensions"] != [rows, cols]:
            raise ValueError("Test bounds must match array dimensions")

        element_size = info["element_size"]
        row_stride, column_stride = info["byte_strides"]

        original = {}
        optimized = {}

        for i in range(rows):
            for j in range(cols):
                env = {row_variable: i, column_variable: j}
                value = self.evaluate(expression_ast, env)

                address = (i * cols + j) * element_size
                original[address] = value

        for i in range(rows):
            row_base = i * row_stride
            address = row_base

            for j in range(cols):
                env = {row_variable: i, column_variable: j}
                value = self.evaluate(expression_ast, env)

                optimized[address] = value
                address += column_stride

        mismatches = [
            address for address in original
            if original[address] != optimized.get(address)
        ]

        return {
            "correct": original == optimized,
            "elements_tested": rows * cols,
            "mismatches": len(mismatches),
            "sample_original": list(original.items())[:5],
            "sample_optimized": list(optimized.items())[:5]
        }

    def evaluate(self, node, env):

        node_type = node["type"]

        if node_type == "number":
            return node["value"]

        if node_type == "identifier":
            return env[node["name"]]

        if node_type == "binary":
            left = self.evaluate(node["left"], env)
            right = self.evaluate(node["right"], env)

            op = node["operator"]

            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if op == "/":
                return left / right

        if node_type == "unary" and node["operator"] == "-":
            return -self.evaluate(node["operand"], env)

        raise ValueError(f"Unsupported expression: {node_type}")
