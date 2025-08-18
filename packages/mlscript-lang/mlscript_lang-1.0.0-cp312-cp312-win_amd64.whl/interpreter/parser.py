
from .lexer import TokenType
from .ast_nodes import *

class Parser:
    def __init__(self, tokens,code):
        self.tokens = tokens
        self.code_lines = code.split('\n')
        self.pos = 0
        self.current_token = self.tokens[self.pos]
        self.in_loop = False
        self.in_class = False 

    def advance(self):
        """Advance the token pointer and update the current token."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]

    def error(self, expected_type):
        token_type, token_value, line_num = self.current_token
        line = self.code_lines[line_num - 1]

        error_message = f"""SyntaxError: Expected {expected_type}, but got {token_type} at line {line_num}: {line.strip()}"""
        raise Exception(error_message)


    def eat(self, token_type):
        """Consume the current token if it matches the expected type."""
        if self.current_token[0] == token_type:
            self.advance()
        else:
            self.error(token_type)

    def parse(self):
        """Parse a list of statements."""
        statements = []
        while self.current_token[0] != TokenType.EOF:
            statements.append(self.statement())
        return statements

    def statement(self):
        token_type = self.current_token[0]

        if token_type == TokenType.PRINT:
            return self.print_statement()
        elif token_type == TokenType.FUN:
            return self.function_definition()
        elif token_type == TokenType.CLASS:
            return self.class_definition()
        elif token_type == TokenType.IF:
            return self.if_statement()
        elif token_type == TokenType.WHILE:
            return self.while_statement()
        elif token_type == TokenType.FOR:
            return self.for_statement()
        elif token_type == TokenType.WITH:
            return self.with_statement()
        elif token_type == TokenType.IMPORT:
            return self.import_statement()
        elif token_type == TokenType.THROW:
            return self.throw_statement()
        elif token_type == TokenType.TRY:
            return self.try_catch_statement()
        elif token_type == TokenType.BREAK:
            return self.break_statement()
        elif token_type == TokenType.CONTINUE:
            return self.continue_statement()
        elif token_type == TokenType.RETURN:
            self.advance()
            expr = self.comparison_expression()
            return ReturnStatement(expr)
        else:
            return self.assignment_or_expression_statement()

    def throw_statement(self):
        token = self.current_token
        self.eat(TokenType.THROW)
        expr = self.comparison_expression()
        return ThrowStatement(token, expr)

    def try_catch_statement(self):
        self.eat(TokenType.TRY)
        try_block = self.block()

        catch_variable = None
        catch_block = None
        if self.current_token[0] == TokenType.CATCH:
            self.eat(TokenType.CATCH)
            self.eat(TokenType.LPAREN)
            catch_variable = Variable(self.current_token)
            self.eat(TokenType.IDENT)
            self.eat(TokenType.RPAREN)
            catch_block = self.block()

        finally_block = None
        if self.current_token[0] == TokenType.FINALLY:
            self.eat(TokenType.FINALLY)
            finally_block = self.block()
        
        if not catch_block and not finally_block:
            self.error("A 'try' statement must have at least one 'catch' or 'finally' block.")

        return TryCatch(try_block, catch_variable, catch_block, finally_block)
        
    def assignment_or_expression_statement(self):
        expr = self.comparison_expression()

        if self.current_token[0] == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            right_expr = self.comparison_expression()

            if isinstance(expr, Variable):
                return Assign(expr, right_expr)
            elif isinstance(expr, IndexAccess):
                return IndexAssign(expr.collection, expr.index_expr, right_expr)
            elif isinstance(expr, AttributeAccess):
                return AttributeAssign(expr.obj,expr.token,right_expr)
            else:
                raise SyntaxError("The left-hand side of an assignment must be a variable or an index.")
        return expr

    def print_statement(self):
        self.eat(TokenType.PRINT)
        self.eat(TokenType.LPAREN)
        expr = self.comparison_expression()
        self.eat(TokenType.RPAREN)
        return PrintStatement(expr)

    def assignment_statement(self):
        ident_token = self.current_token
        self.eat(TokenType.IDENT)
        self.eat(TokenType.ASSIGN)
        expr = self.comparison_expression()
        return Assign(Variable(ident_token), expr)

    def if_statement(self):
        cases = []
        # Parse the initial 'if'
        self.eat(TokenType.IF)
        self.eat(TokenType.LPAREN)
        condition = self.comparison_expression()
        self.eat(TokenType.RPAREN)
        body = self.block()
        cases.append((condition, body))

        # Parse all 'elif' blocks
        while self.current_token[0] == TokenType.ELIF:
            self.eat(TokenType.ELIF)
            self.eat(TokenType.LPAREN)
            condition = self.comparison_expression()
            self.eat(TokenType.RPAREN)
            body = self.block()
            cases.append((condition, body))

        # Parse the final 'else' block, if it exists
        else_body = None
        if self.current_token[0] == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            else_body = self.block()

        # Build the nested IfStatement node from the cases
        # Start from the last case and work backwards
        if else_body:
            node = else_body
        else:
            node = None
            
        for condition, body in reversed(cases):
            node = IfStatement(condition, body, node)
        
        return node
    
    def while_statement(self):
        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)
        condition = self.comparison_expression()
        self.eat(TokenType.RPAREN)

        original_in_loop = self.in_loop
        self.in_loop = True
        try:
            body = self.block()
        finally:
            self.in_loop = original_in_loop
        
        return WhileStatement(condition, body)
    
    def for_statement(self):
        self.eat(TokenType.FOR)
        variable_node = Variable(self.current_token)
        self.eat(TokenType.IDENT)
        self.eat(TokenType.IN)

        iterable_node = self.comparison_expression()

        original_in_loop = self.in_loop
        self.in_loop = True
        try:
            body = self.block()
        finally:
            self.in_loop = original_in_loop
        
        return ForStatement(variable_node, iterable_node, body)
    
    def with_statement(self):
        self.eat(TokenType.WITH)
        context_expr = self.comparison_expression()
        body = self.block()
        return WithStatement(context_expr, body)
    
    def import_statement(self):
        self.eat(TokenType.IMPORT)
        module_name_token = self.current_token
        self.eat(TokenType.STRING)
        self.eat(TokenType.AS)
        alias_token = self.current_token
        self.eat(TokenType.IDENT)
        return ImportStatement(module_name_token, alias_token)

    def function_definition(self):
        self.eat(TokenType.FUN)
        name_token = self.current_token
        self.eat(TokenType.IDENT)
        self.eat(TokenType.LPAREN)
        
        params = []
        has_seen_default = False

        if self.current_token[0] != TokenType.RPAREN:
            while True:
                param_name = Variable(self.current_token)
                self.eat(TokenType.IDENT)
                
                if self.current_token[0] == TokenType.ASSIGN:
                    self.eat(TokenType.ASSIGN)
                    default_value = self.comparison_expression()
                    params.append((param_name, default_value))
                    has_seen_default = True
                else:
                    if has_seen_default:
                        self.error("non-default argument follows default argument")
                    params.append((param_name, None))

                if self.current_token[0] == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                else:
                    break

        self.eat(TokenType.RPAREN)
        body = self.block()
        return FunctionDef(name_token, params, body)

    def block(self):
        """Parses a block of statements enclosed in curly braces."""
        self.eat(TokenType.LBRACE)
        statements = []
        while self.current_token[0] not in (TokenType.RBRACE, TokenType.EOF):
            statements.append(self.statement())
        self.eat(TokenType.RBRACE)
        return Block(statements)

    def comparison_expression(self):
        """Parses comparison operators (==, !=, <, >, etc.)."""
        node = self.expr()

        # Handle 'not in' operator as a special case
        if self.current_token[0] == TokenType.NOT:
            self.eat(TokenType.NOT)
            if self.current_token[0] != TokenType.IN:
                self.error("Expected 'in' after 'not'")

            in_token = self.current_token
            self.eat(TokenType.IN)
            op_token = (in_token[0], 'not in', in_token[2])
            node = BinOp(node, op_token, self.expr())
            return node

        # Handle other comparison operators
        op_types = [
            TokenType.EQ, TokenType.NE, TokenType.LT,
            TokenType.LTE, TokenType.GT, TokenType.GTE, TokenType.IN
        ]
        while self.current_token[0] in op_types:
            op_token = self.current_token
            self.eat(op_token[0])
            node = BinOp(node, op_token, self.expr())
        return node

    def expr(self):
        """Parses addition and subtraction."""
        node = self.term()
        while self.current_token[0] in (TokenType.PLUS, TokenType.MINUS):
            op_token = self.current_token
            self.eat(op_token[0])
            node = BinOp(node, op_token, self.term())
        return node

    def term(self):
        """Parses multiplication and division."""
        node = self.factor()
        while self.current_token[0] in (TokenType.MUL, TokenType.DIV):
            op_token = self.current_token
            self.eat(op_token[0])
            node = BinOp(node, op_token, self.factor()) 
        return node

    def factor(self):
        token = self.current_token
        if token[0] in (TokenType.PLUS, TokenType.MINUS):
            self.advance()
            return UnaryOp(token, self.factor())
        return self.call_and_index()

    def call_and_index(self):
        node = self.primary()

        while True:
            if self.current_token[0] == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                args = []
                if self.current_token[0] != TokenType.RPAREN:
                    args.append(self.comparison_expression())
                    while self.current_token[0] == TokenType.COMMA:
                        self.eat(TokenType.COMMA)
                        args.append(self.comparison_expression())
                self.eat(TokenType.RPAREN)
                node = FunctionCall(node, args)
            elif self.current_token[0] == TokenType.LBRACKET:
                self.eat(TokenType.LBRACKET)
                index_expr = []
                if self.current_token[0] != TokenType.RBRACKET:
                    def parse_slice_or_expr():
                        start=None
                        if self.current_token[0] != TokenType.COLON:
                            start = self.comparison_expression()
                        if self.current_token[0] != TokenType.COLON:
                            return start
                        self.eat(TokenType.COLON)
                        stop = None
                        if self.current_token[0] not in (TokenType.COLON, TokenType.RBRACKET):
                            stop = self.comparison_expression()
                        step = None
                        if self.current_token[0] == TokenType.COLON:
                            self.eat(TokenType.COLON)
                            if self.current_token[0] not in (TokenType.RBRACKET, TokenType.COMMA):
                                step = self.comparison_expression()

                        return SliceNode(start, stop, step)
                        
                    index_expr.append(parse_slice_or_expr())
                    while self.current_token[0] == TokenType.COMMA:
                        self.eat(TokenType.COMMA)
                        index_expr.append(parse_slice_or_expr())
                
                self.eat(TokenType.RBRACKET)
                node = IndexAccess(node, index_expr)
            elif self.current_token[0] == TokenType.DOT:
                self.eat(TokenType.DOT)
                attr_token = self.current_token
                self.eat(TokenType.IDENT)
                node = AttributeAccess(node, attr_token)
            else:
                break
        return node
    
    def primary(self):
        token = self.current_token
        token_type = token[0]

        if token_type == TokenType.STRING:
            self.advance()
            return StringLiteral(token)
        elif token_type in (TokenType.INTEGER, TokenType.FLOAT):
            self.advance()
            return Number(token)
        elif token_type in (TokenType.TRUE, TokenType.FALSE):
            self.advance()
            return BooleanLiteral(token)
        elif token_type == TokenType.SUPER:
            if not self.in_class:
                self.error("The 'super' keyword can only be used inside a class method.")
            self.advance()
            return SuperNode(token)
        elif token_type == TokenType.LBRACKET:
            return self.list_expression()
        elif token_type == TokenType.LBRACE:
            return self.dict_expression()
        elif token_type == TokenType.IDENT:
            self.advance()
            return Variable(token)
        elif token_type == TokenType.LPAREN:
            start_token = self.current_token
            self.eat(TokenType.LPAREN)

            if self.current_token[0] == TokenType.RPAREN:
                self.eat(TokenType.RPAREN)
                return TupleLiteral(start_token, [])

            node = self.comparison_expression()

            if self.current_token[0] == TokenType.COMMA:
                elements = [node]
                while self.current_token[0] == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    if self.current_token[0] == TokenType.RPAREN:
                        break
                    elements.append(self.comparison_expression())
                self.eat(TokenType.RPAREN)
                return TupleLiteral(start_token, elements)
            
            self.eat(TokenType.RPAREN)
            return node
        else:
            raise SyntaxError(f"Unexpected token {self.current_token} in expression")
        
    def list_expression(self):
        """Parses a list literal."""
        start_token = self.current_token
        self.eat(TokenType.LBRACKET)
        elements = []
        if self.current_token[0] != TokenType.RBRACKET:
            elements.append(self.comparison_expression())
            while self.current_token[0] == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                elements.append(self.comparison_expression())
        self.eat(TokenType.RBRACKET)
        return ListLiteral(start_token,elements)

    def dict_expression(self):
        """Parses a dictionary literal."""
        start_token = self.current_token
        self.eat(TokenType.LBRACE)
        pairs = []
        if self.current_token[0] != TokenType.RBRACE:
            key = self.comparison_expression()
            self.eat(TokenType.COLON)
            value_node = self.comparison_expression()
            pairs.append((key, value_node))

            while self.current_token[0] == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                key_node = self.comparison_expression()
                self.eat(TokenType.COLON)
                value_node = self.comparison_expression()
                pairs.append((key_node, value_node))
        self.eat(TokenType.RBRACE)
        return DictLiteral(start_token, pairs)
    
    def break_statement(self):
        if not self.in_loop:
            self.error("Break statement can only be used inside a loop.")
        token = self.current_token
        self.eat(TokenType.BREAK)
        return BreakStatement(token)
    
    def continue_statement(self):
        if not self.in_loop:
            self.error("Continue statement can only be used inside a loop.")
        token = self.current_token
        self.eat(TokenType.CONTINUE)
        return ContinueStatement(token)
    
    def class_definition(self):
        self.eat(TokenType.CLASS)
        name_token = self.current_token
        self.eat(TokenType.IDENT)

        parents = []
        if self.current_token[0] == TokenType.INHERITS:
            self.eat(TokenType.INHERITS)
            parents.append(Variable(self.current_token))
            self.eat(TokenType.IDENT)
            while self.current_token[0] == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                parents.append(Variable(self.current_token))
                self.eat(TokenType.IDENT)

        self.eat(TokenType.LBRACE)

        original_in_class = self.in_class
        self.in_class = True
        try:

            methods=[]
            while self.current_token[0] != TokenType.RBRACE:
                if self.current_token[0] == TokenType.FUN:
                    methods.append(self.function_definition())
                else:
                    self.error("Only method definitions ('fun') are allowed inside a class body.")
        finally:
            self.in_class = original_in_class
        
        self.eat(TokenType.RBRACE)
        return ClassDef(name_token,parents,methods)