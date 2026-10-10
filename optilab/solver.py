"""Core Linear Programming solver for OptiLab."""
from __future__ import annotations

from typing import Any, Sequence

import numpy as np
from scipy.optimize import linprog


def solve_linear_program(
    objective: Sequence[float],
    constraints: Sequence[dict[str, Any]],
    *,
    maximize: bool = True,
    non_negative: bool = True,
) -> dict[str, Any]:
    """Solve a continuous linear program with <=, >=, and = constraints.

    Parameters are plain Python types so results can be cached/serialized by
    Streamlit. Variable bounds apply uniformly to every decision variable.
    """
    c = np.asarray(objective, dtype=float)
    n_variables = len(c)
    if n_variables == 0:
        raise ValueError("Model harus memiliki minimal satu variabel keputusan.")
    if not np.all(np.isfinite(c)):
        raise ValueError("Semua koefisien fungsi tujuan harus berupa angka yang valid.")

    A_ub: list[list[float]] = []
    b_ub: list[float] = []
    A_eq: list[list[float]] = []
    b_eq: list[float] = []

    for index, item in enumerate(constraints, start=1):
        row = np.asarray(item["coefficients"], dtype=float)
        rhs = float(item["rhs"])
        relation = item["relation"]
        if len(row) != n_variables:
            raise ValueError(f"Kendala {index}: jumlah koefisien tidak sesuai jumlah variabel.")
        if not np.all(np.isfinite(row)) or not np.isfinite(rhs):
            raise ValueError(f"Kendala {index}: semua nilai harus berupa angka yang valid.")
        if relation == "≤":
            A_ub.append(row.tolist())
            b_ub.append(rhs)
        elif relation == "≥":
            A_ub.append((-row).tolist())
            b_ub.append(-rhs)
        elif relation == "=":
            A_eq.append(row.tolist())
            b_eq.append(rhs)
        else:
            raise ValueError(f"Operator kendala tidak dikenal pada baris {index}.")

    solver_c = -c if maximize else c
    bounds = [(0, None) if non_negative else (None, None)] * n_variables
    result = linprog(
        solver_c,
        A_ub=np.asarray(A_ub, dtype=float) if A_ub else None,
        b_ub=np.asarray(b_ub, dtype=float) if b_ub else None,
        A_eq=np.asarray(A_eq, dtype=float) if A_eq else None,
        b_eq=np.asarray(b_eq, dtype=float) if b_eq else None,
        bounds=bounds,
        method="highs",
    )

    payload: dict[str, Any] = {
        "success": bool(result.success),
        "status": int(result.status),
        "message": str(result.message),
        "solver": "SciPy linprog (HiGHS)",
        "maximize": bool(maximize),
        "non_negative": bool(non_negative),
        "objective": None,
        "variables": [],
        "constraint_analysis": [],
        "iterations": getattr(result, "nit", None),
    }
    if not result.success or result.x is None:
        return payload

    x_values = np.asarray(result.x, dtype=float)
    objective_value = float(np.dot(c, x_values))
    payload["objective"] = objective_value
    payload["variables"] = [float(x) for x in x_values]

    for index, item in enumerate(constraints, start=1):
        lhs = float(np.dot(np.asarray(item["coefficients"], dtype=float), x_values))
        rhs = float(item["rhs"])
        relation = item["relation"]
        if relation == "≤":
            slack = rhs - lhs
            slack_label = "Slack"
        elif relation == "≥":
            slack = lhs - rhs
            slack_label = "Surplus"
        else:
            slack = abs(lhs - rhs)
            slack_label = "Deviasi absolut"
        payload["constraint_analysis"].append(
            {
                "constraint": index,
                "lhs": lhs,
                "relation": relation,
                "rhs": rhs,
                "slack": float(slack),
                "slack_label": slack_label,
                "binding": bool(abs(lhs - rhs) <= 1e-7),
                "satisfied": bool(
                    (relation == "≤" and lhs <= rhs + 1e-7)
                    or (relation == "≥" and lhs >= rhs - 1e-7)
                    or (relation == "=" and abs(lhs - rhs) <= 1e-7)
                ),
            }
        )
    return payload
