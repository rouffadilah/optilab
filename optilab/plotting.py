"""Plotly visualization helpers for two-variable LP models."""
from __future__ import annotations

from itertools import combinations
from typing import Any, Sequence

import numpy as np
import plotly.graph_objects as go


def build_2d_figure(
    objective: Sequence[float],
    constraints: Sequence[dict[str, Any]],
    result: dict[str, Any],
    *,
    non_negative: bool = True,
) -> go.Figure | None:
    if len(objective) != 2:
        return None
    if not non_negative:
        return None

    x_opt = result.get("variables", [0.0, 0.0])[0] if result.get("success") else 0.0
    y_opt = result.get("variables", [0.0, 0.0])[1] if result.get("success") else 0.0
    x_max, y_max = 10.0, 10.0
    for row in constraints:
        a, b = row["coefficients"]
        rhs = float(row["rhs"])
        if a > 1e-12 and rhs > 0:
            x_max = max(x_max, rhs / a * 1.15)
        if b > 1e-12 and rhs > 0:
            y_max = max(y_max, rhs / b * 1.15)
    x_max = max(x_max, float(x_opt) * 1.2 + 1)
    y_max = max(y_max, float(y_opt) * 1.2 + 1)
    # Keep the graph usable if a model contains unusually large values.
    x_max = min(x_max, 1e6)
    y_max = min(y_max, 1e6)

    # Convert each constraint boundary and the viewport edges into lines.
    boundary_lines: list[tuple[float, float, float]] = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 0.0, x_max), (0.0, 1.0, y_max)]
    for row in constraints:
        a, b = map(float, row["coefficients"])
        rhs = float(row["rhs"])
        if abs(a) + abs(b) > 1e-12:
            boundary_lines.append((a, b, rhs))

    vertices: list[tuple[float, float]] = []
    for first, second in combinations(boundary_lines, 2):
        matrix = np.array([[first[0], first[1]], [second[0], second[1]]], dtype=float)
        if abs(float(np.linalg.det(matrix))) < 1e-10:
            continue
        point = np.linalg.solve(matrix, np.array([first[2], second[2]], dtype=float))
        x, y = float(point[0]), float(point[1])
        if x < -1e-7 or y < -1e-7 or x > x_max + 1e-7 or y > y_max + 1e-7:
            continue
        feasible = True
        for row in constraints:
            lhs = float(np.dot(np.asarray(row["coefficients"], dtype=float), np.array([x, y])))
            rhs = float(row["rhs"])
            relation = row["relation"]
            if relation == "≤" and lhs > rhs + 1e-7:
                feasible = False
            elif relation == "≥" and lhs < rhs - 1e-7:
                feasible = False
            elif relation == "=" and abs(lhs - rhs) > 1e-7:
                feasible = False
            if not feasible:
                break
        if feasible and not any(np.linalg.norm(np.array(point) - np.array(old)) < 1e-6 for old in vertices):
            vertices.append((x, y))

    fig = go.Figure()
    if len(vertices) >= 3:
        center = np.mean(np.asarray(vertices), axis=0)
        ordered = sorted(vertices, key=lambda p: np.arctan2(p[1] - center[1], p[0] - center[0]))
        ordered.append(ordered[0])
        fig.add_trace(go.Scatter(
            x=[p[0] for p in ordered], y=[p[1] for p in ordered],
            mode="lines", fill="toself", name="Daerah layak",
            line={"width": 1.5}, opacity=0.25,
            hovertemplate="x₁=%{x:.3g}<br>x₂=%{y:.3g}<extra>Daerah layak</extra>",
        ))

    xs = np.linspace(0, x_max, 200)
    for idx, row in enumerate(constraints, start=1):
        a, b = map(float, row["coefficients"])
        rhs = float(row["rhs"])
        if abs(b) > 1e-12:
            ys = (rhs - a * xs) / b
            keep = (ys >= -0.05 * y_max) & (ys <= 1.05 * y_max)
            if np.any(keep):
                fig.add_trace(go.Scatter(x=xs[keep], y=ys[keep], mode="lines", name=f"Kendala {idx} ({row['relation']})", hovertemplate="x₁=%{x:.3g}<br>x₂=%{y:.3g}<extra>%{fullData.name}</extra>"))
        elif abs(a) > 1e-12:
            vertical_x = rhs / a
            if -0.01 * x_max <= vertical_x <= 1.01 * x_max:
                fig.add_trace(go.Scatter(x=[vertical_x, vertical_x], y=[0, y_max], mode="lines", name=f"Kendala {idx} ({row['relation']})"))

    if result.get("success"):
        fig.add_trace(go.Scatter(
            x=[x_opt], y=[y_opt], mode="markers+text", name="Solusi optimal",
            marker={"size": 13, "symbol": "star"}, text=["Optimal"], textposition="top right",
            hovertemplate="x₁=%{x:.5g}<br>x₂=%{y:.5g}<extra>Solusi optimal</extra>",
        ))

    fig.update_layout(
        title="Visualisasi Daerah Layak dan Solusi Optimal",
        xaxis_title="Variabel keputusan x₁", yaxis_title="Variabel keputusan x₂",
        template="plotly_white", height=480, legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0},
        margin={"l": 20, "r": 20, "t": 95, "b": 20},
    )
    fig.update_xaxes(range=[0, x_max], zeroline=True)
    fig.update_yaxes(range=[0, y_max], zeroline=True, scaleanchor="x", scaleratio=1)
    return fig
