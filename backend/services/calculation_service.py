
"""
MathForStudent Calculation Engine

Supports:
- Basic arithmetic
- Fractions and decimals
- Percentages
- Ratios
- Powers and roots
- Scientific notation
- Common unit conversions
- Formula evaluation

Python 3.10+
"""

import ast
import math
import operator
import re
from fractions import Fraction


MAX_EXPRESSION_LENGTH = 300
MAX_AST_NODES = 100
MAX_RESULT = 1e100
MAX_EXPONENT = 100

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

UNIT_GROUPS = {
    "length": {
        "mm": 0.001,
        "cm": 0.01,
        "m": 1,
        "km": 1000,
        "inch": 0.0254,
        "ft": 0.3048,
        "mile": 1609.344,
    },
    "mass": {
        "mg": 0.000001,
        "g": 0.001,
        "kg": 1,
        "tonne": 1000,
    },
    "time": {
        "ms": 0.001,
        "s": 1,
        "min": 60,
        "h": 3600,
        "day": 86400,
    },
    "volume": {
        "ml": 0.001,
        "l": 1,
        "m3": 1000,
    },
}


def _validate_number(value):
    if isinstance(value, bool):
        raise ValueError("Boolean values are not allowed.")

    if not isinstance(value, (int, float)):
        raise ValueError("A valid number is required.")

    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Number must be finite.")

    if abs(value) > MAX_RESULT:
        raise ValueError("Number is too large.")

    return value


def _evaluate(node):
    """Safely evaluate approved arithmetic syntax."""

    if isinstance(node, ast.Constant):
        return _validate_number(node.value)

    if isinstance(node, ast.BinOp):
        operation = OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported operator.")

        left = _evaluate(node.left)
        right = _evaluate(node.right)

        if isinstance(node.op, ast.Pow):
            if abs(right) > MAX_EXPONENT:
                raise ValueError("Exponent is too large.")

            if left == 0 and right < 0:
                raise ValueError("Cannot divide by zero.")

        result = operation(left, right)

        return _validate_number(result)

    if isinstance(node, ast.UnaryOp):
        operation = OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported unary operator.")

        return _validate_number(
            operation(_evaluate(node.operand))
        )

    raise ValueError("Unsupported expression syntax.")


def calculate(expression):
    """
    Calculate an arithmetic expression.

    Examples:
        calculate("12 + 8")
        calculate("(20 - 4) / 2")
        calculate("5 ** 2")
        calculate("10 % 3")
    """

    if not isinstance(expression, str):
        raise ValueError("Expression must be text.")

    expression = expression.strip()

    if not expression:
        raise ValueError("Expression cannot be empty.")

    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise ValueError("Expression is too long.")

    try:
        tree = ast.parse(expression, mode="eval")

        if sum(1 for _ in ast.walk(tree)) > MAX_AST_NODES:
            raise ValueError("Expression is too complex.")

        result = _evaluate(tree.body)

        return {
            "operation": "arithmetic",
            "expression": expression,
            "answer": result,
            "steps": [
                "Identify the mathematical operations.",
                "Apply the order of operations.",
                f"Final answer: {result}"
            ]
        }

    except ZeroDivisionError:
        raise ValueError("Cannot divide by zero.") from None
    except (SyntaxError, OverflowError):
        raise ValueError("Invalid arithmetic expression.") from None


def calculate_fraction(numerator, denominator):
    """Calculate and simplify a fraction."""

    numerator = _validate_number(numerator)
    denominator = _validate_number(denominator)

    if denominator == 0:
        raise ValueError("Denominator cannot be zero.")

    fraction = Fraction(numerator) / Fraction(denominator)

    return {
        "operation": "fraction",
        "fraction": str(fraction),
        "decimal": float(fraction),
        "steps": [
            f"Write the fraction: {numerator}/{denominator}",
            "Simplify the numerator and denominator.",
            f"Final answer: {fraction}"
        ]
    }


def calculate_percentage(value, percentage):
    """Find a percentage of a number."""

    value = _validate_number(value)
    percentage = _validate_number(percentage)

    result = value * percentage / 100

    return {
        "operation": "percentage",
        "value": value,
        "percentage": percentage,
        "answer": result,
        "formula": "(value * percentage) / 100",
        "steps": [
            f"Multiply {value} by {percentage}.",
            "Divide the result by 100.",
            f"Final answer: {result}"
        ]
    }


def percentage_change(original, new):
    """Calculate percentage increase or decrease."""

    original = _validate_number(original)
    new = _validate_number(new)

    if original == 0:
        raise ValueError("Original value cannot be zero.")

    change = new - original
    result = (change / abs(original)) * 100

    return {
        "operation": "percentage_change",
        "change": result,
        "type": "increase" if change > 0 else (
            "decrease" if change < 0 else "no change"
        ),
        "steps": [
            f"Change = {new} - {original}",
            "Percentage change = (change / original) × 100",
            f"Final answer: {result}%"
        ]
    }


def calculate_ratio(first, second):
    """Simplify a ratio of two non-negative integers."""

    if (
        isinstance(first, bool)
        or isinstance(second, bool)
        or not isinstance(first, int)
        or not isinstance(second, int)
    ):
        raise ValueError("Ratio values must be integers.")

    if first < 0 or second < 0:
        raise ValueError("Ratio values cannot be negative.")

    if first == 0 and second == 0:
        raise ValueError("Both ratio values cannot be zero.")

    divisor = math.gcd(first, second)

    return {
        "operation": "ratio",
        "original": f"{first}:{second}",
        "simplified": f"{first // divisor}:{second // divisor}",
        "steps": [
            f"Find GCD of {first} and {second}.",
            f"Divide both values by {divisor}.",
            f"Final ratio: {first // divisor}:{second // divisor}"
        ]
    }


def calculate_power(base, exponent):
    """Calculate a number raised to a power."""

    base = _validate_number(base)
    exponent = _validate_number(exponent)

    if abs(exponent) > MAX_EXPONENT:
        raise ValueError("Exponent is too large.")

    if base == 0 and exponent < 0:
        raise ValueError("Zero cannot have a negative exponent.")

    result = base ** exponent

    return {
        "operation": "power",
        "base": base,
        "exponent": exponent,
        "answer": _validate_number(result),
        "steps": [
            f"Base = {base}",
            f"Exponent = {exponent}",
            f"Final answer: {result}"
        ]
    }


def calculate_root(number, degree=2):
    """Calculate a real square, cube or other root."""

    number = _validate_number(number)
    degree = _validate_number(degree)

    if (
        not isinstance(degree, int)
        or degree <= 0
        or degree > 100
    ):
        raise ValueError("Root degree must be an integer from 1 to 100.")

    if number < 0 and degree % 2 == 0:
        raise ValueError("Even root of a negative number is not real.")

    result = (
        -((-number) ** (1 / degree))
        if number < 0
        else number ** (1 / degree)
    )

    return {
        "operation": "root",
        "number": number,
        "degree": degree,
        "answer": result,
        "steps": [
            f"Find the {degree}-th root of {number}.",
            f"Final answer: {result}"
        ]
    }


def scientific_notation(value):
    """Convert a number into scientific notation."""

    value = _validate_number(value)

    if value == 0:
        mantissa, exponent = 0, 0
    else:
        exponent = math.floor(math.log10(abs(value)))
        mantissa = value / (10 ** exponent)

    return {
        "operation": "scientific_notation",
        "mantissa": mantissa,
        "exponent": exponent,
        "answer": f"{mantissa} × 10^{exponent}"
    }


def convert_units(value, from_unit, to_unit):
    """Convert units within the same supported measurement group."""

    value = _validate_number(value)

    if not isinstance(from_unit, str) or not isinstance(to_unit, str):
        raise ValueError("Unit names must be text.")

    from_unit = from_unit.strip().lower()
    to_unit = to_unit.strip().lower()

    for group_name, units in UNIT_GROUPS.items():
        if from_unit in units and to_unit in units:
            base_value = value * units[from_unit]
            result = base_value / units[to_unit]

            return {
                "operation": "unit_conversion",
                "category": group_name,
                "original": f"{value} {from_unit}",
                "answer": result,
                "converted": f"{result} {to_unit}",
                "steps": [
                    f"Convert {value} {from_unit} to the base unit.",
                    f"Convert the base value to {to_unit}.",
                    f"Final answer: {result} {to_unit}"
                ]
            }

    raise ValueError("Unsupported or incompatible units.")



        