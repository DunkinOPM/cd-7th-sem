
class GeneralizedCorrectnessTester:

    def evaluate_expression(self, node, variables):
        node_type = node["type"]

        if node_type == "number":
            return node["value"]

        if node_type == "identifier":
            name = node["name"]

            if name not in variables:
                raise ValueError(f"Unknown variable: {name}")

            return variables[name]

        if node_type == "unary":
            value = self.evaluate_expression(
                node["operand"], variables
            )

            operator = node.get("operator", "-")

            if operator == "-":
                return -value

            raise ValueError(f"Unsupported unary operator: {operator}")

        if node_type == "binary":
            left = self.evaluate_expression(
                node["left"], variables
            )
            right = self.evaluate_expression(
                node["right"], variables
            )

            operator = node["operator"]

            if operator == "+":
                return left + right
            if operator == "-":
                return left - right
            if operator == "*":
                return left * right

            raise ValueError(f"Unsupported operator: {operator}")

        raise ValueError(f"Unsupported expression type: {node_type}")

    def test(
        self,
        coefficient_result,
        index_expressions,
        loop_variables,
        loop_limits,
        array_info
    ):
        if len(loop_variables) != 2 or len(loop_limits) != 2:
            raise ValueError("Exactly two nested loops are supported")

        array_name = coefficient_result["array"]
        info = array_info[array_name]

        dimensions = info["dimensions"]
        strides = info["byte_strides"]
        lower_bounds = info.get(
            "lower_bounds",
            [0] * len(dimensions)
        )

        if len(index_expressions) != len(dimensions):
            raise ValueError("Array dimension mismatch")

        outer, inner = loop_variables
        outer_limit, inner_limit = loop_limits

        coefficients = coefficient_result["VARPART_coefficients"]
        constant = coefficient_result["CONSPART"]

        if not set(coefficients).issubset(set(loop_variables)):
            raise ValueError("Unexpected coefficient variable")

        total_checked = 0
        matching_addresses = 0
        mismatches = []
        out_of_bounds = []

        for outer_value in range(outer_limit):
            for inner_value in range(inner_limit):

                variables = {
                    outer: outer_value,
                    inner: inner_value
                }

                # Independently evaluate the original AST indices.
                original_indices = [
                    self.evaluate_expression(expression, variables)
                    for expression in index_expressions
                ]

                # Check array bounds.
                valid = True

                for dimension_index, index_value in enumerate(original_indices):
                    lower = lower_bounds[dimension_index]
                    upper = lower + dimensions[dimension_index] - 1

                    if not lower <= index_value <= upper:
                        valid = False
                        out_of_bounds.append({
                            "variables": variables.copy(),
                            "indices": original_indices,
                            "dimension": dimension_index,
                            "invalid_index": index_value,
                            "valid_range": [lower, upper]
                        })

                # Original row-major byte offset.
                original_offset = sum(
                    index_value * stride
                    for index_value, stride
                    in zip(original_indices, strides)
                )

                # Optimized coefficient-based byte offset.
                optimized_offset = constant

                for variable, coefficient in coefficients.items():
                    optimized_offset += (
                        coefficient * variables[variable]
                    )

                total_checked += 1

                if original_offset == optimized_offset:
                    matching_addresses += 1
                else:
                    mismatches.append({
                        "variables": variables.copy(),
                        "original_indices": original_indices,
                        "original_offset": original_offset,
                        "optimized_offset": optimized_offset
                    })

        return {
            "correct": (
                len(mismatches) == 0
                and len(out_of_bounds) == 0
            ),
            "total_checked": total_checked,
            "matching_addresses": matching_addresses,
            "mismatches": len(mismatches),
            "out_of_bounds": len(out_of_bounds),
            "mismatch_details": mismatches[:10],
            "out_of_bounds_details": out_of_bounds[:10]
        }
