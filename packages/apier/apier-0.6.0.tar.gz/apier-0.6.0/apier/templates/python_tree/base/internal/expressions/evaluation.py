import ast
import operator

# Supported binary operators
allowed_operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,  # Unary minus
}

# Supported comparison operators
allowed_comparators = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}

# Whitelisted functions
allowed_functions = {
    "int": int,
    "len": len,
    "round": lambda x: int(round(x)),
    "floor": lambda x: int(x // 1),
    "ceil": lambda x: int(-(-x // 1)),
}

# Constants
allowed_constants = {
    "true": True,
    "false": False,
    "null": None,
}


def eval_expr(expr, vars=None):
    """
    Evaluates a compound expression using AST with a restricted subset of
    Python syntax:
     - Arithmetic (+, -, *, /, unary -)
     - Function calls (`int`, `len`, `round`, `floor`, `ceil`)
     - Comparisons (==, !=, <, <=, >, >=)

    Note: This implementation is a basic and temporary solution based on Python syntax.
    It has limited extensibility and is not designed to be portable across other languages.
    For more complex use cases, a dedicated expression language or library would be required.

    Parameters:
        expr (str): The expression string to evaluate.
        vars (dict, optional): A dictionary of variables to use in the expression.

    Returns:
        The result of evaluating the expression.
    """
    # Parse the expression into an AST
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise SyntaxError(f"Invalid expression syntax: {e.msg}") from e

    vars = vars.copy() if vars is not None else {}
    vars.update(allowed_constants)

    def _eval(node: ast.AST):
        """Recursively evaluate supported AST nodes."""

        if isinstance(node, ast.Constant):
            if isinstance(node.value, complex):
                raise ValueError("Complex numbers are not supported.")
            if node.value is True or node.value is False or node.value is None:
                raise ValueError(f"Unsupported constant: {node.value}")
            return node.value

        elif isinstance(node, ast.Name):
            # Variable reference
            if vars is not None and node.id in vars:
                return vars[node.id]
            else:
                raise ValueError(f"Variable not defined: {node.id}")

        elif isinstance(node, ast.BinOp) and type(node.op) in allowed_operators:
            left = _eval(node.left)
            right = _eval(node.right)
            return allowed_operators[type(node.op)](left, right)

        elif isinstance(node, ast.UnaryOp) and type(node.op) in allowed_operators:
            operand = _eval(node.operand)
            return allowed_operators[type(node.op)](operand)

        elif isinstance(node, ast.Call):
            # Only allow calls to whitelisted functions
            if isinstance(node.func, ast.Name) and node.func.id in allowed_functions:
                func = allowed_functions[node.func.id]
                args = [_eval(arg) for arg in node.args]
                return func(*args)
            else:
                raise ValueError(f"Function not allowed: '{node.func.id}'")

        elif isinstance(node, ast.List):
            return [_eval(elt) for elt in node.elts]

        elif isinstance(node, ast.Tuple):
            return tuple(_eval(elt) for elt in node.elts)

        elif isinstance(node, ast.Compare):
            # Only support simple comparisons (not chained comparisons)
            if len(node.ops) != 1 or len(node.comparators) != 1:
                raise ValueError("Only simple comparisons are supported.")
            op = node.ops[0]
            if type(op) not in allowed_comparators:
                raise ValueError(
                    f"Comparison operator not allowed: {type(op).__name__}"
                )
            left = _eval(node.left)
            right = _eval(node.comparators[0])
            return allowed_comparators[type(op)](left, right)

        else:
            raise SyntaxError(f"Unsupported syntax: {type(node).__name__}")

    return _eval(tree.body)
