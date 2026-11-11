
"""
MathForStudent Calculation Service

Provides safe basic arithmetic calculations.
"""

import ast
import operator


OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculate(expression: str):
    """
    Safely evaluate a basic arithmetic expression.

    Supported:
    Addition, subtraction, multiplication,
    division, powers and modulo.
    """

    if not isinstance(expression, str):
        raise ValueError("Expression must be text.")

    expression = expression.strip()

    if not expression or len(expression) > 200:
        raise ValueError("Invalid expression length.")

    try:
        tree = ast.parse(expression, mode="eval")
        result = _evaluate(tree.body)

        if isinstance(result, complex):
            raise ValueError("Complex results are not supported.")

        if not isinstance(result, (int, float)):
            raise ValueError("Invalid calculation result.")

        if abs(result) > 1e100:
            raise ValueError("Result is too large.")

        return result

    except ZeroDivisionError:
        raise ValueError("Cannot divide by zero.") from None
    except (SyntaxError, TypeError, OverflowError):
        raise ValueError("Invalid arithmetic expression.") from None


def _evaluate(node):
    """Evaluate only approved arithmetic syntax."""

    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(
            node.value, (int, float)
        ):
            raise ValueError("Only numbers are allowed.")
        return node.value

    if isinstance(node, ast.BinOp):
        operation = OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported operator.")

        left = _evaluate(node.left)
        right = _evaluate(node.right)

        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("Exponent is too large.")

        return operation(left, right)

    if isinstance(node, ast.UnaryOp):
        operation = OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported operator.")

        return operation(_evaluate(node.operand))

    raise ValueError("Unsupported expression.")
