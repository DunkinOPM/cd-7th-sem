
class CoefficientAnalyzer:

    def analyze_expression(self, node):

        node_type = node["type"]

        if node_type == "number":
            return {"coefficients": {}, "constant": node["value"]}

        if node_type == "identifier":
            return {
                "coefficients": {node["name"]: 1},
                "constant": 0
            }

        if node_type == "unary":
            result = self.analyze_expression(node["operand"])

            if node.get("operator", "-") != "-":
                raise ValueError("Unsupported unary operator")

            return {
                "coefficients": {
                    variable: -coefficient
                    for variable, coefficient
                    in result["coefficients"].items()
                },
                "constant": -result["constant"]
            }

        if node_type == "binary":

            left = self.analyze_expression(node["left"])
            right = self.analyze_expression(node["right"])

            operator = node["operator"]

            if operator == "+":
                return self._add(left, right)

            if operator == "-":
                return self._subtract(left, right)

            if operator == "*":
                if left["coefficients"] and right["coefficients"]:
                    raise ValueError(
                        "Nonlinear expressions are not supported"
                    )

                if left["coefficients"]:
                    return self._multiply(left, right["constant"])

                if right["coefficients"]:
                    return self._multiply(right, left["constant"])

                return {
                    "coefficients": {},
                    "constant": left["constant"] * right["constant"]
                }

            raise ValueError(
                f"Unsupported operator: {operator}"
            )

        raise ValueError(
            f"Unsupported expression type: {node_type}"
        )

    def _add(self, left, right):

        coefficients = left["coefficients"].copy()

        for variable, value in right["coefficients"].items():
            coefficients[variable] = (
                coefficients.get(variable, 0) + value
            )

        return {
            "coefficients": {
                k: v for k, v in coefficients.items() if v != 0
            },
            "constant": left["constant"] + right["constant"]
        }

    def _subtract(self, left, right):

        negative_right = self._multiply(right, -1)

        return self._add(left, negative_right)

    def _multiply(self, expression, constant):

        return {
            "coefficients": {
                variable: coefficient * constant
                for variable, coefficient
                in expression["coefficients"].items()
            },
            "constant": expression["constant"] * constant
        }
