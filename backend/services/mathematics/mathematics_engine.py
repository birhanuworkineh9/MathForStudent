
import re
import sympy as sp

from sympy import (
    symbols, Eq, solve, simplify, factor, expand,
    diff, integrate, limit, Matrix, sqrt, pi,
    sin, cos, tan, log, exp, oo
)

x, y, z = symbols("x y z")


def result(method, steps, answer):
    return {
        "subject": "Mathematics",
        "method": method,
        "steps": steps,
        "answer": str(answer),
        "status": "success"
    }


def clean_expression(expression):
    """Normalize common mathematical notation."""
    expression = expression.strip()
    expression = expression.replace("^", "**")
    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("−", "-")

    # Convert implicit multiplication: 2x -> 2*x
    expression = re.sub(
        r"(?<=\d)(?=[a-zA-Z(])",
        "*",
        expression
    )

    # Convert x(y+1) and (x+1)(x-1)
    expression = re.sub(
        r"(?<=[a-zA-Z)])(?=\()",
        "*",
        expression
    )

    # Convert xy -> x*y, but preserve known function names
    expression = re.sub(
        r"(?<=[xyz])(?=[xyz])",
        "*",
        expression
    )

    return expression


def parse_expression(expression):
    """Parse a mathematical expression using known symbols."""
    expression = clean_expression(expression)

    local_symbols = {
        "x": x,
        "y": y,
        "z": z,
        "pi": pi,
        "sqrt": sqrt,
        "sin": sin,
        "cos": cos,
        "tan": tan,
        "log": log,
        "exp": exp
    }

    return sp.sympify(
        expression,
        locals=local_symbols
    )


def solve_arithmetic(question):
    """Evaluate a basic arithmetic expression."""
    text = clean_expression(question)

    if not re.fullmatch(r"[0-9+\-*/().\s%]+", text):
        return None

    text = text.replace("%", "/100")

    try:
        answer = sp.sympify(text)

        if answer.free_symbols:
            return None

        return result(
            "Arithmetic",
            [
                f"Original expression: {question}",
                "Apply the order of mathematical operations.",
                f"Calculate the result: {answer}"
            ],
            answer
        )

    except Exception:
        return None


def solve_equation(question):
    """Solve equations for x."""
    text = question.lower().strip()

    text = re.sub(
        r"^(solve|find|calculate)\s+",
        "",
        text
    )

    if "=" not in text:
        return None

    left, right = text.split("=", 1)

    try:
        left_expr = parse_expression(left)
        right_expr = parse_expression(right)

        equation = Eq(left_expr, right_expr)
        solutions = solve(equation, x)

        if not solutions:
            answer = "No solution found"
        else:
            answer = solutions

        return result(
            "Equation solving",
            [
                f"Given equation: {left} = {right}",
                "Write both sides as mathematical expressions.",
                "Move all terms to one side of the equation.",
                "Solve the equation for x.",
                f"Solutions: {solutions}"
            ],
            answer
        )

    except Exception:
        return None


def solve_derivative(question):
    """Differentiate an expression with respect to x."""
    text = question.lower()

    match = re.search(
        r"(?:derivative of|differentiate)\s+(.+)",
        text
    )

    if not match:
        return None

    try:
        function = parse_expression(match.group(1))
        answer = diff(function, x)

        return result(
            "Differentiation",
            [
                f"Given function: f(x) = {function}",
                "Differentiate with respect to x.",
                f"Derivative: {answer}"
            ],
            answer
        )

    except Exception:
        return None


def solve_integral(question):
    """Integrate an expression with respect to x."""
    text = question.lower()

    match = re.search(
        r"(?:integrate|integral of)\s+(.+)",
        text
    )

    if not match:
        return None

    try:
        function = parse_expression(match.group(1))
        answer = integrate(function, x)

        return result(
            "Integration",
            [
                f"Given function: {function}",
                "Integrate with respect to x.",
                f"Indefinite integral: {answer} + C"
            ],
            f"{answer} + C"
        )

    except Exception:
        return None


def solve_factorization(question):
    """Factor an algebraic expression."""
    match = re.search(
        r"(?:factor|factorize)\s+(.+)",
        question.lower()
    )

    if not match:
        return None

    try:
        expression = parse_expression(match.group(1))
        answer = factor(expression)

        return result(
            "Factorization",
            [
                f"Original expression: {expression}",
                "Find the algebraic factors.",
                f"Factorized expression: {answer}"
            ],
            answer
        )

    except Exception:
        return None


def solve_matrix(question):
    """Calculate the determinant of a supplied matrix."""
    match = re.search(
        r"matrix\s*(\[\[.*\]\])",
        question.lower()
    )

    if not match:
        return None

    try:
        values = sp.sympify(match.group(1))
        matrix = Matrix(values)

        if matrix.rows != matrix.cols:
            return {
                "status": "error",
                "message": "The matrix must be square to calculate its determinant."
            }

        determinant = matrix.det()

        return result(
            "Matrix determinant",
            [
                f"Given matrix:\n{matrix}",
                "Calculate the determinant.",
                f"Determinant = {determinant}"
            ],
            determinant
        )

    except Exception:
        return None


def solve_mathematics(question):
    """Main mathematics solving entry point."""
    if not question or not question.strip():
        return {
            "status": "error",
            "message": "Please enter a mathematics question."
        }

    solvers = [
        solve_arithmetic,
        solve_equation,
        solve_derivative,
        solve_integral,
        solve_factorization,
        solve_matrix
    ]

    for solver in solvers:
        answer = solver(question)

        if answer:
            return answer

    return {
        "status": "needs_ai",
        "subject": "Mathematics",
        "message": (
            "This question needs a more advanced mathematical "
            "interpretation. Please provide the complete question."
        )
    }
