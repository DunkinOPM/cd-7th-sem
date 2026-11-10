
class ArrayAddressOptimizer:

    def __init__(self, array_info):
        self.array_info = array_info
        self.optimized_instructions = []

    def optimize_access(self, array_name, indices):
        if array_name not in self.array_info:
            raise ValueError(f"Unknown array: {array_name}")

        info = self.array_info[array_name]

        if len(indices) != info["number_of_dimensions"]:
            raise ValueError("Array index count does not match dimensions")

        strides = info["byte_strides"]

        constant_parts = []
        variable_parts = []

        for index, stride in zip(indices, strides):

            if isinstance(index, (int, float)):
                constant_parts.append(index * stride)

            else:
                variable_parts.append(
                    f"({index} * {stride})"
                )

        constant_part = sum(constant_parts)

        if variable_parts:
            variable_part = " + ".join(variable_parts)
        else:
            variable_part = "0"

        return {
            "array": array_name,
            "base": info["base_address"],
            "CONSPART": constant_part,
            "VARPART": variable_part,
            "address": (
                f"{info['base_address']} + "
                f"({constant_part}) + ({variable_part})"
            )
        }

    def optimize(self, array_name, indices):
        result = self.optimize_access(array_name, indices)

        self.optimized_instructions = [
            f"CONSPART = {result['CONSPART']}",
            f"VARPART = {result['VARPART']}",
            f"ADDRESS = {result['base']} + CONSPART + VARPART"
        ]

        return self.optimized_instructions



class IncrementalAddressOptimizer:

    def __init__(self, array_info):
        self.array_info = array_info

    def optimize_2d_access(
        self,
        array_name,
        row_variable,
        column_variable
    ):

        if array_name not in self.array_info:
            raise ValueError(f"Unknown array: {array_name}")

        info = self.array_info[array_name]

        if info["number_of_dimensions"] != 2:
            raise ValueError("This optimizer currently supports 2D arrays")

        row_stride, column_stride = info["byte_strides"]

        return [
            f"ROW_BASE = BASE_{array_name} + {row_variable} * {row_stride}",
            "ADDRESS = ROW_BASE",
            "INNER_LOOP:",
            "STORE ADDRESS, VALUE",
            f"ADDRESS = ADDRESS + {column_stride}",
            f"{column_variable} = {column_variable} + 1"
        ]
