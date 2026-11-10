
class AddressTransformer:

    def __init__(self, array_info):
        self.array_info = array_info

    def transform(self, array_name, row_variable, column_variable,
                  row_limit, column_limit, expression):

        if array_name not in self.array_info:
            raise ValueError(f"Unknown array: {array_name}")

        info = self.array_info[array_name]

        if info["number_of_dimensions"] != 2:
            raise ValueError("Only 2D arrays are supported")

        row_stride, column_stride = info["byte_strides"]

        if row_stride != info["dimensions"][1] * column_stride:
            raise ValueError("Invalid row-major stride information")

        return [
            f"{row_variable} = 0",
            "OUTER_LOOP:",
            f"IF {row_variable} >= {row_limit} GOTO END",
            f"ROW_BASE = BASE_{array_name} + {row_variable} * {row_stride}",
            f"{column_variable} = 0",
            "ADDRESS = ROW_BASE",
            "INNER_LOOP:",
            f"IF {column_variable} >= {column_limit} GOTO NEXT_ROW",
            f"VALUE = {expression}",
            "STORE ADDRESS, VALUE",
            f"{column_variable} = {column_variable} + 1",
            f"ADDRESS = ADDRESS + {column_stride}",
            "GOTO INNER_LOOP",
            "NEXT_ROW:",
            f"{row_variable} = {row_variable} + 1",
            "GOTO OUTER_LOOP",
            "END:"
        ]
