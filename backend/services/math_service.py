
"""
MathForStudent Mathematics Engine

Supports algebra, equations, simplification,
expansion, factorization and differentiation.
"""

import ast
import sympy as sp

x, y, z = sp.symbols("x y z")

SYMBOLS = {
    "x": x,
    "y": y,
    "z": z,
    "pi": sp.pi,
    "E": sp.E,
}

FUNCTIONS = {
    "sqrt": sp.sqrt,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "log": sp.log,
    "exp": sp.exp,
    "abs": sp.Abs,
}


def parse_expression(text):
    """Parse mathematical input using an approved syntax only."""

    if not isinstance(text, str):
        raise ValueError("Input must be text.")

    text = text.strip()

    if not text or len(text) > 500:
        raise ValueError("Invalid expression length.")

    try:
        tree = ast.parse(text, mode="eval")
        return _convert(tree.body)
    except (SyntaxError, TypeError, ValueError) as error:
        raise ValueError(
            "Invalid or unsupported mathematical expression."
        ) from error


def _convert(node):
    """Convert approved Python AST nodes into SymPy expressions."""

    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            raise ValueError("Boolean values are not allowed.")
        if isinstance(node.value, (int, float)):
            return sp.sympify(node.value)
        raise ValueError("Only numeric constants are allowed.")

    if isinstance(node, ast.Name):
        if node.id in SYMBOLS:
            return SYMBOLS[node.id]
        raise ValueError(f"Unknown symbol: {node.id}")

    if isinstance(node, ast.BinOp):
        left = _convert(node.left)
        right = _convert(node.right)

        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            if right.is_number and abs(float(right)) > 100:
                raise ValueError("Exponent is too large.")
            return left ** right

        raise ValueError("Unsupported mathematical operator.")

    if isinstance(node, ast.UnaryOp):
        value = _convert(node.operand)

        if isinstance(node.op, ast.USub):
            return -value
        if isinstance(node.op, ast.UAdd):
            return value

        raise ValueError("Unsupported unary operator.")

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Unsupported function.")

        function = FUNCTIONS.get(node.func.id)

        if function is None or node.keywords:
            raise ValueError("Function is not supported.")

        arguments = [_convert(arg) for arg in node.args]

        if len(arguments) != 1:
            raise ValueError("This function requires one argument.")

        return function(*arguments)

    raise ValueError("Unsupported expression syntax.")


def solve_math_problem(problem, operation="auto"):
    """
    Solve supported algebraic and symbolic problems.

    Examples:
        2*x + 4 = 10
        x**2 - 9
        x**2 - 5*x + 6
    """

    if not isinstance(problem, str):
        raise ValueError("Problem must be text.")

    problem = problem.strip()

    if not problem or len(problem) > 1000:
        raise ValueError("Invalid problem length.")

    if operation == "differentiate":
        expression = parse_expression(problem)
        result = sp.diff(expression, x)

        return {
            "topic": "Differentiation",
            "original": str(expression),
            "answer": str(result),
            "steps": [
                "Identify the expression.",
                "Differentiate with respect to x.",
                f"Result: {result}"
            ]
        }

    if operation == "integrate":
        expression = parse_expression(problem)
        result = sp.integrate(expression, x)

        return {
            "topic": "Integration",
            "original": str(expression),
            "answer": str(result),
            "steps": [
                "Identify the expression.",
                "Integrate with respect to x.",
                f"Result: {result} + C"
            ]
        }

    if "=" in problem:
        if problem.count("=") != 1:
            raise ValueError("Please provide one equation at a time.")

        left, right = problem.split("=", 1)

        equation = sp.Eq(
            parse_expression(left),
            parse_expression(right)
        )

        solutions = sp.solve(equation, x)

        return {
            "topic": "Algebra and Equations",
            "equation": str(equation),
            "answer": [str(item) for item in solutions],
            "steps": [
                "Identify the equation.",
                "Rearrange the equation to find x.",
                f"Solution: {solutions}"
            ]
        }

    expression = parse_expression(problem)

    if operation == "expand":
        result = sp.expand(expression)
    elif operation == "factor":
        result = sp.factor(expression)
    elif operation == "simplify" or operation == "auto":
        result = sp.simplify(expression)
    else:
        raise ValueError("Unsupported mathematics operation.")

    return {
        "topic": "Algebra",
        "original": str(expression),
        "answer": str(result),
        "expanded": str(sp.expand(expression)),
        "factorized": str(sp.factor(expression)),
        "steps": [
            "Read and identify the expression.",
            "Apply the requested algebraic operation.",
            f"Result: {result}"
        ]
  }
      
