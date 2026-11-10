
from compiler.parser import parse_source
from compiler.array_analyzer import ArrayAnalyzer
from compiler.address_coefficient_calculator import AddressCoefficientCalculator

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

outer = ast["body"][1]
inner = outer["body"]["body"][0]
assignment = inner["body"]["body"][0]

index_expressions = assignment["target"]["indices"]

calculator = AddressCoefficientCalculator(array_info)

result = calculator.calculate("A", index_expressions)

print(result)
