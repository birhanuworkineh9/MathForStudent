"""
MathForStudent Mathematics Engine
=================================

A safe, SymPy-powered symbolic mathematics service.

Features
--------
- Safe expression parsing (AST allow-list; never eval/exec)
- Algebra: simplify, expand, factor, collect
- Equations: solve for one or more variables
- Differentiation and integration
- Limits, series, substitution and numerical evaluation
- Polynomial degree and roots
- Linear systems (equations separated by semicolons)
- Step summaries suitable for an AI tutor/UI

Public compatibility
--------------------
The main entry point remains solve_math_problem(problem, operation="auto").
The result is a JSON-friendly dictionary containing topic, original,
answer, steps, and operation-specific details.

This engine deliberately does not claim to solve every possible math problem.
Unsupported or ambiguous input is rejected with a useful error instead of
returning a misleading answer.
"""

from __future__ import annotations

import ast
import math
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import sympy as sp


# ---------------------------------------------------------------------------
# Limits and symbols
# ---------------------------------------------------------------------------

MAX_EXPRESSION_LENGTH = 1000
MAX_PROBLEM_LENGTH = 4000
MAX_AST_NODES = 250
MAX_ABS_EXPONENT = 100
MAX_VARIABLES = 12
MAX_EQUATIONS = 12
MAX_SERIES_ORDER = 20

DEFAULT_SYMBOL_NAMES = ("x", "y", "z", "a", "b", "c", "t", "n")

SYMBOLS: Dict[str, sp.Symbol] = {
    name: sp.Symbol(name, real=True) for name in DEFAULT_SYMBOL_NAMES
}
SYMBOLS.update({
    "pi": sp.pi,
    "E": sp.E,
    "e": sp.E,
    "I": sp.I,
    "oo": sp.oo,
})

FUNCTIONS = {
    "sqrt": sp.sqrt,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "sinh": sp.sinh,
    "cosh": sp.cosh,
    "tanh": sp.tanh,
    "log": sp.log,
    "ln": sp.log,
    "log10": lambda value: sp.log(value, 10),
    "exp": sp.exp,
    "abs": sp.Abs,
    "Abs": sp.Abs,
    "floor": sp.floor,
    "ceil": sp.ceiling,
    "factorial": sp.factorial,
    "gamma": sp.gamma,
    "sign": sp.sign,
    "min": sp.Min,
    "max": sp.Max,
}

BINARY_OPERATORS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a ** b,
    ast.Mod: lambda a, b: sp.Mod(a, b),
}

UNARY_OPERATORS = {
    ast.UAdd: lambda value: value,
    ast.USub: lambda value: -value,
}


# ---------------------------------------------------------------------------
# Parsing and validation
# ---------------------------------------------------------------------------

def _normalise_expression(text: str) -> str:
    """Normalise common classroom notation into Python-compatible syntax."""
    text = text.strip()
    text = text.replace("^", "**")
    text = text.replace("−", "-").replace("×", "*").replace("÷", "/")
    text = text.replace("π", "pi")
    # Convert a simple number followed by a variable/parenthesis to explicit *.
    text = re.sub(r"(?<=\d)(?=[a-zA-Z(])", "*", text)
    text = re.sub(r"(?<=\))(?=[a-zA-Z0-9(])", "*", text)
    text = re.sub(r"(?<=[a-zA-Z])(?=\()", "*", text) if False else text
    return text


def _validate_tree(tree: ast.AST) -> None:
    nodes = list(ast.walk(tree))
    if len(nodes) > MAX_AST_NODES:
        raise ValueError("Expression is too complex. Please split it into smaller parts.")
    # The strict _convert allow-list rejects every unsupported node type.


def _convert(node: ast.AST) -> sp.Expr:
    if isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Only numeric constants are allowed.")
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("Non-finite numbers are not allowed.")
        return sp.Rational(str(value)) if isinstance(value, float) else sp.Integer(value)

    if isinstance(node, ast.Name):
        if node.id in SYMBOLS:
            value = SYMBOLS[node.id]
            if isinstance(value, sp.Symbol):
                return value
            return value
        raise ValueError(f"Unknown symbol '{node.id}'. Allowed variables: {', '.join(DEFAULT_SYMBOL_NAMES)}.")

    if isinstance(node, ast.BinOp):
        left = _convert(node.left)
        right = _convert(node.right)
        for operator_type, operation in BINARY_OPERATORS.items():
            if isinstance(node.op, operator_type):
                if isinstance(node.op, ast.Pow) and right.is_number:
                    try:
                        if abs(float(right)) > MAX_ABS_EXPONENT:
                            raise ValueError("Exponent is too large.")
                    except (TypeError, OverflowError):
                        raise ValueError("Exponent is outside the supported range.")
                return operation(left, right)
        raise ValueError("Unsupported mathematical operator.")

    if isinstance(node, ast.UnaryOp):
        value = _convert(node.operand)
        for operator_type, operation in UNARY_OPERATORS.items():
            if isinstance(node.op, operator_type):
                return operation(value)
        raise ValueError("Unsupported unary operator.")

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only direct calls to approved math functions are allowed.")
        function = FUNCTIONS.get(node.func.id)
        if function is None or node.keywords:
            raise ValueError(f"Unsupported function '{node.func.id}'.")
        args = [_convert(arg) for arg in node.args]
        if node.func.id in ("min", "max"):
            if len(args) < 1:
                raise ValueError(f"{node.func.id} requires at least one argument.")
        elif len(args) != 1:
            raise ValueError(f"{node.func.id} requires exactly one argument.")
        return function(*args)

    raise ValueError("Unsupported expression syntax.")


def parse_expression(text: str) -> sp.Expr:
    """Parse a mathematical expression using a strict AST allow-list."""
    if not isinstance(text, str):
        raise ValueError("Expression must be text.")
    text = _normalise_expression(text)
    if not text or len(text) > MAX_EXPRESSION_LENGTH:
        raise ValueError("Expression is empty or too long.")
    try:
        tree = ast.parse(text, mode="eval")
        if len(list(ast.walk(tree))) > MAX_AST_NODES:
            raise ValueError("Expression is too complex.")
        return _convert(tree.body)
    except (SyntaxError, RecursionError, OverflowError) as exc:
        raise ValueError("Invalid or overly complex mathematical expression.") from exc


def _json_value(value: Any) -> Any:
    """Convert SymPy values to JSON-friendly strings/lists/dicts."""
    if isinstance(value, dict):
        return {str(k): _json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, sp.FiniteSet)):
        return [_json_value(item) for item in value]
    return str(value)


def _symbols_for(expressions: Iterable[sp.Expr]) -> List[sp.Symbol]:
    found = set()
    for expression in expressions:
        found.update(expression.free_symbols)
    return sorted(found, key=lambda item: item.name)


def _select_variable(expressions: Sequence[sp.Expr], variable: Optional[str]) -> sp.Symbol:
    symbols = _symbols_for(expressions)
    if variable:
        if variable not in SYMBOLS or not isinstance(SYMBOLS[variable], sp.Symbol):
            raise ValueError(f"Unsupported variable '{variable}'.")
        return SYMBOLS[variable]
    if not symbols:
        return SYMBOLS["x"]
    if len(symbols) == 1:
        return symbols[0]
    if sp.Symbol("x", real=True) in symbols:
        return SYMBOLS["x"]
    return symbols[0]


def _parse_equation(text: str) -> sp.Equality:
    if text.count("=") != 1:
        raise ValueError("Each equation must contain exactly one '=' sign.")
    left, right = text.split("=", 1)
    if not left.strip() or not right.strip():
        raise ValueError("Both sides of the equation are required.")
    return sp.Eq(parse_expression(left), parse_expression(right))


def _result(topic: str, original: str, answer: Any, steps: List[str],
            operation: str, **extra: Any) -> Dict[str, Any]:
    payload = {
        "topic": topic,
        "operation": operation,
        "original": original,
        "answer": _json_value(answer),
        "steps": steps,
    }
    payload.update({key: _json_value(value) for key, value in extra.items()})
    return payload


# ---------------------------------------------------------------------------
# Main service
# ---------------------------------------------------------------------------

def solve_math_problem(
    problem: str,
    operation: str = "auto",
    variable: Optional[str] = None,
    substitutions: Optional[Mapping[str, Any]] = None,
    point: Any = 0,
    order: int = 6,
    precision: int = 12,
) -> Dict[str, Any]:
    """
    Solve a symbolic mathematics request.

    Supported operations:
      auto, simplify, expand, factor, collect, solve, differentiate,
      integrate, limit, series, evaluate, roots, degree, system

    Examples:
      solve_math_problem("2*x + 4 = 10")
      solve_math_problem("x**2 - 5*x + 6", operation="factor")
      solve_math_problem("sin(x)*x**2", operation="differentiate")
      solve_math_problem("1/x", operation="limit", point=0)
      solve_math_problem("x**2 + 2*x + 1", operation="evaluate",
                         substitutions={"x": 3})
      solve_math_problem("x+y=5; x-y=1", operation="system")
    """
    if not isinstance(problem, str):
        raise ValueError("Problem must be text.")
    problem = problem.strip()
    if not problem or len(problem) > MAX_PROBLEM_LENGTH:
        raise ValueError("Problem is empty or too long.")

    operation = str(operation or "auto").strip().lower()
    aliases = {
        "differentiate": "differentiate", "derivative": "differentiate",
        "integrate": "integrate", "integration": "integrate",
        "factorize": "factor", "factorise": "factor",
        "differentiate_x": "differentiate",
        "numerical": "evaluate", "substitute": "evaluate",
        "linear_system": "system",
    }
    operation = aliases.get(operation, operation)

    allowed = {
        "auto", "simplify", "expand", "factor", "collect", "solve",
        "differentiate", "integrate", "limit", "series", "evaluate",
        "roots", "degree", "system",
    }
    if operation not in allowed:
        raise ValueError(f"Unsupported operation '{operation}'.")

    if operation == "system":
        raw_equations = [part.strip() for part in problem.split(";") if part.strip()]
        if not raw_equations or len(raw_equations) > MAX_EQUATIONS:
            raise ValueError(f"Provide between 1 and {MAX_EQUATIONS} equations separated by semicolons.")
        equations = [_parse_equation(item) for item in raw_equations]
        symbols = _symbols_for([eq.lhs - eq.rhs for eq in equations])
        if not symbols:
            raise ValueError("The system contains no variables.")
        if len(symbols) > MAX_VARIABLES:
            raise ValueError("Too many variables in the system.")
        solutions = sp.solve(equations, symbols, dict=True)
        return _result(
            "Systems of Equations", problem, solutions,
            ["Separate the input into individual equations.",
             "Identify the unknown variables.",
             "Solve the equations simultaneously.",
             f"Found {len(solutions)} solution set(s)."],
            operation, variables=[str(s) for s in symbols],
            equations=[str(eq) for eq in equations],
        )

    if operation == "solve" or (operation == "auto" and "=" in problem):
        equation = _parse_equation(problem)
        expression = equation.lhs - equation.rhs
        symbols = _symbols_for([expression])
        target = _select_variable([expression], variable)
        solutions = sp.solve(equation, target)
        return _result(
            "Algebra and Equations", problem, solutions,
            ["Write the equation with all terms on one side.",
             f"Solve for {target}.",
             f"Check the candidate solution(s) in the original equation.",
             f"Solution set: {solutions}"],
            "solve", variable=str(target), equation=str(equation),
            solution_count=len(solutions),
        )

    expression = parse_expression(problem)
    symbols = _symbols_for([expression])
    target = _select_variable([expression], variable)

    if operation in ("auto", "simplify"):
        answer = sp.simplify(expression)
        topic = "Algebra and Simplification"
        steps = ["Identify the mathematical expression.",
                 "Apply symbolic simplification.",
                 f"Simplified result: {answer}"]
        selected = "simplify"

    elif operation == "expand":
        answer = sp.expand(expression)
        topic = "Algebraic Expansion"
        steps = ["Identify products and powers.",
                 "Apply the distributive law and expand powers.",
                 f"Expanded result: {answer}"]
        selected = operation

    elif operation == "factor":
        answer = sp.factor(expression)
        topic = "Factorization"
        steps = ["Identify the algebraic expression.",
                 "Find common factors or polynomial factors.",
                 f"Factorized result: {answer}"]
        selected = operation

    elif operation == "collect":
        answer = sp.collect(sp.expand(expression), target)
        topic = "Collecting Like Terms"
        steps = [f"Group terms by powers of {target}.",
                 f"Collected result: {answer}"]
        selected = operation

    elif operation == "differentiate":
        answer = sp.diff(expression, target)
        topic = "Differentiation"
        steps = [f"Differentiate with respect to {target}.",
                 "Apply the relevant differentiation rules.",
                 f"Derivative: {answer}"]
        selected = operation

    elif operation == "integrate":
        answer = sp.integrate(expression, target)
        topic = "Integration"
        steps = [f"Integrate with respect to {target}.",
                 "Apply the relevant integration rules.",
                 f"Antiderivative: {answer} + C"]
        selected = operation

    elif operation == "limit":
        if isinstance(point, str):
            point_expr = parse_expression(point)
        else:
            point_expr = sp.sympify(point)
        answer = sp.limit(expression, target, point_expr)
        topic = "Limits"
        steps = [f"Identify the limit as {target} approaches {point_expr}.",
                 "Evaluate the symbolic limit.",
                 f"Limit: {answer}"]
        selected = operation

    elif operation == "series":
        if not isinstance(order, int) or not 1 <= order <= MAX_SERIES_ORDER:
            raise ValueError(f"Series order must be between 1 and {MAX_SERIES_ORDER}.")
        answer = sp.series(expression, target, 0, order)
        topic = "Power Series"
        steps = [f"Expand around {target} = 0.",
                 f"Keep terms up to order {order - 1}.",
                 f"Series: {answer}"]
        selected = operation

    elif operation == "evaluate":
        if not isinstance(substitutions, Mapping) or not substitutions:
            raise ValueError("Provide substitutions, for example {'x': 2}.")
        mapping = {}
        for name, value in substitutions.items():
            if name not in SYMBOLS or not isinstance(SYMBOLS[name], sp.Symbol):
                raise ValueError(f"Unsupported substitution variable '{name}'.")
            try:
                numeric = sp.sympify(value)
            except (sp.SympifyError, TypeError, ValueError) as exc:
                raise ValueError(f"Invalid value for '{name}'.") from exc
            if numeric.free_symbols:
                raise ValueError("Substitution values must be numeric.")
            mapping[SYMBOLS[name]] = numeric
        answer = expression.subs(mapping)
        topic = "Substitution and Evaluation"
        steps = ["Identify the given variable values.",
                 "Substitute each value into the expression.",
                 f"Result: {answer}"]
        selected = operation

    elif operation == "roots":
        polynomial = sp.Poly(expression, target)
        answer = sp.solve(polynomial.as_expr(), target)
        topic = "Polynomial Roots"
        steps = [f"Set the polynomial equal to zero.",
                 f"Solve for {target}.",
                 f"Root(s): {answer}"]
        selected = operation

    elif operation == "degree":
        polynomial = sp.Poly(expression, target)
        answer = polynomial.degree()
        topic = "Polynomial Degree"
        steps = [f"Write the expression as a polynomial in {target}.",
                 f"The highest power of {target} is {answer}."]
        selected = operation

    else:
        raise ValueError("This operation is not implemented.")

    extra = {
        "variable": str(target),
        "variables": [str(item) for item in symbols],
    }
    if selected in ("simplify", "expand", "factor", "collect"):
        extra["expanded"] = sp.expand(expression)
        extra["factorized"] = sp.factor(expression)
    if selected == "differentiate":
        extra["second_derivative"] = sp.diff(expression, target, 2)
    return _result(topic, problem, answer, steps, selected, **extra)


def solve_equation(problem: str, variable: Optional[str] = None) -> Dict[str, Any]:
    """Convenience wrapper for solving one equation."""
    return solve_math_problem(problem, operation="solve", variable=variable)


def differentiate(problem: str, variable: Optional[str] = None) -> Dict[str, Any]:
    """Convenience wrapper for symbolic differentiation."""
    return solve_math_problem(problem, operation="differentiate", variable=variable)


def integrate(problem: str, variable: Optional[str] = None) -> Dict[str, Any]:
    """Convenience wrapper for symbolic integration."""
    return solve_math_problem(problem, operation="integrate", variable=variable)


__all__ = [
    "parse_expression",
    "solve_math_problem",
    "solve_equation",
    "differentiate",
    "integrate",
    "SYMBOLS",
    "FUNCTIONS",
]

