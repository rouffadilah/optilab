"""LaTeX and Markdown report exporters."""
from __future__ import annotations

from typing import Any, Sequence


def _number(value: float) -> str:
    value = float(value)
    if abs(value - round(value)) < 1e-10:
        return str(int(round(value)))
    return f"{value:.6g}"


def objective_latex(coefficients: Sequence[float]) -> str:
    terms: list[str] = []
    for idx, value in enumerate(coefficients, start=1):
        value = float(value)
        if abs(value) < 1e-12:
            continue
        magnitude = abs(value)
        coef = "" if abs(magnitude - 1) < 1e-12 else _number(magnitude)
        term = rf"{coef}x_{{{idx}}}"
        if not terms:
            terms.append(("-" if value < 0 else "") + term)
        else:
            terms.append((" - " if value < 0 else " + ") + term)
    return "".join(terms) if terms else "0"


def constraint_latex(coefficients: Sequence[float], relation: str, rhs: float) -> str:
    terms: list[str] = []
    for idx, value in enumerate(coefficients, start=1):
        value = float(value)
        if abs(value) < 1e-12:
            continue
        magnitude = abs(value)
        coef = "" if abs(magnitude - 1) < 1e-12 else _number(magnitude)
        term = rf"{coef}x_{{{idx}}}"
        if not terms:
            terms.append(("-" if value < 0 else "") + term)
        else:
            terms.append((" - " if value < 0 else " + ") + term)
    expression = "".join(terms) if terms else "0"
    latex_relation = {"≤": r"\leq", "≥": r"\geq", "=": "="}[relation]
    return f"{expression} {latex_relation} {_number(rhs)}"


def _model_lines(
    objective: Sequence[float],
    constraints: Sequence[dict[str, Any]],
    maximize: bool,
    non_negative: bool,
) -> list[str]:
    operator = r"\max" if maximize else r"\min"
    lines = [rf"{operator}\quad Z &= {objective_latex(objective)}", r"\text{dengan kendala:} &"]
    lines.extend(r"&\quad " + constraint_latex(row["coefficients"], row["relation"], row["rhs"]) for row in constraints)
    if non_negative:
        variables = r",\;".join(rf"x_{{{i}}}\geq 0" for i in range(1, len(objective) + 1))
        lines.append(r"&\quad " + variables)
    return lines


def _aligned(lines: Sequence[str]) -> str:
    # One line break plus a real newline keeps generated TeX readable.
    separator = r" \\" + "\n"
    return r"\begin{aligned}" + "\n" + separator.join(lines) + "\n" + r"\end{aligned}"


def model_latex(
    objective: Sequence[float],
    constraints: Sequence[dict[str, Any]],
    maximize: bool,
    non_negative: bool,
) -> str:
    return _aligned(_model_lines(objective, constraints, maximize, non_negative))


def generate_latex_report(
    objective: Sequence[float],
    constraints: Sequence[dict[str, Any]],
    result: dict[str, Any],
    *,
    maximize: bool,
    non_negative: bool,
    title: str = "Laporan Pemodelan dan Optimasi",
) -> str:
    if result.get("success"):
        variable_rows = [rf"x_{{{i}}} &= {_number(value)}" for i, value in enumerate(result["variables"], start=1)]
        solution_section = (
            r"\section*{Hasil Penyelesaian}" + "\n"
            + rf"Nilai objektif optimal: $Z^* = {_number(result['objective'])}$." + "\n\n"
            + r"\[" + _aligned(variable_rows) + r"\]" + "\n"
            + r"\subsection*{Analisis Kendala}" + "\n"
            + r"\begin{center}" + "\n"
            + r"\begin{tabular}{rrrrl}" + "\n"
            + r"\toprule Kendala & LHS & RHS & Slack/Surplus & Status \\" + "\n"
            + r"\midrule" + "\n"
        )
        for row in result.get("constraint_analysis", []):
            status = "Aktif" if row["binding"] else ("Terpenuhi" if row["satisfied"] else "Tidak terpenuhi")
            solution_section += (
                f"{row['constraint']} & {_number(row['lhs'])} & {_number(row['rhs'])} & "
                f"{_number(row['slack'])} & {status} " + r"\\" + "\n"
            )
        solution_section += r"\bottomrule" + "\n" + r"\end{tabular}" + "\n" + r"\end{center}" + "\n"
        iters = result.get("iterations")
        if iters is not None:
            solution_section += rf"\noindent Iterasi solver yang dilaporkan: {iters}." + "\n"
    else:
        safe_message = str(result.get("message", "Tidak tersedia")).replace("_", r"\_").replace("%", r"\%")
        solution_section = (
            r"\section*{Status Penyelesaian}" + "\n"
            + r"Solver tidak menemukan solusi optimal yang dapat dilaporkan." + "\n\n"
            + r"\noindent Pesan solver: \texttt{" + safe_message + "}." + "\n"
        )

    safe_title = title.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
    return (
        r"\documentclass[11pt,a4paper]{article}" + "\n"
        + r"\usepackage[margin=2.5cm]{geometry}" + "\n"
        + r"\usepackage{amsmath,amssymb,booktabs}" + "\n"
        + r"\usepackage[T1]{fontenc}" + "\n"
        + r"\usepackage[utf8]{inputenc}" + "\n"
        + r"\title{" + safe_title + "}" + "\n"
        + r"\date{\today}" + "\n"
        + r"\begin{document}" + "\n"
        + r"\maketitle" + "\n"
        + r"\section*{Formulasi Matematis}" + "\n"
        + r"\[" + _aligned(_model_lines(objective, constraints, maximize, non_negative)) + r"\]" + "\n"
        + solution_section
        + r"\section*{Metode}" + "\n"
        + r"Model diselesaikan sebagai Linear Programming kontinu menggunakan SciPy \texttt{linprog} dengan metode HiGHS. Hasil berlaku untuk koefisien dan asumsi yang dimasukkan." + "\n"
        + r"\end{document}" + "\n"
    )


def generate_markdown_report(
    objective: Sequence[float],
    constraints: Sequence[dict[str, Any]],
    result: dict[str, Any],
    maximize: bool,
) -> str:
    direction = "Maksimisasi" if maximize else "Minimisasi"
    lines = [
        "# Laporan OptiLab", "", f"**Jenis model:** {direction}", "",
        "## Fungsi tujuan", "", f"`Z = {objective_latex(objective)}`", "", "## Kendala", "",
    ]
    for i, row in enumerate(constraints, start=1):
        lines.append(f"{i}. `{constraint_latex(row['coefficients'], row['relation'], row['rhs'])}`")
    lines.extend(["", "## Hasil", ""])
    if result.get("success"):
        lines.append(f"Nilai objektif optimal: **{_number(result['objective'])}**")
        lines.extend(["", "| Variabel | Nilai optimal |", "|---|---:|"])
        for i, value in enumerate(result["variables"], start=1):
            lines.append(f"| x{i} | {_number(value)} |")
        lines.extend([
            "", "### Analisis kendala", "",
            "| Kendala | LHS | Relasi | RHS | Slack/Surplus | Status |",
            "|---:|---:|:---:|---:|---:|---|",
        ])
        for row in result.get("constraint_analysis", []):
            status = "Aktif" if row["binding"] else ("Terpenuhi" if row["satisfied"] else "Tidak terpenuhi")
            lines.append(
                f"| {row['constraint']} | {_number(row['lhs'])} | {row['relation']} | "
                f"{_number(row['rhs'])} | {_number(row['slack'])} | {status} |"
            )
    else:
        lines.extend(["Solver belum menghasilkan solusi optimal.", "", f"Pesan solver: {result.get('message', 'Tidak tersedia')}"])
    lines.extend(["", "## Metode", "", "Diselesaikan menggunakan SciPy `linprog` dengan metode HiGHS."])
    return "\n".join(lines)
