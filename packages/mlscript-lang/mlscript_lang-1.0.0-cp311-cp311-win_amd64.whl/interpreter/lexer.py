import re
from enum import Enum, auto

class TokenType(Enum):
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    IDENT = auto()
    ASSIGN = auto()
    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    COLON = auto()
    DOT = auto()
    PRINT = auto()
    FUN = auto()
    RETURN = auto()
    IF = auto()
    ELIF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    NOT = auto()
    IN = auto()
    WITH = auto()
    TRY = auto()
    CATCH = auto()
    FINALLY = auto()
    THROW = auto()
    BREAK = auto()
    CONTINUE = auto()
    EQ = auto()
    NE = auto()
    GT = auto()
    GTE = auto()
    LT = auto()
    LTE = auto()
    TRUE = auto()
    FALSE = auto()
    IMPORT = auto()
    CLASS = auto()
    SUPER = auto()
    INHERITS = auto()
    AS = auto()
    EOF = auto()

token_spec = [
    ("COMMENT",       r'//.*'),
    ("NEWLINE",        r'\n'),
    ("SKIP",            r'[ \t]+'),
    (TokenType.IF,      r'if\b'),
    (TokenType.ELIF,    r'elif\b'),
    (TokenType.ELSE,    r'else\b'),
    (TokenType.WHILE,   r'while\b'),
    (TokenType.FOR,     r'for\b'),
    (TokenType.NOT,     r'not\b'),
    (TokenType.IN,      r'in\b'),
    (TokenType.WITH,    r'with\b'),
    (TokenType.TRY,     r'try\b'),
    (TokenType.CATCH,   r'catch\b'),
    (TokenType.FINALLY, r'finally\b'),
    (TokenType.THROW,   r'throw\b'),
    (TokenType.BREAK,   r'break\b'),
    (TokenType.CONTINUE, r'continue\b'),
    (TokenType.FUN,     r'fun\b'),
    (TokenType.CLASS,   r'class\b'),
    (TokenType.SUPER,   r'super\b'),
    (TokenType.INHERITS, r'inherits\b'),
    (TokenType.RETURN,  r'return\b'),
    (TokenType.PRINT,   r'print\b'),
    (TokenType.TRUE,    r'true\b'),
    (TokenType.FALSE,   r'false\b'),
    (TokenType.IMPORT,  r'import\b'),
    (TokenType.AS,      r'as\b'),
    (TokenType.FLOAT,   r'\d+\.\d+'),
    (TokenType.INTEGER, r'\d+'),
    (TokenType.STRING,  r'"(?:\\.|[^"\\])*"'),
    (TokenType.IDENT,   r'[a-zA-Z_]\w*'),
    (TokenType.EQ,      r'=='),
    (TokenType.NE,      r'!='),
    (TokenType.GTE,     r'>='),
    (TokenType.LTE,     r'<='),
    (TokenType.GT,      r'>'),
    (TokenType.LT,      r'<'),
    (TokenType.ASSIGN,  r'='),
    (TokenType.PLUS,    r'\+'),
    (TokenType.MINUS,   r'-'),
    (TokenType.MUL,     r'\*'),
    (TokenType.DIV,     r'/'),
    (TokenType.LPAREN,  r'\('),
    (TokenType.RPAREN,  r'\)'),
    (TokenType.LBRACE,  r'\{'),
    (TokenType.RBRACE,  r'\}'),
    (TokenType.LBRACKET, r'\['),
    (TokenType.RBRACKET, r'\]'),
    (TokenType.COMMA,   r','),
    (TokenType.COLON,   r':'),
    (TokenType.DOT,     r'\.'),
    
    ("MISMATCH",        r'.'),
]

token_regex = '|'.join(f'(?P<{spec[0].name if isinstance(spec[0], Enum) else spec[0]}>{spec[1]})' for spec in token_spec)
 
def tokenize(code):
    tokens = []
    line_num = 1

    for mo in re.finditer(token_regex, code):
        kind_str = mo.lastgroup
        value = mo.group()

        if kind_str == "COMMENT":
            continue
        if kind_str == "NEWLINE":
            line_num += 1
            continue
        if kind_str == "SKIP" or kind_str == "MISMATCH":
            continue

        kind = TokenType[kind_str]

        if kind == TokenType.FLOAT:
            value = float(value)
        elif kind == TokenType.INTEGER:
            value = int(value)
        elif kind == TokenType.STRING:
            value = bytes(value[1:-1], "utf-8").decode("unicode_escape")
        elif kind == TokenType.TRUE:
            value = True
        elif kind == TokenType.FALSE:
            value = False

        tokens.append((kind, value, line_num))

    tokens.append((TokenType.EOF, None,line_num))
    return tokens