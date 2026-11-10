
from compiler.parser import parse_source
from compiler.coefficient_analyzer import CoefficientAnalyzer

source = """
int A[100][100];

for (int i = 0; i < 100; i++) {
    for (int j = 0; j < 100; j++) {
        A[2*i + j][3*j + 5] = i + j;
    }
}
"""

ast = parse_source(source)

# Get the array assignment
outer = ast["body"][1]
inner = outer["body"]["body"][0]
assignment = inner["body"]["body"][0]

analyzer = CoefficientAnalyzer()

for index in assignment["target"]["indices"]:
    result = analyzer.analyze_expression(index)
    print(result)
