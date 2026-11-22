
import re
import sympy as sp
from sympy import (
    symbols, Eq, solve, simplify, expand, factor,
    diff, integrate, Matrix, sin, cos, tan, log,
    exp, sqrt, pi, Rational, oo
)

x, y, z = symbols("x y z")


def make_result(method, steps, answer):
    return {
        "status": "success",
        "subject": "Mathematics",
        "method": method,
        "steps": steps,
        "answer": str(answer)
    }


def clean_expression(text):
    text = text.strip()
    text = text.replace("^", "**")
    text = text.replace("×", "*")
    text = text.replace("÷", "/")
    text = text.replace("−", "-")
    text = re.sub(r"(?<=\d)(?=[a-zA-Z(])", "*", text)
    text = re.sub(r"(?<=[a-zA-Z)])(?=\()", "*", text)
    return text


def parse_expression(text):
    allowed = {
        "x": x, "y": y, "z": z,
        "pi": pi, "sqrt": sqrt,
        "sin": sin, "cos": cos,
        "tan": tan, "log": log, "ln": log,
        "exp": exp
    }
    return sp.sympify(clean_expression(text), locals=allowed)


def solve_arithmetic(question):
    text = clean_expression(question)

    if not re.fullmatch(r"[0-9+\-*/().\s%]+", text):
        return None

    try:
        text = text.replace("%", "/100")
        answer = sp.sympify(text)

        if answer.free_symbols:
            return None

        return make_result(
            "Arithmetic",
            [
                f"Given expression: {question}",
                "Step 1: Identify the operations.",
                "Step 2: Apply the order of operations (BODMAS).",
                f"Step 3: Calculate the result: {answer}"
            ],
            answer
        )
    except Exception:
        return None


def solve_linear_equation(left, right):
    left_expr = expand(parse_expression(left))
    right_expr = expand(parse_expression(right))
    reduced = expand(left_expr - right_expr)

    polynomial = sp.Poly(reduced, x)

    if polynomial.degree() != 1:
        return None

    coefficient = polynomial.coeff_monomial(x)
    constant = polynomial.coeff_monomial(1)

    if coefficient == 0:
        return None

    value = simplify(-constant / coefficient)

    return make_result(
        "Linear equation",
        [
            f"Step 1: Given equation: {left} = {right}",
            f"Step 2: Expand and collect terms: {coefficient}*x + ({constant}) = 0",
            f"Step 3: Move the constant: {coefficient}*x = {-constant}",
            f"Step 4: Divide both sides by {coefficient}.",
            f"Step 5: Simplify: x = {value}",
            f"Step 6: Check: left side = {left_expr.subs(x, value)}",
            f"Check: right side = {right_expr.subs(x, value)}"
        ],
        f"x = {value}"
    )


def solve_quadratic_equation(left, right):
    left_expr = expand(parse_expression(left))
    right_expr = expand(parse_expression(right))
    polynomial = sp.Poly(expand(left_expr - right_expr), x)

    if polynomial.degree() != 2:
        return None

    a = polynomial.coeff_monomial(x**2)
    b = polynomial.coeff_monomial(x)
    c = polynomial.coeff_monomial(1)

    discriminant = simplify(b**2 - 4*a*c)
    solutions = solve(Eq(a*x**2 + b*x + c, 0), x)

    return make_result(
        "Quadratic equation",
        [
            f"Step 1: Given equation: {left} = {right}",
            f"Step 2: Write in standard form: {a}x² + {b}x + {c} = 0",
            f"Step 3: Identify a = {a}, b = {b}, c = {c}.",
            f"Step 4: Calculate discriminant: D = b² - 4ac = {discriminant}",
            "Step 5: Use the quadratic formula.",
            f"Step 6: Calculate the roots: {solutions}",
            "Step 7: Substitute the roots into the original equation to check."
        ],
        f"x = {solutions}"
    )


def solve_equation(question):
    text = re.sub(
        r"^(solve|find|calculate)\s+",
        "",
        question.strip(),
        flags=re.IGNORECASE
    )

    if "=" not in text:
        return None

    left, right = text.split("=", 1)

    try:
        left_expr = parse_expression(left)
        right_expr = parse_expression(right)
        degree = sp.Poly(expand(left_expr - right_expr), x).degree()

        if degree == 1:
            return solve_linear_equation(left, right)

        if degree == 2:
            return solve_quadratic_equation(left, right)

        return None
    except Exception:
        return None


def solve_factorization(question):
    match = re.search(
        r"(?:factor|factorize)\s+(.+)",
        question,
        re.IGNORECASE
    )
    if not match:
        return None

    try:
        expression = parse_expression(match.group(1))
        answer = factor(expression)

        return make_result(
            "Factorization",
            [
                f"Step 1: Given expression: {expression}",
                "Step 2: Identify common factors and algebraic patterns.",
                "Step 3: Factorize the expression.",
                f"Step 4: Final factorization: {answer}",
                "Step 5: Expand the factors to check the result."
            ],
            answer
        )
    except Exception:
        return None


def solve_derivative(question):
    match = re.search(
        r"(?:derivative of|differentiate)\s+(.+)",
        question,
        re.IGNORECASE
    )
    if not match:
        return None

    try:
        function = parse_expression(match.group(1))
        answer = diff(function, x)

        return make_result(
            "Differentiation",
            [
                f"Step 1: Given function: f(x) = {function}",
                "Step 2: Differentiate each term with respect to x.",
                "Step 3: Apply the appropriate differentiation rules.",
                f"Step 4: Simplify the derivative: {answer}",
                "Step 5: The derivative is the rate of change of the function."
            ],
            answer
        )
    except Exception:
        return None


def solve_integral(question):
    match = re.search(
        r"(?:integrate|integral of)\s+(.+)",
        question,
        re.IGNORECASE
    )
    if not match:
        return None

    try:
        function = parse_expression(match.group(1))
        answer = integrate(function, x)

        return make_result(
            "Integration",
            [
                f"Step 1: Given function: {function}",
                "Step 2: Integrate with respect to x.",
                "Step 3: Apply the appropriate integration rules.",
                f"Step 4: Find the antiderivative: {answer}",
                "Step 5: Add the constant of integration C."
            ],
            f"{answer} + C"
        )
    except Exception:
        return None


def solve_matrix(question):
    match = re.search(
        r"matrix\s*(\[\[.*\]\])",
        question,
        re.IGNORECASE
    )
    if not match:
        return None

    try:
        matrix = Matrix(sp.sympify(match.group(1)))

        if matrix.rows != matrix.cols:
            return {
                "status": "error",
                "message": "A determinant requires a square matrix."
            }

        determinant = matrix.det()

        return make_result(
            "Matrix determinant",
            [
                f"Step 1: Given matrix:\n{matrix}",
                f"Step 2: Matrix has {matrix.rows} rows and {matrix.cols} columns.",
                "Step 3: Calculate the determinant.",
                f"Step 4: Determinant = {determinant}"
            ],
            determinant
        )
    except Exception:
        return None


def solve_statistics(question):
    match = re.search(
        r"(?:mean|average|median|mode)\s+(?:of\s+)?([0-9,\s.-]+)",
        question,
        re.IGNORECASE
    )
    if not match:
        return None

    try:
        values = [
            float(v.strip())
            for v in match.group(1).split(",")
            if v.strip()
        ]

        if not values:
            return None

        ordered = sorted(values)
        mean_value = sum(values) / len(values)
        middle = len(ordered) // 2

        median_value = (
            ordered[middle]
            if len(ordered) % 2
            else (ordered[middle - 1] + ordered[middle]) / 2
        )

        modes = sp.stats.mode(values)

        return make_result(
            "Statistics",
            [
                f"Step 1: Data values: {values}",
                f"Step 2: Arrange values: {ordered}",
                f"Step 3: Mean = sum / count = {mean_value}",
                f"Step 4: Median = {median_value}",
                f"Step 5: Mode = {modes}"
            ],
            {
                "mean": mean_value,
                "median": median_value,
                "mode": modes
            }
        )
    except Exception:
        return None


def solve_probability(question):
    match = re.search(
        r"probability\s+.*?(\d+)\s*.*?(\d+)",
        question,
        re.IGNORECASE
    )
    if not match:
        return None

    try:
        favorable = int(match.group(1))
        total = int(match.group(2))

        if total <= 0 or favorable < 0 or favorable > total:
            return None

        answer = Rational(favorable, total)

        return make_result(
            "Probability",
            [
                f"Step 1: Favorable outcomes = {favorable}",
                f"Step 2: Total possible outcomes = {total}",
                "Step 3: Use P(E) = favorable outcomes / total outcomes.",
                f"Step 4: P(E) = {favorable}/{total}",
                f"Step 5: Simplify: {answer}"
            ],
            answer
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
        solve_matrix,
        solve_statistics,
        solve_probability
    ]

    for solver in solvers:
        try:
            answer = solver(question)
            if answer:
                return answer
        except Exception:
            continue

    return {
        "status": "needs_ai",
        "subject": "Mathematics",
        "message": (
            "This question needs a more advanced mathematical "
            "interpretation. Please provide the complete question."
        )
    }

