
class ArrayAnalyzer:

    TYPE_SIZES = {
        "int": 4,
        "float": 4
    }

    def __init__(self):
        self.arrays = {}

    def analyze(self, ast):
        self.arrays = {}
        self._visit(ast)
        return self.arrays

    def _visit(self, node):

        if node is None:
            return

        if isinstance(node, list):
            for item in node:
                self._visit(item)
            return

        if not isinstance(node, dict):
            return

        node_type = node.get("type")

        if node_type == "declaration":
            self._analyze_declaration(node)

        for key, value in node.items():
            if isinstance(value, (dict, list)):
                self._visit(value)

    def _analyze_declaration(self, node):

        name = node["name"]
        data_type = node["data_type"]
        dimensions = node["dimensions"]

        if not dimensions:
            return

        element_size = self.TYPE_SIZES.get(data_type)

        if element_size is None:
            raise ValueError(f"Unsupported array type: {data_type}")

        number_of_dimensions = len(dimensions)

        # Calculate row-major coefficients.
        element_strides = []
        byte_strides = []

        for i in range(number_of_dimensions):
            stride = 1

            for dimension in dimensions[i + 1:]:
                stride *= dimension

            element_strides.append(stride)
            byte_strides.append(stride * element_size)

        total_elements = 1

        for dimension in dimensions:
            if dimension <= 0:
                raise ValueError("Array dimensions must be positive")

            total_elements *= dimension

        self.arrays[name] = {
            "name": name,
            "data_type": data_type,
            "dimensions": dimensions,
            "number_of_dimensions": number_of_dimensions,
            "lower_bounds": [0] * number_of_dimensions,
            "upper_bounds": [d - 1 for d in dimensions],
            "element_size": element_size,
            "total_elements": total_elements,
            "total_size_bytes": total_elements * element_size,
            "element_strides": element_strides,
            "byte_strides": byte_strides,
            "base_address": f"BASE_{name}"
        }
