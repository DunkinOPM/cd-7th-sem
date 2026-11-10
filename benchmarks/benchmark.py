
class Benchmark:

    def compare(self, rows, cols):

        total_accesses = rows * cols

        original = {
            "multiplications": total_accesses * 2,
            "additions": total_accesses * 2
        }

        optimized = {
            "multiplications": rows,
            "additions": rows + total_accesses
        }

        original_total = sum(original.values())
        optimized_total = sum(optimized.values())

        reduction = (
            (original_total - optimized_total)
            / original_total
        ) * 100

        return {
            "total_accesses": total_accesses,
            "original": original,
            "optimized": optimized,
            "original_total": original_total,
            "optimized_total": optimized_total,
            "reduction_percent": round(reduction, 2)
        }
