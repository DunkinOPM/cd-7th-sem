
import ply.yacc as yacc

from compiler.lexer import tokens, lexer

precedence = (
    ("left", "LT", "GT", "LE", "GE", "EQ", "NE"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
    ("right", "UMINUS"),
)

def p_program(p):
    "program : statement_list"
    p[0] = {
        "type": "program",
        "body": p[1]
    }

def p_statement_list_multiple(p):
    "statement_list : statement_list statement"
    p[0] = p[1] + [p[2]]

def p_statement_list_empty(p):
    "statement_list : empty"
    p[0] = []

def p_empty(p):
    "empty :"
    p[0] = None

def p_statement(p):
    """statement : declaration
                 | assignment SEMICOLON
                 | for_statement
                 | block"""
    p[0] = p[1]

def p_type_spec(p):
    """type_spec : INT
                 | FLOAT"""
    p[0] = p[1]

def p_declaration(p):
    "declaration : type_spec IDENTIFIER dimensions SEMICOLON"
    p[0] = {
        "type": "declaration",
        "data_type": p[1],
        "name": p[2],
        "dimensions": p[3]
    }

def p_dimensions_multiple(p):
    "dimensions : dimensions LBRACKET NUMBER RBRACKET"
    p[0] = p[1] + [p[3]]

def p_dimensions_empty(p):
    "dimensions : empty"
    p[0] = []

def p_block(p):
    "block : LBRACE statement_list RBRACE"
    p[0] = {
        "type": "block",
        "body": p[2]
    }

def p_for_statement(p):
    """for_statement : FOR LPAREN for_init SEMICOLON expression SEMICOLON for_update RPAREN statement"""
    p[0] = {
        "type": "for_loop",
        "init": p[3],
        "condition": p[5],
        "update": p[7],
        "body": p[9]
    }

def p_for_init_declaration(p):
    "for_init : type_spec IDENTIFIER ASSIGN expression"
    p[0] = {
        "type": "variable_declaration",
        "data_type": p[1],
        "name": p[2],
        "value": p[4]
    }

def p_for_init_assignment(p):
    "for_init : assignment"
    p[0] = p[1]

def p_for_init_empty(p):
    "for_init : empty"
    p[0] = None

def p_for_update_increment(p):
    "for_update : IDENTIFIER INCREMENT"
    p[0] = {
        "type": "increment",
        "name": p[1]
    }

def p_for_update_assignment(p):
    "for_update : assignment"
    p[0] = p[1]

def p_assignment(p):
    "assignment : lvalue ASSIGN expression"
    p[0] = {
        "type": "assignment",
        "target": p[1],
        "value": p[3]
    }

def p_lvalue(p):
    "lvalue : IDENTIFIER indices"

    if p[2]:
        p[0] = {
            "type": "array_access",
            "name": p[1],
            "indices": p[2]
        }
    else:
        p[0] = {
            "type": "identifier",
            "name": p[1]
        }

def p_indices_multiple(p):
    "indices : indices LBRACKET expression RBRACKET"
    p[0] = p[1] + [p[3]]

def p_indices_empty(p):
    "indices : empty"
    p[0] = []

def p_expression_binary(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression LT expression
                  | expression GT expression
                  | expression LE expression
                  | expression GE expression
                  | expression EQ expression
                  | expression NE expression"""
    p[0] = {
        "type": "binary",
        "operator": p[2],
        "left": p[1],
        "right": p[3]
    }

def p_expression_number(p):
    "expression : NUMBER"
    p[0] = {
        "type": "number",
        "value": p[1]
    }

def p_expression_identifier(p):
    "expression : IDENTIFIER indices"

    if p[2]:
        p[0] = {
            "type": "array_access",
            "name": p[1],
            "indices": p[2]
        }
    else:
        p[0] = {
            "type": "identifier",
            "name": p[1]
        }

def p_expression_group(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]

def p_expression_unary(p):
    "expression : MINUS expression %prec UMINUS"
    p[0] = {
        "type": "unary",
        "operator": "-",
        "operand": p[2]
    }

def p_error(p):
    if p:
        raise SyntaxError(
            f"Syntax error near '{p.value}' at line {p.lineno}"
        )
    raise SyntaxError("Unexpected end of input")

parser = yacc.yacc()

def parse_source(source_code):
    return parser.parse(source_code, lexer=lexer)
