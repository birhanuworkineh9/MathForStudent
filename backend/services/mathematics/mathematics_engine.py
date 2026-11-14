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
    expression = expression.strip()
    expression = expression.replace("^", "**")
    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    return expression


def solve_arithmetic(question):
    """
    Evaluate safe arithmetic expressions using SymPy.
    """
    text = clean_expression(question)

    allowed = re.fullmatch(r"[0-9+\-*/().\s%*]+", text)

    if not allowed:
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
                "Convert the expression into mathematical operations.",
                f"Evaluate: {answer}"
            ],
            answer
        )

    except Exception:
        return None


def solve_equation(question):
    """
    Examples:
    solve 2*x + 5 = 15
    x^2 - 5*x + 6 = 0
    """
    text = question.lower().strip()

    text = re.sub(
        r"^(solve|find|calculate)\s+",
        "",
        text
    )

    text = clean_expression(text)

    if "=" not in text:
        return None

    left, right = text.split("=", 1)

    try:
        equation = Eq(
            sp.sympify(left),
            sp.sympify(right)
        )

        solutions = solve(equation, x)

        return result(
            "Equation solving",
            [
                f"Given equation: {left} = {right}",
                "Move the right-hand side to the left.",
                "Solve the resulting equation for x.",
                f"Solutions: {solutions}"
            ],
            solutions
        )

    except Exception:
        return None


def solve_derivative(question):
    """
    Example: derivative of x^3 + 2*x^2
    """
    text = question.lower()

    match = re.search(
        r"(?:derivative of|differentiate)\s+(.+)",
        text
    )

    if not match:
        return None

    expression = clean_expression(match.group(1))

    try:
        function = sp.sympify(expression)
        answer = diff(function, x)

        return result(
            "Differentiation",
            [
                f"Given function: f(x) = {function}",
                "Apply differentiation rules.",
                f"Differentiate with respect to x: {answer}"
            ],
            answer
        )

    except Exception:
        return None


def solve_integral(question):
    """
    Example: integrate x^2
    """
    text = question.lower()

    match = re.search(
        r"(?:integrate|integral of)\s+(.+)",
        text
    )

    if not match:
        return None

    expression = clean_expression(match.group(1))

    try:
        function = sp.sympify(expression)
        answer = integrate(function, x)

        return result(
            "Integration",
            [
                f"Given function: {function}",
                "Apply integration rules.",
                f"Integrate with respect to x: {answer} + C"
            ],
            f"{answer} + C"
        )

    except Exception:
        return None


def solve_factorization(question):
    match = re.search(
        r"(?:factor|factorize)\s+(.+)",
        question.lower()
    )

    if not match:
        return None

    try:
        expression = sp.sympify(
            clean_expression(match.group(1))
        )

        answer = factor(expression)

        return result(
            "Factorization",
            [
                f"Original expression: {expression}",
                "Find common factors or algebraic factors.",
                f"Factorized expression: {answer}"
            ],
            answer
        )

    except Exception:
        return None


def solve_matrix(question):
    """
    Example:
    matrix [[1,2],[3,4]]
    """
    match = re.search(
        r"matrix\s*(\[\[.*\]\])",
        question.lower()
    )

    if not match:
        return None

    try:
        values = sp.sympify(match.group(1))
        matrix = Matrix(values)

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