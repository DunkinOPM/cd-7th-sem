



class LoopInterchange:

    def interchange(self, ast):
        if ast.get("type") != "program":
            raise ValueError("Expected a program AST")

        for statement in ast["body"]:
            if statement.get("type") != "for_loop":
                continue

            outer = statement
            outer_body = outer["body"].get("body", [])

            for inner in outer_body:
                if inner.get("type") != "for_loop":
                    continue

                self._validate_loop(outer)
                self._validate_loop(inner)

                outer_limit = outer["condition"]["right"]["value"]
                inner_limit = inner["condition"]["right"]["value"]

                if outer_limit != inner_limit:
                    raise ValueError(
                        "Loop interchange requires equal iteration counts in this version"
                    )

                outer_var = outer["init"]["name"]
                inner_var = inner["init"]["name"]

                assignments = inner["body"].get("body", [])

                if len(assignments) != 1:
                    raise ValueError(
                        "Only one assignment inside the inner loop is supported"
                    )

                assignment = assignments[0]

                if assignment.get("type") != "assignment":
                    raise ValueError("Expected an assignment inside the loop")

                target = assignment["target"]

                if target.get("type") != "array_access":
                    raise ValueError("Expected an array access assignment")

                indices = target["indices"]

                if len(indices) != 2:
                    raise ValueError("Only 2D arrays are supported")

                if not (
                    self._is_identifier(indices[0], inner_var)
                    and self._is_identifier(indices[1], outer_var)
                ):
                    raise ValueError(
                        "Unsupported index pattern. Expected A[inner][outer]."
                    )

                self._check_expression(
                    assignment["value"], outer_var, inner_var
                )

                # Original outer loop becomes the new inner loop
                new_inner = {
                    **outer,
                    "body": inner["body"]
                }

                # Original inner loop becomes the new outer loop
                new_outer = {
                    **inner,
                    "body": {
                        "type": "block",
                        "body": [new_inner]
                    }
                }

                new_ast = {
                    **ast,
                    "body": list(ast["body"])
                }

                new_ast["body"][new_ast["body"].index(outer)] = new_outer

                return {
                    "optimized_ast": new_ast,
                    "outer_variable": inner_var,
                    "inner_variable": outer_var,
                    "status": "interchanged"
                }

        raise ValueError("No supported nested loop found")

    def _validate_loop(self, loop):
        init = loop["init"]
        condition = loop["condition"]
        update = loop["update"]

        if init.get("type") != "variable_declaration":
            raise ValueError("Unsupported loop initialization")

        if init["value"].get("type") != "number":
            raise ValueError("Loop must start with a constant")

        if init["value"]["value"] != 0:
            raise ValueError("Loop must start at zero")

        if condition.get("type") != "binary":
            raise ValueError("Unsupported loop condition")

        if condition["operator"] != "<":
            raise ValueError("Loop condition must use <")

        if not self._is_identifier(condition["left"], init["name"]):
            raise ValueError("Loop condition variable mismatch")

        if condition["right"].get("type") != "number":
            raise ValueError("Loop limit must be constant")

        if update.get("type") != "increment":
            raise ValueError("Loop must use increment")

        if update["name"] != init["name"]:
            raise ValueError("Loop update variable mismatch")

    def _is_identifier(self, node, name):
        return (
            node.get("type") == "identifier"
            and node.get("name") == name
        )

    def _check_expression(self, node, outer_var, inner_var):
        node_type = node.get("type")

        if node_type in ("number", "identifier"):
            return

        if node_type == "binary":
            self._check_expression(
                node["left"], outer_var, inner_var
            )
            self._check_expression(
                node["right"], outer_var, inner_var
            )
            return

        raise ValueError("Unsupported expression for loop interchange")
