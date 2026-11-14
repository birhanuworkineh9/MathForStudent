import re


def make_result(method, steps, answer):
    return {
        "status": "success",
        "subject": "Computer Science",
        "method": method,
        "steps": steps,
        "answer": str(answer)
    }


def binary_to_decimal(question):
    match = re.search(
        r"(?:binary)\s+([01]+)",
        question.lower()
    )

    if not match:
        return None

    binary = match.group(1)
    decimal = int(binary, 2)

    return make_result(
        "Binary to decimal conversion",
        [
            f"Binary number = {binary}",
            "Multiply each digit by its power of 2.",
            f"Decimal value = {decimal}"
        ],
        decimal
    )


def decimal_to_binary(question):
    match = re.search(
        r"(?:decimal)\s+(\d+).*binary",
        question.lower()
    )

    if not match:
        return None

    decimal = int(match.group(1))
    binary = bin(decimal)[2:]

    return make_result(
        "Decimal to binary conversion",
        [
            f"Decimal number = {decimal}",
            "Repeatedly divide by 2 and record remainders.",
            f"Binary number = {binary}"
        ],
        binary
    )


def sort_numbers(question):
    match = re.search(
        r"sort\s+(?:numbers\s+)?([\d,\s.-]+)",
        question.lower()
    )

    if not match:
        return None

    try:
        numbers = [
            float(item.strip())
            for item in match.group(1).split(",")
            if item.strip()
        ]

        if not numbers:
            return None

        sorted_numbers = sorted(numbers)

        return make_result(
            "Sorting",
            [
                f"Input numbers: {numbers}",
                "Arrange the numbers in ascending order.",
                f"Sorted numbers: {sorted_numbers}"
            ],
            sorted_numbers
        )

    except ValueError:
        return None


def calculate_average(question):
    match = re.search(
        r"average\s+(?:of\s+)?([\d,\s.-]+)",
        question.lower()
    )

    if not match:
        return None

    try:
        numbers = [
            float(item.strip())
            for item in match.group(1).split(",")
            if item.strip()
        ]

        if not numbers:
            return None

        average = sum(numbers) / len(numbers)

        return make_result(
            "Arithmetic mean",
            [
                f"Numbers = {numbers}",
                "Add all numbers.",
                f"Sum = {sum(numbers)}",
                "Divide the sum by the number of values.",
                f"Average = {average}"
            ],
            round(average, 4)
        )

    except ValueError:
        return None


def solve_computer_science(question):
    if not question or not question.strip():
        return {
            "status": "error",
            "message": "Please enter a computer science question."
        }

    solvers = [
        binary_to_decimal,
        decimal_to_binary,
        sort_numbers,
        calculate_average
    ]

    for solver in solvers:
        result = solver(question)
        if result:
            return result

    return {
        "status": "needs_ai",
        "subject": "Computer Science",
        "message": (
            "This question needs further computer science "
            "interpretation."
        )
    }