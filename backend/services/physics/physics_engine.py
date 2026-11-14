import re
import math


def make_result(method, steps, answer, unit=""):
    return {
        "status": "success",
        "subject": "Physics",
        "method": method,
        "steps": steps,
        "answer": f"{answer} {unit}".strip()
    }


def extract_values(question):
    numbers = re.findall(
        r"[-+]?\d*\.?\d+",
        question
    )
    return [float(value) for value in numbers]


def solve_speed(question):
    """
    Speed = distance / time
    Example: calculate speed if distance is 100 m
    and time is 20 s
    """
    text = question.lower()

    if "speed" not in text and "velocity" not in text:
        return None

    values = extract_values(question)

    if len(values) < 2:
        return {
            "status": "needs_information",
            "subject": "Physics",
            "message": "Please provide distance and time."
        }

    distance, time = values[:2]

    if time <= 0 or distance < 0:
        return {
            "status": "error",
            "message": "Distance must be non-negative and time positive."
        }

    speed = distance / time

    return make_result(
        "Speed calculation",
        [
            f"Distance = {distance} m",
            f"Time = {time} s",
            "Formula: speed = distance / time",
            f"speed = {distance} / {time}"
        ],
        round(speed, 4),
        "m/s"
    )


def solve_acceleration(question):
    """
    a = (v-u)/t
    """
    text = question.lower()

    if "acceleration" not in text:
        return None

    values = extract_values(question)

    if len(values) < 3:
        return {
            "status": "needs_information",
            "subject": "Physics",
            "message": (
                "Provide initial velocity, final velocity "
                "and time."
            )
        }

    initial_velocity, final_velocity, time = values[:3]

    if time <= 0:
        return {
            "status": "error",
            "message": "Time must be greater than zero."
        }

    acceleration = (
        final_velocity - initial_velocity
    ) / time

    return make_result(
        "Acceleration calculation",
        [
            f"Initial velocity u = {initial_velocity} m/s",
            f"Final velocity v = {final_velocity} m/s",
            f"Time t = {time} s",
            "Formula: a = (v - u) / t",
            f"a = ({final_velocity} - {initial_velocity}) / {time}"
        ],
        round(acceleration, 4),
        "m/s²"
    )


def solve_force(question):
    """
    Newton's second law: F = m*a
    """
    if "force" not in question.lower():
        return None

    values = extract_values(question)

    if len(values) < 2:
        return {
            "status": "needs_information",
            "subject": "Physics",
            "message": "Provide mass and acceleration."
        }

    mass, acceleration = values[:2]

    if mass < 0:
        return {
            "status": "error",
            "message": "Mass cannot be negative."
        }

    force = mass * acceleration

    return make_result(
        "Newton's second law",
        [
            f"Mass = {mass} kg",
            f"Acceleration = {acceleration} m/s²",
            "Formula: F = m × a",
            f"F = {mass} × {acceleration}"
        ],
        round(force, 4),
        "N"
    )


def solve_weight(question):
    """
    W = m*g
    """
    if "weight" not in question.lower():
        return None

    values = extract_values(question)

    if not values:
        return {
            "status": "needs_information",
            "message": "Provide the mass in kilograms."
        }

    mass = values[0]
    gravity = 9.81

    if mass < 0:
        return {
            "status": "error",
            "message": "Mass cannot be negative."
        }

    weight = mass * gravity

    return make_result(
        "Weight calculation",
        [
            f"Mass = {mass} kg",
            f"Gravitational acceleration = {gravity} m/s²",
            "Formula: W = m × g",
            f"W = {mass} × {gravity}"
        ],
        round(weight, 4),
        "N"
    )


def solve_physics(question):
    if not question or not question.strip():
        return {
            "status": "error",
            "message": "Please enter a physics question."
        }

    solvers = [
        solve_speed,
        solve_acceleration,
        solve_force,
        solve_weight
    ]

    for solver in solvers:
        result = solver(question)
        if result:
            return result

    return {
        "status": "needs_ai",
        "subject": "Physics",
        "message": (
            "This question needs further physics interpretation. "
            "Provide all known values and units."
        )
    }