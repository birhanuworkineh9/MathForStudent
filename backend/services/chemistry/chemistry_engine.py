import re
from collections import Counter

ATOMIC_MASSES = {
    "H": 1.008,
    "He": 4.0026,
    "Li": 6.94,
    "Be": 9.0122,
    "B": 10.81,
    "C": 12.011,
    "N": 14.007,
    "O": 15.999,
    "F": 18.998,
    "Ne": 20.180,
    "Na": 22.990,
    "Mg": 24.305,
    "Al": 26.982,
    "Si": 28.085,
    "P": 30.974,
    "S": 32.06,
    "Cl": 35.45,
    "K": 39.098,
    "Ca": 40.078,
    "Fe": 55.845,
    "Cu": 63.546,
    "Zn": 65.38,
    "Ag": 107.868,
    "I": 126.904,
    "Ba": 137.327,
    "Pb": 207.2
}


def chemistry_result(method, steps, answer):
    return {
        "status": "success",
        "subject": "Chemistry",
        "method": method,
        "steps": steps,
        "answer": str(answer)
    }


def parse_formula(formula):
    """
    Count atoms in ordinary chemical formulas.
    Supports parentheses and integer subscripts.
    Example: Ca(OH)2 -> Ca:1, O:2, H:2
    """
    tokens = re.findall(r"[A-Z][a-z]?|\d+|[()]", formula)

    if "".join(tokens) != formula:
        raise ValueError("Invalid chemical formula.")

    stack = [Counter()]
    i = 0

    while i < len(tokens):
        token = tokens[i]

        if token == "(":
            stack.append(Counter())
            i += 1

        elif token == ")":
            if len(stack) == 1:
                raise ValueError("Unmatched parenthesis.")

            group = stack.pop()
            i += 1

            multiplier = 1
            if i < len(tokens) and tokens[i].isdigit():
                multiplier = int(tokens[i])
                i += 1

            for element, count in group.items():
                stack[-1][element] += count * multiplier

        elif token.isdigit():
            raise ValueError("Unexpected number in formula.")

        else:
            element = token

            if element not in ATOMIC_MASSES:
                raise ValueError(
                    f"Atomic mass for {element} is not available."
                )

            i += 1
            count = 1

            if i < len(tokens) and tokens[i].isdigit():
                count = int(tokens[i])
                i += 1

            stack[-1][element] += count

    if len(stack) != 1:
        raise ValueError("Unclosed parenthesis.")

    return stack[0]


def molar_mass(formula):
    atoms = parse_formula(formula)

    total = sum(
        ATOMIC_MASSES[element] * count
        for element, count in atoms.items()
    )

    return total, atoms


def solve_molar_mass(question):
    match = re.search(
        r"(?:molar mass|molecular mass|mass of)\s+([A-Z][A-Za-z0-9()]*)",
        question
    )

    if not match:
        return None

    formula = match.group(1)

    try:
        mass, atoms = molar_mass(formula)

        steps = [
            f"Chemical formula: {formula}",
            f"Number of atoms: {dict(atoms)}",
            "Multiply each element's atomic mass by its atom count.",
            f"Add the contributions to get {mass:.3f} g/mol."
        ]

        return chemistry_result(
            "Molar mass calculation",
            steps,
            f"{mass:.3f} g/mol"
        )

    except ValueError as error:
        return {
            "status": "error",
            "message": str(error)
        }


def solve_stoichiometry(question):
    """
    Convert a supplied mass into moles when a formula is provided.
    Example:
    calculate moles in 18 g H2O
    """
    match = re.search(
        r"(?:moles?|amount of substance).*?(\d+(?:\.\d+)?)\s*g\s+([A-Z][A-Za-z0-9()]*)",
        question,
        re.IGNORECASE
    )

    if not match:
        return None

    mass = float(match.group(1))
    formula = match.group(2)

    try:
        molar, _ = molar_mass(formula)

        if molar <= 0:
            raise ValueError("Invalid molar mass.")

        moles = mass / molar

        return chemistry_result(
            "Mass-to-moles stoichiometry",
            [
                f"Given mass = {mass} g",
                f"Formula = {formula}",
                f"Molar mass = {molar:.3f} g/mol",
                "Use n = m / M.",
                f"n = {mass} / {molar:.3f} = {moles:.4f} mol"
            ],
            f"{moles:.4f} mol"
        )

    except ValueError as error:
        return {
            "status": "error",
            "message": str(error)
        }


def solve_chemistry(question):
    if not question or not question.strip():
        return {
            "status": "error",
            "message": "Please enter a chemistry question."
        }

    solvers = [
        solve_molar_mass,
        solve_stoichiometry
    ]

    for solver in solvers:
        answer = solver(question)

        if answer:
            return answer

    return {
        "status": "needs_ai",
        "subject": "Chemistry",
        "message": (
            "This chemistry question needs further interpretation. "
            "Please provide the complete chemical equation, values, "
            "and conditions where relevant."
        )
    }
from functools import reduce
from math import gcd
from sympy import Matrix, lcm


def balance_equation(equation):
    """
    Balance ordinary chemical equations.
    Example: H2 + O2 -> H2O
    """
    equation = equation.replace("→", "->").replace("=", "->")

    if equation.count("->") != 1:
        raise ValueError("Use one reaction arrow, for example H2 + O2 -> H2O.")

    left_text, right_text = equation.split("->")

    reactants = [x.strip() for x in left_text.split("+")]
    products = [x.strip() for x in right_text.split("+")]

    if not reactants or not products or any(not x for x in reactants + products):
        raise ValueError("The chemical equation is incomplete.")

    if len(reactants) + len(products) > 12:
        raise ValueError("This equation is too large for this balancing engine.")

    formulas = reactants + products
    compositions = [parse_formula(formula) for formula in formulas]

    elements = sorted({
        element
        for composition in compositions
        for element in composition
    })

    # Reactants are positive; products are negative.
    rows = []

    for element in elements:
        row = []

        for index, composition in enumerate(compositions):
            count = composition.get(element, 0)

            if index >= len(reactants):
                count = -count

            row.append(count)

        rows.append(row)

    matrix = Matrix(rows)
    basis = matrix.nullspace()

    if not basis:
        raise ValueError("No balancing solution was found.")

    # A one-dimensional nullspace gives a unique basic ratio.
    if len(basis) != 1:
        raise ValueError(
            "This equation has multiple possible balancing solutions."
        )

    vector = basis[0]
    common_denominator = 1

    for value in vector:
        common_denominator = lcm(
            common_denominator,
            value.q
        )

    coefficients = [
        int(value * common_denominator)
        for value in vector
    ]

    common_factor = reduce(gcd, coefficients)

    coefficients = [
        value // common_factor
        for value in coefficients
    ]

    if any(value <= 0 for value in coefficients):
        raise ValueError("A positive balancing solution was not found.")

    balanced_left = " + ".join(
        f"{coefficients[i]}{reactants[i]}"
        for i in range(len(reactants))
    )

    balanced_right = " + ".join(
        f"{coefficients[len(reactants) + i]}{products[i]}"
        for i in range(len(products))
    )

    return f"{balanced_left} -> {balanced_right}"


def solve_balancing(question):
    text = question.strip()

    if "->" not in text and "→" not in text and "=" not in text:
        return None

    try:
        balanced = balance_equation(text)

        return chemistry_result(
            "Chemical equation balancing",
            [
                f"Original equation: {text}",
                "Count each element on both sides.",
                "Find the smallest whole-number coefficient ratio.",
                f"Balanced equation: {balanced}"
            ],
            balanced
        )

    except ValueError as error:
        return {
            "status": "error",
            "message": str(error)
        }