
from compiler.coefficient_analyzer import CoefficientAnalyzer


class AddressCoefficientCalculator:

    def __init__(self, array_info):
        self.array_info = array_info
        self.analyzer = CoefficientAnalyzer()

    def calculate(self, array_name, index_expressions):

        if array_name not in self.array_info:
            raise ValueError(f"Unknown array: {array_name}")

        info = self.array_info[array_name]

        strides = info["byte_strides"]

        if len(index_expressions) != len(strides):
            raise ValueError("Array dimension mismatch")

        final_coefficients = {}
        constant_part = 0

        for index, stride in zip(index_expressions, strides):

            result = self.analyzer.analyze_expression(index)

            constant_part += result["constant"] * stride

            for variable, coefficient in result["coefficients"].items():

                final_coefficients[variable] = (
                    final_coefficients.get(variable, 0)
                    + coefficient * stride
                )

        final_coefficients = {
            variable: coefficient
            for variable, coefficient in final_coefficients.items()
            if coefficient != 0
        }

        return {
            "array": array_name,
            "base_address": info["base_address"],
            "CONSPART": constant_part,
            "VARPART_coefficients": final_coefficients
        }
