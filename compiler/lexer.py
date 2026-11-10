
import ply.lex as lex

reserved = {
    "int": "INT",
    "float": "FLOAT",
    "for": "FOR",
    "if": "IF",
    "else": "ELSE",
    "return": "RETURN",
}

tokens = [
    "IDENTIFIER",
    "NUMBER",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "ASSIGN",
    "LT",
    "GT",
    "LE",
    "GE",
    "EQ",
    "NE",
    "INCREMENT",
    "LBRACKET",
    "RBRACKET",
    "LPAREN",
    "RPAREN",
    "LBRACE",
    "RBRACE",
    "SEMICOLON",
    "COMMA",
] + list(reserved.values())

t_INCREMENT = r"\+\+"
t_LE = r"<="
t_GE = r">="
t_EQ = r"=="
t_NE = r"!="

t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_ASSIGN = r"="
t_LT = r"<"
t_GT = r">"

t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_SEMICOLON = r";"
t_COMMA = r","

t_ignore = " \t\r"

def t_IDENTIFIER(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    t.type = reserved.get(t.value, "IDENTIFIER")
    return t

def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t

def t_COMMENT(t):
    r"//.*"
    pass

def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

def t_error(t):
    raise SyntaxError(
        f"Illegal character '{t.value[0]}' at line {t.lineno}"
    )

lexer = lex.lex()

def tokenize(source_code):
    lexer.input(source_code)
    result = []

    while True:
        token = lexer.token()

        if token is None:
            break

        result.append({
            "type": token.type,
            "value": token.value,
            "line": token.lineno
        })

    return result
