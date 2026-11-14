from backend.services.mathematics import solve_mathematics
from backend.services.chemistry import solve_chemistry


def test_arithmetic():
    result = solve_mathematics("2 + 3 * 4")
    assert result["status"] == "success"
    assert result["answer"] == "14"


def test_linear_equation():
    result = solve_mathematics("solve 2*x + 5 = 15")
    assert result["status"] == "success"
    assert "5" in result["answer"]


def test_derivative():
    result = solve_mathematics("derivative of x^3")
    assert result["status"] == "success"
    assert result["answer"] == "3*x**2"


def test_water_molar_mass():
    result = solve_chemistry("molar mass H2O")
    assert result["status"] == "success"
    assert "18." in result["answer"]


def test_water_moles():
    result = solve_chemistry("calculate moles in 18 g H2O")
    assert result["status"] == "success"
    assert "1." in result["answer"]