# ast_nodes.py

class Node:
    """Base class for all Abstract Syntax Tree nodes."""
    pass

class Number(Node):
    """Represents a literal integer or float value."""
    def __init__(self, token):
        self.token = token
        self.value = token[1]

class StringLiteral(Node):
    """Represents a string literal."""
    def __init__(self, token):
        self.token = token
        self.value = token[1] 

class BooleanLiteral(Node):
    """Represents a boolean literal."""
    def __init__(self, token):
        self.token = token
        self.value = token[1] 

class ListLiteral(Node):
    """Represents a list literal."""
    def __init__(self, start_token,elements):
        self.token = start_token
        self.elements = elements

class DictLiteral(Node):
    """Represents a dictionary literal."""
    def __init__(self, start_token, pairs):
        self.token = start_token
        self.pairs = pairs

class TupleLiteral(Node):
    """Represents a tuple literal."""
    def __init__(self, start_token, elements):
        self.token = start_token
        self.elements = elements                                                

class Variable(Node):
    """Represents a variable identifier."""
    def __init__(self, token):
        self.token = token
        self.name = token[1]

class AttributeAccess(Node):
    """Represents an attribute access (e.g., object.attribute)."""
    def __init__(self,obj,attribute_name_token):
        self.obj = obj
        self.attribute= attribute_name_token[1]  
        self.token = attribute_name_token

class IndexAccess(Node):
    """Represents an index access operation (e.g., list[index])."""
    def __init__(self, collection, index_expr):
        self.collection = collection  # This is a Variable or ListLiteral node
        self.index_expr = index_expr
        self.token = collection.token

class IndexAssign(Node):
    """Represents an index assignment operation (e.g., list[index] = value)."""
    def __init__(self, collection, index_expr, value_expr):
        self.collection = collection  # This is a Variable or ListLiteral node
        self.index_expr = index_expr
        self.value_expr = value_expr
        self.token = collection.token
        

class UnaryOp(Node):
    """Represents a unary operation (e.g., -x, !x)."""
    def __init__(self, op_token,expr):
        self.token = op_token
        self.op = op_token[1]  # The operator (e.g., '-', '!')
        self.expr = expr

class BinOp(Node):
    """Represents a binary operation (e.g., +, -, *, /, ==)."""
    def __init__(self, left, op_token, right):
        self.left = left
        self.op_token = op_token
        self.right = right

class Assign(Node):
    """Represents a variable assignment (e.g., x = 5)."""
    def __init__(self, left, expr):
        self.left = left  # This is a Variable node
        self.expr = expr

class PrintStatement(Node):
    """Represents a print statement."""
    def __init__(self, expr):
        self.expr = expr

class Block(Node):
    """Represents a block of statements { ... }."""
    def __init__(self, statements):
        self.statements = statements

class IfStatement(Node):
    """Represents an if-else statement."""
    def __init__(self, condition, if_block, else_block=None):
        self.condition = condition
        self.if_block = if_block
        self.else_block = else_block

class WhileStatement(Node):
    """Represents a while loop."""
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ForStatement(Node):
    """Represents a for loop."""
    def __init__(self, variable, iterable, body):
        self.variable = variable
        self.iterable = iterable 
        self.body = body

class FunctionDef(Node):
    """Represents a function definition."""
    def __init__(self, name_token, params, body):
        self.name = name_token[1]
        self.params = params  # List of Variable nodes
        self.body = body      # Block node

class FunctionCall(Node):
    """Represents a function call."""
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args
        self.token = callee.token  

class ReturnStatement(Node):
    """Represents a return statement."""
    def __init__(self, expr):
        self.expr = expr

class SliceNode(Node):
    """Represents a slice operation (e.g., list[start:end:step])."""
    def __init__(self, start=None, stop=None, step=None):
        self.start = start
        self.stop = stop
        self.step = step

class ImportStatement(Node):
    """Represents an import statement."""
    def __init__(self,module_name_token, alias_token):
        self.module_name = module_name_token[1]  
        self.alias = alias_token[1] 
        self.token = module_name_token  

class WithStatement(Node):
    """Represents a with statement."""
    def __init__(self, context_expr, body):
        self.context_expr = context_expr
        self.body = body

class ThrowStatement(Node):
    """Represents a throw statement."""
    def __init__(self, token, expr):
        self.token = token
        self.expr = expr

class TryCatch(Node):
    """Represents a try-catch block."""
    def __init__(self, try_block, catch_variable, catch_block, finally_block=None):
        self.try_block = try_block
        self.catch_variable = catch_variable
        self.catch_block = catch_block
        self.finally_block = finally_block

class BreakStatement(Node):
    """Represents a break statement."""
    def __init__(self, token):
        self.token = token

class ContinueStatement(Node):
    """Represents a continue statement."""
    def __init__(self, token):
        self.token = token

class ClassDef(Node):
    """Represents a class definition"""
    def __init__(self,name_token,parents,methods):
        self.name = name_token[1]
        self.token = name_token
        self.parents = parents  
        self.methods = methods

class AttributeAssign(Node):
    """Represents assigning a value to an object's attribute."""
    def __init__(self,obj,attribute_token,value_expr):
        self.obj=obj
        self.attribute = attribute_token[1]
        self.token = attribute_token
        self.value_expr = value_expr

class SuperNode(Node):
    """Represents the 'super' keyword"""
    def __init__(self, token):
        self.token = token
