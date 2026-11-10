
class GeneralizedIncrementalGenerator:

    def generate(
        self,
        result,
        loop_variables,
        loop_limits,
        value_expression
    ):
        coefficients = result["VARPART_coefficients"]
        base = result["base_address"]
        constant = result["CONSPART"]

        if len(loop_variables) != 2 or len(loop_limits) != 2:
            raise ValueError("Currently supports exactly two nested loops")

        outer, inner = loop_variables
        outer_limit, inner_limit = loop_limits

        if outer not in coefficients or inner not in coefficients:
            raise ValueError("Missing loop variable coefficient")

        outer_coefficient = coefficients[outer]
        inner_coefficient = coefficients[inner]

        if set(coefficients) != {outer, inner}:
            raise ValueError("Unexpected coefficient variable")

        instructions = [
            f"{outer} = 0",
            "OUTER_LOOP:",
            f"IF {outer} >= {outer_limit} GOTO END",
            f"ROW_BASE = {base} + {outer} * {outer_coefficient} + {constant}",
            f"{inner} = 0",
            "ADDRESS = ROW_BASE",
            "INNER_LOOP:",
            f"IF {inner} >= {inner_limit} GOTO NEXT_ROW",
            f"VALUE = {value_expression}",
            "STORE ADDRESS, VALUE",
            f"{inner} = {inner} + 1",
            f"ADDRESS = ADDRESS + {inner_coefficient}",
            "GOTO INNER_LOOP",
            "NEXT_ROW:",
            f"{outer} = {outer} + 1",
            "GOTO OUTER_LOOP",
            "END:"
        ]

        return instructions
