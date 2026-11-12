
"""
MathForStudent Calculation Service

Provides safe basic arithmetic calculations
for Grade 9 through University students.
"""

import ast
import math
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

MAX_EXPRESSION_LENGTH = 200
MAX_AST_NODES = 100
MAX_ABS_RESULT = 1e100
MAX_EXPONENT = 100


def calculate(expression: str):
    """
    Safely calculate a basic arithmetic expression.

    Supported:
    + Addition
    - Subtraction
    * Multiplication
    / Division
    ** Powers
    % Modulo
    Parentheses and negative numbers

    Examples:
        10 + 5
        (20 - 4) / 2
        5 ** 2
        -8 + 3
    """

    if not isinstance(expression, str):
        raise ValueError("Expression must be text.")

    expression = expression.strip()

    if not expression:
        raise ValueError("Please enter an expression.")

    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise ValueError("Expression is too long.")

    try:
        tree = ast.parse(expression, mode="eval")

        node_count = sum(1 for _ in ast.walk(tree))

        if node_count > MAX_AST_NODES:
            raise ValueError("Expression is too complex.")

        result = _evaluate(tree.body)

        if isinstance(result, bool):
            raise ValueError("Boolean results are not allowed.")

        if not isinstance(result, (int, float)):
            raise ValueError("Invalid calculation result.")

        if isinstance(result, float) and not math.isfinite(result):
            raise ValueError("Result is not a finite number.")

        if abs(result) > MAX_ABS_RESULT:
            raise ValueError("Result is too large.")

        return result

    except ZeroDivisionError:
        raise ValueError("Cannot divide by zero.") from None

    except (SyntaxError, OverflowError):
        raise ValueError("Invalid or excessively large expression.") from None


def _evaluate(node):
    """Evaluate only approved arithmetic operations."""

    if isinstance(node, ast.Constant):
        value = node.value

        if isinstance(value, bool):
            raise ValueError("Boolean values are not allowed.")

        if not isinstance(value, (int, float)):
            raise ValueError("Only numeric values are allowed.")

        if isinstance(value, int) and abs(value) > MAX_ABS_RESULT:
            raise ValueError("Number is too large.")

        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("Invalid numeric value.")

        return value

    if isinstance(node, ast.BinOp):
        operation = OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported arithmetic operator.")

        left = _evaluate(node.left)
        right = _evaluate(node.right)

        if isinstance(node.op, ast.Pow):
            if abs(right) > MAX_EXPONENT:
                raise ValueError("Exponent is too large.")

            if left == 0 and right < 0:
                raise ZeroDivisionError

        result = operation(left, right)

        if isinstance(result, float) and not math.isfinite(result):
            raise ValueError("Calculation result is not finite.")

        if abs(result) > MAX_ABS_RESULT:
            raise ValueError("Calculation result is too large.")

        return result

    if isinstance(node, ast.UnaryOp):
        operation = OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported unary operator.")

        return operation(_evaluate(node.operand))

    raise ValueError("Unsupported expression syntax.")


