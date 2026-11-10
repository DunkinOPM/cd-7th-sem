
class GeneralizedBenchmark:

    def count_expression_operations(self, node):
        if node["type"] in ("number", "identifier"):
            return 0

        if node["type"] == "unary":
            return self.count_expression_operations(
                node["operand"]
            )

        if node["type"] == "binary":
            left_count = self.count_expression_operations(
                node["left"]
            )
            right_count = self.count_expression_operations(
                node["right"]
            )

            return left_count + right_count + 1

        raise ValueError(
            f"Unsupported expression type: {node['type']}"
        )

    def compare(
        self,
        coefficient_result,
        index_expressions,
        loop_variables,
        loop_limits,
        array_info
    ):
        if len(loop_variables) != 2 or len(loop_limits) != 2:
            raise ValueError("Exactly two nested loops are supported")

        outer, inner = loop_variables
        outer_limit, inner_limit = loop_limits

        coefficients = coefficient_result["VARPART_coefficients"]

        if set(coefficients) != {outer, inner}:
            raise ValueError("Loop variables do not match coefficients")

        dimensions = array_info[
            coefficient_result["array"]
        ]["dimensions"]

        if len(index_expressions) != len(dimensions):
            raise ValueError("Array dimension mismatch")

        # Check the original index expressions' arithmetic operations.
        index_operations = sum(
            self.count_expression_operations(expression)
            for expression in index_expressions
        )

        # Original address calculation:
        # (dimensions - 1) multiplications for strides,
        # (dimensions - 1) additions to combine offsets,
        # 1 multiplication for element size,
        # 1 addition for the base address.
        dimensions_count = len(dimensions)

        address_operations = (
            dimensions_count + dimensions_count
        )

        original_per_access = (
            index_operations + address_operations
        )

        total_accesses = outer_limit * inner_limit

        original_total = (
            original_per_access * total_accesses
        )

        # Optimized:
        # One outer coefficient multiplication,
        # two additions to calculate the row base,
        # one address increment per inner iteration.
        optimized_setup = outer_limit * 3
        optimized_increments = total_accesses

        optimized_total = (
            optimized_setup + optimized_increments
        )

        reduction = (
            (original_total - optimized_total)
            / original_total * 100
            if original_total else 0
        )

        return {
            "total_accesses": total_accesses,
            "original_per_access": original_per_access,
            "original_total": original_total,
            "optimized_setup": optimized_setup,
            "optimized_increments": optimized_increments,
            "optimized_total": optimized_total,
            "operations_saved": original_total - optimized_total,
            "reduction_percent": round(reduction, 2)
        }
