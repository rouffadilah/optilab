from optilab.solver import solve_linear_program


def test_maximization_production_example():
    result = solve_linear_program(
        [40, 30],
        [
            {"coefficients": [2, 1], "relation": "≤", "rhs": 100},
            {"coefficients": [1, 2], "relation": "≤", "rhs": 80},
        ],
        maximize=True,
        non_negative=True,
    )
    assert result["success"]
    assert abs(result["objective"] - 2200) < 1e-7
    assert abs(result["variables"][0] - 40) < 1e-7
    assert abs(result["variables"][1] - 20) < 1e-7


def test_minimization_with_greater_equal_constraint():
    result = solve_linear_program(
        [3, 2],
        [
            {"coefficients": [1, 1], "relation": "≥", "rhs": 10},
            {"coefficients": [1, 0], "relation": "≥", "rhs": 2},
            {"coefficients": [0, 1], "relation": "≥", "rhs": 1},
        ],
        maximize=False,
        non_negative=True,
    )
    assert result["success"]
    assert abs(result["objective"] - 22) < 1e-7
    assert abs(result["variables"][0] - 2) < 1e-7
    assert abs(result["variables"][1] - 8) < 1e-7


def test_infeasible_model_is_reported():
    result = solve_linear_program(
        [1, 1],
        [
            {"coefficients": [1, 1], "relation": "≤", "rhs": 1},
            {"coefficients": [1, 1], "relation": "≥", "rhs": 3},
        ],
        maximize=True,
        non_negative=True,
    )
    assert not result["success"]
    assert result["status"] == 2
