
from compiler.parser import parse_source
from compiler.array_analyzer import ArrayAnalyzer
from compiler.address_coefficient_calculator import AddressCoefficientCalculator
from compiler.generalized_incremental_generator import GeneralizedIncrementalGenerator

source = """
int A[298][303];

for (int i = 0; i < 100; i++) {
    for (int j = 0; j < 100; j++) {
        A[2*i + j][3*j + 5] = i + j;
    }
}
"""

ast = parse_source(source)
array_info = ArrayAnalyzer().analyze(ast)

outer_loop = ast["body"][1]
inner_loop = outer_loop["body"]["body"][0]
assignment = inner_loop["body"]["body"][0]

result = AddressCoefficientCalculator(array_info).calculate(
    "A",
    assignment["target"]["indices"]
)

generator = GeneralizedIncrementalGenerator()

instructions = generator.generate(
    result,
    loop_variables=["i", "j"],
    loop_limits=[100, 100],
    value_expression="i + j"
)

print("\n".join(instructions))
