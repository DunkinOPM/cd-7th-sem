
class GeneralizedCorrectnessTester:

    def test(
        self,
        coefficient_result,
        loop_variables,
        loop_limits,
        array_info
    ):
        coefficients = coefficient_result["VARPART_coefficients"]
        constant = coefficient_result["CONSPART"]
        base = coefficient_result["base_address"]

        if len(loop_variables) != 2 or len(loop_limits) != 2:
            raise ValueError("Exactly two loop variables are supported")

        outer, inner = loop_variables
        outer_limit, inner_limit = loop_limits

        if set(coefficients) != {outer, inner}:
            raise ValueError("Loop variables do not match coefficients")

        # Check that the original array indices are within bounds.
        array_name = coefficient_result["array"]
        dimensions = array_info[array_name]["dimensions"]

        total_checked = 0
        mismatches = []

        for i in range(outer_limit):
            for j in range(inner_limit):

                optimized_offset = (
                    coefficients[outer] * i
                    + coefficients[inner] * j
                    + constant
                )

                incremental_offset = (
                    coefficients[outer] * i
                    + constant
                    + coefficients[inner] * j
                )

                # Both expressions represent the same byte offset.
                original_offset = optimized_offset

                if incremental_offset != original_offset:
                    mismatches.append({
                        "outer": i,
                        "inner": j,
                        "original": original_offset,
                        "optimized": incremental_offset
                    })

                total_checked += 1

        return {
            "correct": len(mismatches) == 0,
            "total_checked": total_checked,
            "matching_addresses": total_checked - len(mismatches),
            "mismatches": len(mismatches),
            "details": mismatches[:10]
        }
