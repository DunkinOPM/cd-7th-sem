
from compiler.parser import parse_source
from compiler.array_analyzer import ArrayAnalyzer
from compiler.address_coefficient_calculator import AddressCoefficientCalculator
from compiler.generalized_address_generator import GeneralizedAddressGenerator

source = """
int A[100][100];

for (int i = 0; i < 100; i++) {
    for (int j = 0; j < 100; j++) {
        A[2*i + j][3*j + 5] = i + j;
    }
}
"""

ast = parse_source(source)

array_info = ArrayAnalyzer().analyze(ast)

assignment = ast["body"][1]["body"]["body"][0]["body"]["body"][0]

calculator = AddressCoefficientCalculator(array_info)

result = calculator.calculate(
    "A",
    assignment["target"]["indices"]
)

generator = GeneralizedAddressGenerator()

instructions = generator.generate(result)

print("\n".join(instructions))
