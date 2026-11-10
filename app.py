
import re
import streamlit as st
import pandas as pd

from compiler.lexer import tokenize
from compiler.parser import parse_source
from compiler.tac_generator import TACGenerator
from compiler.array_analyzer import ArrayAnalyzer
from compiler.address_coefficient_calculator import AddressCoefficientCalculator
from compiler.generalized_address_generator import GeneralizedAddressGenerator
from compiler.generalized_incremental_generator import GeneralizedIncrementalGenerator

from benchmarks.generalized_correctness import GeneralizedCorrectnessTester
from benchmarks.generalized_benchmark import GeneralizedBenchmark


st.set_page_config(
    page_title="Array Compiler Optimizer",
    page_icon="⚙️",
    layout="wide"
)

st.title("Array Compiler Optimizer")
st.caption("Intermediate Code Optimization for Multidimensional Arrays")


default_code = """int A[298][303];

for (int i = 0; i < 100; i++) {
    for (int j = 0; j < 100; j++) {
        A[2*i + j][3*j + 5] = i + j;
    }
}"""

source_code = st.text_area(
    "Enter your C-like source code",
    value=default_code,
    height=250
)


def find_array_assignment(ast):
    for statement in ast.get("body", []):
        if statement.get("type") != "for_loop":
            continue

        for inner in statement.get("body", {}).get("body", []):
            if inner.get("type") != "for_loop":
                continue

            for operation in inner.get("body", {}).get("body", []):
                if (
                    operation.get("type") == "assignment"
                    and operation.get("target", {}).get("type")
                    == "array_access"
                ):
                    return operation

    raise ValueError("No nested array assignment found")


def extract_loop_details(source):
    loops = re.findall(
        r"for\s*\(\s*int\s+(\w+)\s*=\s*0\s*;\s*\w+\s*<\s*(\d+)",
        source
    )

    if len(loops) < 2:
        raise ValueError(
            "Expected two nested loops starting at zero"
        )

    return (
        [loops[0][0], loops[1][0]],
        [int(loops[0][1]), int(loops[1][1])]
    )


def expression_to_string(node):
    node_type = node["type"]

    if node_type == "number":
        return str(node["value"])

    if node_type == "identifier":
        return node["name"]

    if node_type == "binary":
        left = expression_to_string(node["left"])
        right = expression_to_string(node["right"])

        return f"({left} {node['operator']} {right})"

    if node_type == "unary":
        return f"-{expression_to_string(node['operand'])}"

    raise ValueError(
        f"Unsupported expression type: {node_type}"
    )


if st.button(
    "Run Compiler and Optimize",
    type="primary",
    width="stretch"
):

    try:
        # 1. Lexical Analysis
        st.header("1. Lexical Analysis")

        tokens = tokenize(source_code)

        st.success(f"Generated {len(tokens)} tokens")

        df = pd.DataFrame(tokens)
        df["value"] = df["value"].astype(str)

        st.dataframe(df, width="stretch")

        # 2. Syntax Analysis
        st.header("2. Syntax Analysis")

        ast = parse_source(source_code)

        st.success("Syntax analysis successful")

        with st.expander("View Abstract Syntax Tree"):
            st.json(ast)

        # 3. Array Analysis
        st.header("3. Array Analysis")

        array_info = ArrayAnalyzer().analyze(ast)

        for name, info in array_info.items():
            st.subheader(f"Array: {name}")
            st.json(info)

        # 4. Original TAC
        st.header("4. Original Three-Address Code")

        original_tac = TACGenerator({}).generate(ast)

        st.code("\n".join(original_tac), language="text")

        assignment = find_array_assignment(ast)

        array_name = assignment["target"]["name"]
        index_expressions = assignment["target"]["indices"]

        # 5. Generalized Address Coefficient Optimization
        st.header("5. Generalized Address Coefficient Optimization")

        generalized_result = None

        try:
            calculator = AddressCoefficientCalculator(array_info)

            generalized_result = calculator.calculate(
                array_name,
                index_expressions
            )

            st.success(
                "Generalized coefficients calculated successfully"
            )

            st.subheader("CONSPART / VARPART")
            st.json(generalized_result)

            address_generator = GeneralizedAddressGenerator()

            generalized_tac = address_generator.generate(
                generalized_result
            )

            st.subheader("Generated Address Instructions")

            st.code(
                "\n".join(generalized_tac),
                language="text"
            )

        except Exception as error:
            st.error(
                f"Generalized coefficient optimization error: {error}"
            )

        # 6. Generalized Incremental Address Optimization
        st.header("6. Generalized Incremental Address Optimization")

        loop_variables = None
        loop_limits = None

        if generalized_result is not None:
            try:
                loop_variables, loop_limits = extract_loop_details(
                    source_code
                )

                value_expression = expression_to_string(
                    assignment["value"]
                )

                incremental_generator = (
                    GeneralizedIncrementalGenerator()
                )

                incremental_tac = incremental_generator.generate(
                    generalized_result,
                    loop_variables,
                    loop_limits,
                    value_expression
                )

                st.success(
                    "Generalized incremental address generation completed"
                )

                st.code(
                    "\n".join(incremental_tac),
                    language="text"
                )

            except Exception as error:
                st.info(
                    f"Incremental optimization unavailable: {error}"
                )

        # 7. Independent Generalized Correctness Verification
        st.header("7. Generalized Correctness Verification")

        if generalized_result is not None and loop_variables is not None:
            try:
                tester = GeneralizedCorrectnessTester()

                verification = tester.test(
                    coefficient_result=generalized_result,
                    index_expressions=index_expressions,
                    loop_variables=loop_variables,
                    loop_limits=loop_limits,
                    array_info=array_info
                )

                if verification["correct"]:
                    st.success(
                        "Independent correctness verification passed"
                    )
                else:
                    st.error(
                        "Correctness verification failed"
                    )

                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "Addresses Checked",
                    verification["total_checked"]
                )

                col2.metric(
                    "Matching Addresses",
                    verification["matching_addresses"]
                )

                col3.metric(
                    "Mismatches",
                    verification["mismatches"]
                )

                col4.metric(
                    "Out-of-Bounds",
                    verification["out_of_bounds"]
                )

                with st.expander("Verification Details"):
                    st.json(verification)

            except Exception as error:
                st.warning(
                    f"Correctness verification unavailable: {error}"
                )

        else:
            st.info(
                "Correctness verification skipped because "
                "generalized address optimization was unavailable."
            )

        # 8. Generalized Performance Comparison
        st.header("8. Generalized Performance Comparison")

        if (
            generalized_result is not None
            and loop_variables is not None
            and loop_limits is not None
        ):
            try:
                benchmark = GeneralizedBenchmark()

                results = benchmark.compare(
                    coefficient_result=generalized_result,
                    index_expressions=index_expressions,
                    loop_variables=loop_variables,
                    loop_limits=loop_limits,
                    array_info=array_info
                )

                st.success(
                    "Generalized performance comparison completed"
                )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Array Accesses",
                    results["total_accesses"]
                )

                col2.metric(
                    "Original Operations",
                    results["original_total"]
                )

                col3.metric(
                    "Optimized Operations",
                    results["optimized_total"]
                )

                st.subheader("Operation Count Comparison")

                chart_data = pd.DataFrame({
                    "Operations": [
                        results["original_total"],
                        results["optimized_total"]
                    ]
                }, index=["Original", "Optimized"])

                st.bar_chart(chart_data)

                col1, col2 = st.columns(2)

                col1.metric(
                    "Operations Saved",
                    results["operations_saved"]
                )

                col2.metric(
                    "Estimated Reduction",
                    f"{results['reduction_percent']}%"
                )

                with st.expander("Detailed Benchmark Results"):
                    st.json(results)

                st.caption(
                    "Static address-calculation operation-count estimate. "
                    "This is not measured execution time."
                )

            except Exception as error:
                st.warning(
                    f"Performance comparison unavailable: {error}"
                )

        else:
            st.info(
                "Performance comparison skipped because generalized "
                "address optimization was unavailable."
            )

        st.success("Compiler demonstration completed!")

    except Exception as error:
        st.error(f"Compilation error: {error}")
        st.exception(error)
