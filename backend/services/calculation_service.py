"""
MathForStudent Calculation Engine
=================================
Safe numerical calculation engine for Grade 9 through university.

This module handles numerical calculations only. Symbolic algebra, calculus,
matrices, vectors, probability, differential equations and integral equations
belong in dedicated services coordinated by math_service.py.

Security:
- Parses expressions with Python AST; never uses eval() or exec().
- Allows only explicitly approved operators, names and functions.
- Limits expression size, AST nodes, exponents, factorials and results.
- Rejects non-finite, complex and oversized results.
- No attribute access, imports, indexing, comprehensions or arbitrary calls.

Python 3.10+
"""

from __future__ import annotations

import ast
import math
import operator
import re
from decimal import Decimal, InvalidOperation, localcontext
from fractions import Fraction
from typing import Any, Callable, Mapping

MAX_EXPRESSION_LENGTH = 500
MAX_AST_NODES = 150
MAX_RESULT = 1e100
MAX_EXPONENT = 100
MAX_POWER_BASE = 1e50
MAX_FACTORIAL = 500
MAX_STATISTICS_ITEMS = 100_000
MAX_VARIABLES = 50
DECIMAL_PRECISION = 50

# All linear conversion factors point to one base unit per category.
UNIT_GROUPS: dict[str, dict[str, float]] = {
    "length": {
        "mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0,
        "inch": 0.0254, "in": 0.0254, "ft": 0.3048,
        "yd": 0.9144, "mile": 1609.344,
    },
    "area": {
        "mm2": 1e-6, "cm2": 1e-4, "m2": 1.0, "km2": 1e6,
        "ha": 10000.0, "acre": 4046.8564224, "ft2": 0.09290304,
    },
    "volume": {
        "ml": 0.001, "l": 1.0, "m3": 1000.0, "cm3": 0.001,
        "mm3": 1e-6, "gallon_us": 3.785411784, "cup_us": 0.2365882365,
    },
    "mass": {
        "mg": 1e-6, "g": 0.001, "kg": 1.0, "tonne": 1000.0,
        "lb": 0.45359237, "oz": 0.028349523125,
    },
    "time": {
        "ms": 0.001, "s": 1.0, "sec": 1.0, "min": 60.0,
        "h": 3600.0, "hr": 3600.0, "day": 86400.0, "week": 604800.0,
    },
    "speed": {
        "m/s": 1.0, "km/h": 1.0 / 3.6, "mph": 0.44704, "ft/s": 0.3048,
    },
    "pressure": {
        "pa": 1.0, "kpa": 1000.0, "mpa": 1e6, "bar": 100000.0,
        "atm": 101325.0, "psi": 6894.757293168,
    },
    "energy": {
        "j": 1.0, "kj": 1000.0, "mj": 1e6, "cal": 4.184,
        "kcal": 4184.0, "wh": 3600.0, "kwh": 3.6e6,
    },
    "data": {
        "bit": 1.0, "byte": 8.0, "kb": 8000.0, "mb": 8e6,
        "gb": 8e9, "kib": 8192.0, "mib": 8 * 1024**2,
        "gib": 8 * 1024**3,
    },
}

TEMPERATURE_ALIASES = {
    "c": "c", "°c": "c", "celsius": "c",
    "f": "f", "°f": "f", "fahrenheit": "f",
    "k": "k", "kelvin": "k",
}


def _number(value: Any, name: str = "Number") -> int | float:
    """Return a finite, real, bounded int/float."""
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError(f"{name} must be a real number.")
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError(f"{name} must be finite.")
        # Preserve integer Decimals as integers when possible.
        value = int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{name} must be finite.")
    if abs(value) > MAX_RESULT:
        raise ValueError(f"{name} is too large.")
    return value


def _result(value: Any) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("The result is not a real number.")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("The result is not finite.")
    if abs(value) > MAX_RESULT:
        raise ValueError("The result is too large.")
    return value


def _fraction_value(value: int | float | Decimal) -> Fraction:
    if isinstance(value, float):
        return Fraction(str(value))
    return Fraction(value)


def _factorial(value: int | float) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("Factorial requires a whole number.")
    if not 0 <= value <= MAX_FACTORIAL:
        raise ValueError(f"Factorial must be from 0 to {MAX_FACTORIAL}.")
    return math.factorial(value)


def _root(value: int | float, degree: int | float = 2) -> float:
    value = _number(value, "Value")
    degree = _number(degree, "Root degree")
    if isinstance(degree, bool) or not isinstance(degree, int) or not 1 <= degree <= 100:
        raise ValueError("Root degree must be an integer from 1 to 100.")
    if value < 0:
        if degree % 2 == 0:
            raise ValueError("An even root of a negative number is not real.")
        return _result(-((-value) ** (1.0 / degree)))
    return _result(value ** (1.0 / degree))


def _log(value: int | float, base: int | float = math.e) -> float:
    value, base = _number(value), _number(base, "Log base")
    if value <= 0 or base <= 0 or base == 1:
        raise ValueError("Logarithm requires value > 0 and base > 0, base != 1.")
    return _result(math.log(value, base))


def _integer_function(name: str, function: Callable[..., int], *args: int | float) -> int:
    if any(isinstance(x, bool) or not isinstance(x, int) for x in args):
        raise ValueError(f"{name} requires integer arguments.")
    return function(*args)


FUNCTIONS: dict[str, Callable[..., Any]] = {
    "abs": abs, "sqrt": math.sqrt, "cbrt": lambda x: _root(x, 3),
    "root": _root, "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
    "log": _log, "log10": math.log10, "ln": math.log, "exp": math.exp,
    "floor": math.floor, "ceil": math.ceil, "factorial": _factorial,
    "gcd": lambda *x: _integer_function("gcd", math.gcd, *x),
    "lcm": lambda *x: _integer_function("lcm", math.lcm, *x),
    "min": min, "max": max, "round": round,
}
CONSTANTS = {"pi": math.pi, "e": math.e, "tau": math.tau}
BINARY_OPERATORS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
}
UNARY_OPERATORS = {ast.USub: operator.neg, ast.UAdd: operator.pos}


def _evaluate(node: ast.AST, variables: Mapping[str, int | float]) -> int | float:
    if isinstance(node, ast.Constant):
        return _number(node.value, "Constant")
    if isinstance(node, ast.Name):
        if node.id in CONSTANTS:
            return CONSTANTS[node.id]
        if node.id in variables:
            return _number(variables[node.id], f"Variable {node.id}")
        raise ValueError(f"Unknown variable or constant: {node.id}")
    if isinstance(node, ast.BinOp):
        fn = BINARY_OPERATORS.get(type(node.op))
        if fn is None:
            raise ValueError("Unsupported arithmetic operator.")
        left, right = _evaluate(node.left, variables), _evaluate(node.right, variables)
        if isinstance(node.op, ast.Pow):
            if abs(right) > MAX_EXPONENT:
                raise ValueError(f"Exponent magnitude cannot exceed {MAX_EXPONENT}.")
            if abs(left) > MAX_POWER_BASE and abs(right) > 1:
                raise ValueError("Power calculation is too large.")
            if left == 0 and right < 0:
                raise ValueError("Zero cannot be raised to a negative power.")
        return _result(fn(left, right))
    if isinstance(node, ast.UnaryOp):
        fn = UNARY_OPERATORS.get(type(node.op))
        if fn is None:
            raise ValueError("Unsupported unary operator.")
        return _result(fn(_evaluate(node.operand, variables)))
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only approved mathematical functions are allowed.")
        fn = FUNCTIONS.get(node.func.id)
        if fn is None or node.keywords:
            raise ValueError(f"Unsupported function: {node.func.id}")
        if not 1 <= len(node.args) <= 3:
            raise ValueError("Function argument count is not supported.")
        args = [_evaluate(arg, variables) for arg in node.args]
        try:
            return _result(fn(*args))
        except (TypeError, OverflowError, ValueError) as exc:
            raise ValueError(str(exc) or "Invalid function arguments.") from None
    raise ValueError("Unsupported expression syntax.")


def calculate(expression: str, variables: Mapping[str, int | float] | None = None) -> dict[str, Any]:
    """Safely evaluate a numerical expression. Trigonometry uses radians."""
    if not isinstance(expression, str):
        raise ValueError("Expression must be text.")
    expression = expression.strip()
    if not expression:
        raise ValueError("Expression cannot be empty.")
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise ValueError("Expression is too long.")
    if "^" in expression:
        expression = expression.replace("^", "**")
    variables = {} if variables is None else variables
    if not isinstance(variables, Mapping) or len(variables) > MAX_VARIABLES:
        raise ValueError(f"Variables must be a mapping with at most {MAX_VARIABLES} entries.")
    for key, value in variables.items():
        if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise ValueError("Variable names must be valid identifiers.")
        _number(value, f"Variable {key}")
        if key in CONSTANTS or key in FUNCTIONS:
            raise ValueError(f"Variable name '{key}' is reserved.")
    try:
        tree = ast.parse(expression, mode="eval")
        if sum(1 for _ in ast.walk(tree)) > MAX_AST_NODES:
            raise ValueError("Expression is too complex.")
        answer = _evaluate(tree.body, variables)
    except ZeroDivisionError:
        raise ValueError("Cannot divide by zero.") from None
    except (SyntaxError, OverflowError, RecursionError):
        raise ValueError("Invalid or excessively complex arithmetic expression.") from None
    return {
        "operation": "arithmetic", "expression": expression, "answer": answer,
        "steps": [
            "Identify the numbers, variables and operations.",
            "Apply parentheses and the order of operations.",
            f"Evaluate the expression to obtain {answer}.",
        ],
        "note": "Trigonometric functions use radians.",
    }


def calculate_fraction(numerator: int | float, denominator: int | float) -> dict[str, Any]:
    numerator, denominator = _number(numerator, "Numerator"), _number(denominator, "Denominator")
    if denominator == 0:
        raise ValueError("Denominator cannot be zero.")
    fraction = _fraction_value(numerator) / _fraction_value(denominator)
    return {
        "operation": "fraction", "fraction": str(fraction),
        "numerator": fraction.numerator, "denominator": fraction.denominator,
        "decimal": float(fraction),
        "steps": [
            f"Start with {numerator}/{denominator}.",
            "Convert decimal inputs to exact decimal fractions where possible.",
            f"Simplified fraction: {fraction}.",
        ],
    }


def calculate_percentage(value: int | float, percentage: int | float) -> dict[str, Any]:
    value, percentage = _number(value, "Value"), _number(percentage, "Percentage")
    answer = _result(value * percentage / 100)
    return {
        "operation": "percentage", "value": value, "percentage": percentage,
        "answer": answer, "formula": "(value × percentage) / 100",
        "steps": [
            f"Multiply {value} by {percentage}: {value * percentage}.",
            "Divide the product by 100.", f"Answer: {answer}.",
        ],
    }


def percentage_change(original: int | float, new: int | float) -> dict[str, Any]:
    original, new = _number(original, "Original value"), _number(new, "New value")
    if original == 0:
        raise ValueError("Percentage change is undefined when the original value is zero.")
    change = new - original
    percent = _result(change / abs(original) * 100)
    kind = "increase" if change > 0 else "decrease" if change < 0 else "no change"
    return {
        "operation": "percentage_change", "original": original, "new": new,
        "absolute_change": change, "percentage_change": percent, "type": kind,
        "steps": [
            f"Change = {new} - {original} = {change}.",
            "Percentage change = change / |original| × 100.",
            f"Result: {percent}% ({kind}).",
        ],
        "note": "The absolute original value is used as the percentage base.",
    }


def calculate_ratio(first: int, second: int) -> dict[str, Any]:
    if any(isinstance(x, bool) or not isinstance(x, int) for x in (first, second)):
        raise ValueError("Ratio values must be integers.")
    if first < 0 or second < 0:
        raise ValueError("This ratio function accepts non-negative integers.")
    if first == second == 0:
        raise ValueError("A ratio cannot have both parts equal to zero.")
    divisor = math.gcd(first, second)
    simplified = f"{first // divisor}:{second // divisor}"
    return {
        "operation": "ratio", "original": f"{first}:{second}",
        "gcd": divisor, "simplified": simplified,
        "steps": [
            f"GCD({first}, {second}) = {divisor}.",
            f"Divide both parts by {divisor}.",
            f"Simplified ratio: {simplified}.",
        ],
    }


def solve_proportion(a: int | float, b: int | float, c: int | float) -> dict[str, Any]:
    """Solve a:b = c:x, where a and b must define a valid ratio."""
    a, b, c = _number(a, "a"), _number(b, "b"), _number(c, "c")
    if a == 0 or b == 0:
        raise ValueError("The first ratio a:b is undefined when a or b is zero.")
    answer = _result(b * c / a)
    return {
        "operation": "proportion", "equation": f"{a}:{b} = {c}:x", "answer": answer,
        "steps": [
            f"Write the proportion: {a}/{b} = {c}/x.",
            f"Cross multiply: {a}x = {b} × {c}.",
            f"x = ({b} × {c}) / {a} = {answer}.",
        ],
    }


def calculate_power(base: int | float, exponent: int | float) -> dict[str, Any]:
    base, exponent = _number(base, "Base"), _number(exponent, "Exponent")
    if abs(exponent) > MAX_EXPONENT:
        raise ValueError(f"Exponent magnitude cannot exceed {MAX_EXPONENT}.")
    if base == 0 and exponent < 0:
        raise ValueError("Zero cannot have a negative exponent.")
    if abs(base) > MAX_POWER_BASE and abs(exponent) > 1:
        raise ValueError("Power calculation is too large.")
    answer = _result(base ** exponent)
    return {
        "operation": "power", "base": base, "exponent": exponent, "answer": answer,
        "steps": [
            f"Base = {base}; exponent = {exponent}.",
            "Apply the exponent to the base.",
            f"Answer: {answer}.",
        ],
    }


def calculate_root(number: int | float, degree: int = 2) -> dict[str, Any]:
    number = _number(number, "Number")
    answer = _root(number, degree)
    return {
        "operation": "root", "number": number, "degree": degree, "answer": answer,
        "steps": [
            f"Find the {degree}-th root of {number}.",
            f"Check by raising {answer} to the power {degree}.",
            f"Approximate answer: {answer}.",
        ],
    }


def scientific_notation(value: int | float) -> dict[str, Any]:
    value = _number(value, "Value")
    if value == 0:
        mantissa, exponent = 0.0, 0
    else:
        with localcontext() as ctx:
            ctx.prec = DECIMAL_PRECISION
            dec = Decimal(str(value))
            exponent = dec.copy_abs().adjusted()
            mantissa = float(dec.scaleb(-exponent))
    return {
        "operation": "scientific_notation", "mantissa": mantissa,
        "exponent": exponent, "answer": f"{mantissa} × 10^{exponent}",
        "steps": [
            "Move the decimal point until the mantissa has absolute value from 1 to less than 10 (unless zero).",
            f"The power of ten is {exponent}.",
            f"Scientific notation: {mantissa} × 10^{exponent}.",
        ],
    }


def convert_temperature(value: int | float, from_unit: str, to_unit: str) -> dict[str, Any]:
    value = _number(value, "Temperature")
    if not isinstance(from_unit, str) or not isinstance(to_unit, str):
        raise ValueError("Temperature unit names must be text.")
    source = TEMPERATURE_ALIASES.get(from_unit.strip().lower())
    target = TEMPERATURE_ALIASES.get(to_unit.strip().lower())
    if source is None or target is None:
        raise ValueError("Temperature units must be Celsius, Fahrenheit or Kelvin.")
    if source == "k" and value < 0:
        raise ValueError("Kelvin temperature cannot be below absolute zero.")
    celsius = value if source == "c" else (value - 32) * 5 / 9 if source == "f" else value - 273.15
    answer = celsius if target == "c" else celsius * 9 / 5 + 32 if target == "f" else celsius + 273.15
    if target == "k" and answer < 0:
        raise ValueError("Temperature cannot be below absolute zero.")
    answer = _result(answer)
    return {
        "operation": "temperature_conversion", "original": f"{value} {source.upper()}",
        "answer": answer, "converted": f"{answer} {target.upper()}",
        "steps": [
            "Convert the original temperature to Celsius.",
            f"Convert Celsius to {target.upper()}.",
            f"Answer: {answer} {target.upper()}.",
        ],
    }


def convert_units(value: int | float, from_unit: str, to_unit: str) -> dict[str, Any]:
    value = _number(value, "Value")
    if not isinstance(from_unit, str) or not isinstance(to_unit, str):
        raise ValueError("Unit names must be text.")
    source, target = from_unit.strip().lower(), to_unit.strip().lower()
    if source in TEMPERATURE_ALIASES or target in TEMPERATURE_ALIASES:
        return convert_temperature(value, source, target)
    for category, units in UNIT_GROUPS.items():
        if source in units and target in units:
            base = value * units[source]
            answer = _result(base / units[target])
            return {
                "operation": "unit_conversion", "category": category,
                "original": f"{value} {source}", "answer": answer,
                "converted": f"{answer} {target}",
                "steps": [
                    f"Convert {value} {source} to the {category} base unit.",
                    f"Convert the base value to {target}.",
                    f"Answer: {answer} {target}.",
                ],
            }
    raise ValueError(f"Unsupported or incompatible units: {from_unit} to {to_unit}.")


def evaluate_formula(formula: str, variables: Mapping[str, int | float]) -> dict[str, Any]:
    result = calculate(formula, variables)
    result["operation"] = "formula"
    result["variables"] = dict(variables)
    result["steps"].insert(0, f"Substitute the supplied values: {dict(variables)}.")
    return result


def calculate_statistics(data: list[int | float]) -> dict[str, Any]:
    if not isinstance(data, (list, tuple)) or not data:
        raise ValueError("Statistics require a non-empty list of numbers.")
    if len(data) > MAX_STATISTICS_ITEMS:
        raise ValueError(f"Statistics input cannot exceed {MAX_STATISTICS_ITEMS} values.")
    values = [_number(x, "Data value") for x in data]
    ordered = sorted(values)
    count = len(values)
    mean = math.fsum(values) / count
    middle = count // 2
    median = ordered[middle] if count % 2 else (ordered[middle - 1] + ordered[middle]) / 2
    frequencies: dict[int | float, int] = {}
    for item in values:
        frequencies[item] = frequencies.get(item, 0) + 1
    highest_frequency = max(frequencies.values())
    modes = sorted(k for k, v in frequencies.items() if v == highest_frequency) if highest_frequency > 1 else []
    data_range = ordered[-1] - ordered[0]
    population_variance = math.fsum((x - mean) ** 2 for x in values) / count
    sample_variance = (
        math.fsum((x - mean) ** 2 for x in values) / (count - 1) if count > 1 else None
    )
    return {
        "operation": "statistics", "count": count, "mean": _result(mean),
        "median": _result(median), "mode": modes, "range": _result(data_range),
        "minimum": ordered[0], "maximum": ordered[-1],
        "population_variance": _result(population_variance),
        "population_standard_deviation": _result(math.sqrt(population_variance)),
        "sample_variance": _result(sample_variance) if sample_variance is not None else None,
        "sample_standard_deviation": _result(math.sqrt(sample_variance)) if sample_variance is not None else None,
        "steps": [
            f"Count the values: n = {count}.",
            f"Mean = sum / n = {mean}.",
            f"Median = middle value(s) = {median}.",
            f"Range = maximum - minimum = {data_range}.",
            "Variance is the average squared distance from the mean (population or sample formula).",
        ],
        "note": "Sample variance and sample standard deviation are undefined for a single value.",
    }


__all__ = [
    "calculate", "calculate_fraction", "calculate_percentage", "percentage_change",
    "calculate_ratio", "solve_proportion", "calculate_power", "calculate_root",
    "scientific_notation", "convert_temperature", "convert_units",
    "evaluate_formula", "calculate_statistics",
]
