
class LoopAnalyzer:

    def __init__(self):
        self.loop_variables = []

    def analyze(self, ast):
        self.loop_variables = []
        self._visit(ast)
        return self.loop_variables

    def _visit(self, node):

        if node is None:
            return

        if isinstance(node, list):
            for item in node:
                self._visit(item)
            return

        if not isinstance(node, dict):
            return

        if node.get("type") == "for_loop":
            self._analyze_loop(node)

        for value in node.values():
            if isinstance(value, (dict, list)):
                self._visit(value)

    def _analyze_loop(self, node):

        init = node.get("init")
        condition = node.get("condition")
        update = node.get("update")

        if not init or not condition or not update:
            return

        if init.get("type") != "variable_declaration":
            return

        variable = init["name"]

        if update.get("type") == "increment":
            increment = 1
        elif update.get("type") == "assignment":
            increment = None
        else:
            increment = None

        self.loop_variables.append({
            "variable": variable,
            "initial_value": init["value"],
            "condition": condition,
            "increment": increment
        })

    def get_loop_order(self):
        return [
            item["variable"]
            for item in self.loop_variables
        ]
