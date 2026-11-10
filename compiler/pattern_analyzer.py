
class PatternAnalyzer:

    def analyze(self, ast):

        if ast["type"] != "program":
            raise ValueError("Expected a program AST")

        statements = ast["body"]

        for statement in statements:

            if statement["type"] != "for_loop":
                continue

            outer = statement
            outer_body = outer["body"]["body"]

            for inner in outer_body:

                if inner["type"] != "for_loop":
                    continue

                outer_variable = self._get_loop_variable(outer)
                inner_variable = self._get_loop_variable(inner)

                inner_body = inner["body"]["body"]

                for operation in inner_body:

                    if operation["type"] != "assignment":
                        continue

                    target = operation["target"]

                    if target["type"] != "array_access":
                        continue

                    indices = target["indices"]

                    if len(indices) != 2:
                        continue

                    first_index = indices[0]
                    second_index = indices[1]

                    # Support A[i][j] and A[j][i]
                    if (
                        self._is_identifier(first_index, outer_variable)
                        and self._is_identifier(second_index, inner_variable)
                    ):
                        row_variable = outer_variable
                        column_variable = inner_variable

                    elif (
                        self._is_identifier(first_index, inner_variable)
                        and self._is_identifier(second_index, outer_variable)
                    ):
                        row_variable = inner_variable
                        column_variable = outer_variable

                    else:
                        continue

                    return {
                        "array_name": target["name"],
                        "row_variable": row_variable,
                        "column_variable": column_variable,
                        "row_limit": self._get_limit(
                            outer if row_variable == outer_variable else inner
                        ),
                        "column_limit": self._get_limit(
                            outer if column_variable == outer_variable else inner
                        ),
                        "expression": operation["value"]
                    }

        raise ValueError("Supported nested array assignment pattern not found")

    def _get_loop_variable(self, loop):

        init = loop["init"]

        if init["type"] != "variable_declaration":
            raise ValueError("Loop initialization must declare a variable")

        return init["name"]

    def _get_limit(self, loop):

        condition = loop["condition"]

        if condition["type"] != "binary":
            raise ValueError("Unsupported loop condition")

        if condition["operator"] != "<":
            raise ValueError("Only less-than loop conditions are supported")

        right = condition["right"]

        if right["type"] != "number":
            raise ValueError("Loop limit must be a constant number")

        return right["value"]

    def _is_identifier(self, node, name):

        return (
            node["type"] == "identifier"
            and node["name"] == name
        )


def expression_to_string(node):

    if node["type"] == "number":
        return str(node["value"])

    if node["type"] == "identifier":
        return node["name"]

    if node["type"] == "binary":
        left = expression_to_string(node["left"])
        right = expression_to_string(node["right"])

        return f"({left} {node['operator']} {right})"

    if node["type"] == "unary":
        operand = expression_to_string(node["operand"])
        return f"(-{operand})"

    raise ValueError(
        f"Unsupported expression type: {node['type']}"
    )
