from __future__ import annotations

from io import StringIO
from typing import Any

import pandas as pd
import streamlit as st

from optilab.latex_report import generate_latex_report, generate_markdown_report, model_latex
from optilab.plotting import build_2d_figure
from optilab.solver import solve_linear_program


st.set_page_config(
    page_title="OptiLab | Modelling & Optimization",
    page_icon="∑",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.4rem; padding-bottom: 2.5rem; max-width: 1500px;}
      .hero {padding: 1.2rem 1.35rem; border-radius: 18px; background: linear-gradient(120deg,#10243d,#23527a); color: white; margin-bottom: 1rem;}
      .hero h1 {margin: 0; font-size: 2.05rem; letter-spacing: -0.03em;}
      .hero p {margin: .35rem 0 0 0; color: #d8e6f4;}
      .small-muted {color: #667085; font-size: .9rem;}
      div[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.20); padding: .8rem; border-radius: 12px;}
    </style>
    """,
    unsafe_allow_html=True,
)


def _get_default_objective(index: int) -> float:
    return [40.0, 30.0][index] if index < 2 else 0.0


def _get_default_constraint(row: int, col: int) -> float:
    defaults = [[2.0, 1.0], [1.0, 2.0]]
    if row < len(defaults) and col < len(defaults[row]):
        return defaults[row][col]
    return 0.0


@st.cache_data(show_spinner=False, max_entries=128)
def _cached_solve(
    objective: tuple[float, ...],
    coefficients: tuple[tuple[float, ...], ...],
    relations: tuple[str, ...],
    rhs_values: tuple[float, ...],
    maximize: bool,
    non_negative: bool,
) -> dict[str, Any]:
    constraints = [
        {"coefficients": list(coefficients[i]), "relation": relations[i], "rhs": rhs_values[i]}
        for i in range(len(relations))
    ]
    return solve_linear_program(objective, constraints, maximize=maximize, non_negative=non_negative)


with st.sidebar:
    st.markdown("## ∑ OptiLab")
    st.caption("Mathematical Modelling & Optimization")
    st.divider()
    direction_label = st.radio("Jenis optimasi", ["Maksimisasi", "Minimisasi"], horizontal=True)
    n_variables = st.slider("Jumlah variabel", min_value=2, max_value=6, value=2)
    n_constraints = st.slider("Jumlah kendala", min_value=1, max_value=8, value=2)
    non_negative = st.checkbox("Semua variabel non-negatif", value=True, help="Jika dicentang, setiap variabel dibatasi xᵢ ≥ 0. Jika tidak, variabel bebas tanda.")
    st.divider()
    st.markdown("**Solver aktif**")
    st.code("SciPy linprog · HiGHS", language=None)
    st.markdown("**Runtime**")
    st.caption("Solusi dihitung ketika tombol ditekan. Parameter identik menggunakan cache.")
    st.markdown("**Developer**")
    st.caption("Rouf Fadilah  ·  Arief Soyfan Indrawan  ·  Kurniawan")

maximize = direction_label == "Maksimisasi"

st.markdown(
    """
    <div class="hero">
      <h1>OptiLab</h1>
      <p>Interactive mathematical modelling, fast optimization, and LaTeX-ready reports.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

intro_a, intro_b, intro_c = st.columns([1.2, 1, 1])
with intro_a:
    st.markdown("### Model Builder")
    st.caption("Masukkan fungsi tujuan dan kendala dalam bentuk koefisien.")
with intro_b:
    st.markdown("### Solver & Analysis")
    st.caption("Solver HiGHS mencari solusi LP kontinu.")
with intro_c:
    st.markdown("### LaTeX Export")
    st.caption("Ekspor model dan hasil dalam berkas .tex.")

with st.form("lp_model_form", clear_on_submit=False, border=True):
    st.markdown("#### 1. Fungsi tujuan")
    objective_columns = st.columns(n_variables)
    objective_values: list[float] = []
    for j, column in enumerate(objective_columns):
        with column:
            value = st.number_input(
                f"Koefisien x{j + 1}",
                value=float(_get_default_objective(j)),
                step=1.0,
                format="%.6g",
                key=f"objective_{j}_{n_variables}",
            )
            objective_values.append(float(value))

    st.markdown("#### 2. Kendala")
    constraint_values: list[list[float]] = []
    relation_values: list[str] = []
    rhs_values: list[float] = []
    for i in range(n_constraints):
        with st.container(border=True):
            st.markdown(f"**Kendala {i + 1}**")
            row_columns = st.columns([1] * n_variables + [0.8, 1])
            coefficients_row: list[float] = []
            for j in range(n_variables):
                with row_columns[j]:
                    coeff = st.number_input(
                        f"Koef. x{j + 1}",
                        value=float(_get_default_constraint(i, j)),
                        step=1.0,
                        format="%.6g",
                        key=f"constraint_{i}_coefficient_{j}_{n_variables}_{n_constraints}",
                    )
                    coefficients_row.append(float(coeff))
            with row_columns[n_variables]:
                relation = st.selectbox(
                    "Relasi",
                    options=["≤", "≥", "="],
                    index=0,
                    key=f"constraint_{i}_relation_{n_variables}_{n_constraints}",
                )
            with row_columns[n_variables + 1]:
                rhs = st.number_input(
                    "Ruas kanan",
                    value=float([100, 80][i] if i < 2 else 0),
                    step=1.0,
                    format="%.6g",
                    key=f"constraint_{i}_rhs_{n_variables}_{n_constraints}",
                )
            constraint_values.append(coefficients_row)
            relation_values.append(relation)
            rhs_values.append(float(rhs))

    submitted = st.form_submit_button("▶ Selesaikan model", type="primary", use_container_width=True)

if submitted:
    try:
        objective_tuple = tuple(objective_values)
        coefficients_tuple = tuple(tuple(row) for row in constraint_values)
        relations_tuple = tuple(relation_values)
        rhs_tuple = tuple(rhs_values)
        result = _cached_solve(
            objective_tuple,
            coefficients_tuple,
            relations_tuple,
            rhs_tuple,
            maximize,
            non_negative,
        )
        model_data = {
            "objective": list(objective_tuple),
            "constraints": [
                {"coefficients": list(coefficients_tuple[i]), "relation": relations_tuple[i], "rhs": rhs_tuple[i]}
                for i in range(len(relations_tuple))
            ],
            "maximize": maximize,
            "non_negative": non_negative,
            "result": result,
        }
        st.session_state["optilab_app_last_model"] = model_data
    except (ValueError, TypeError, ArithmeticError) as exc:
        st.error(f"Model tidak dapat diproses: {exc}")

model_data = st.session_state.get("optilab_app_last_model")
if model_data:
    model_objective = model_data["objective"]
    model_constraints = model_data["constraints"]
    model_maximize = model_data["maximize"]
    model_non_negative = model_data["non_negative"]
    result = model_data["result"]

    st.divider()
    st.markdown("## Hasil Pemodelan")
    st.markdown("#### Formulasi matematis (LaTeX)")
    st.latex(model_latex(model_objective, model_constraints, model_maximize, model_non_negative))

    if result.get("success"):
        metric_cols = st.columns([1, 1, 1, 1])
        metric_cols[0].metric("Nilai objektif optimal", f"{result['objective']:,.6g}")
        metric_cols[1].metric("Jumlah variabel", str(len(result["variables"])))
        metric_cols[2].metric("Kendala aktif", f"{sum(row['binding'] for row in result['constraint_analysis'])}/{len(model_constraints)}")
        iteration_value = result.get("iterations")
        metric_cols[3].metric("Iterasi solver", str(iteration_value) if iteration_value is not None else "—")
        st.success("Solusi optimal berhasil ditemukan.")

        left, right = st.columns([1, 1.15], gap="large")
        with left:
            st.markdown("#### Nilai variabel keputusan")
            variable_df = pd.DataFrame({
                "Variabel": [f"x{i}" for i in range(1, len(result["variables"]) + 1)],
                "Nilai optimal": result["variables"],
            })
            st.dataframe(variable_df, hide_index=True, use_container_width=True)
            st.markdown("#### Analisis kendala")
            constraint_df = pd.DataFrame([
                {
                    "Kendala": f"K{i}",
                    "LHS": row["lhs"],
                    "Relasi": row["relation"],
                    "RHS": row["rhs"],
                    "Slack/Surplus": row["slack"],
                    "Status": "Aktif" if row["binding"] else ("Terpenuhi" if row["satisfied"] else "Tidak terpenuhi"),
                }
                for i, row in enumerate(result["constraint_analysis"], start=1)
            ])
            st.dataframe(constraint_df, hide_index=True, use_container_width=True)
        with right:
            st.markdown("#### Visualisasi")
            if len(model_objective) == 2 and model_non_negative:
                fig = build_2d_figure(model_objective, model_constraints, result, non_negative=model_non_negative)
                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True)
            elif len(model_objective) == 2:
                st.info("Grafik daerah layak pada MVP ini tersedia saat semua variabel dibatasi non-negatif.")
            else:
                st.info("Grafik daerah layak 2D hanya tersedia untuk model dengan dua variabel. Tabel hasil tetap tersedia untuk model dengan 2–6 variabel.")
            st.caption(f"Metode: {result['solver']}. Solver message: {result['message']}")
    else:
        if result.get("status") == 2:
            st.error("Model tidak layak (infeasible): tidak ada kombinasi variabel yang memenuhi seluruh kendala.")
        elif result.get("status") == 3:
            st.error("Model tidak terbatas (unbounded): nilai fungsi tujuan dapat terus membaik tanpa batas.")
        else:
            st.warning("Solver belum menemukan solusi optimal.")
        st.caption(result.get("message", "Tidak ada pesan solver."))

    st.divider()
    st.markdown("## Ekspor")
    report_tex = generate_latex_report(
        model_objective,
        model_constraints,
        result,
        maximize=model_maximize,
        non_negative=model_non_negative,
        title="Laporan OptiLab",
    )
    report_md = generate_markdown_report(model_objective, model_constraints, result, model_maximize)
    export_left, export_middle, export_right = st.columns(3)
    with export_left:
        st.download_button(
            "Unduh laporan LaTeX (.tex)",
            data=report_tex,
            file_name="laporan_optilab_app.tex",
            mime="application/x-tex",
            use_container_width=True,
        )
    with export_middle:
        st.download_button(
            "Unduh laporan Markdown (.md)",
            data=report_md,
            file_name="laporan_optilab_app.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with export_right:
        csv_buffer = StringIO()
        if result.get("success"):
            variable_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
        else:
            csv_data = "Variabel,Nilai optimal\n"
        st.download_button(
            "Unduh hasil variabel (.csv)",
            data=csv_data,
            file_name="hasil_variabel_optilab_app.csv",
            mime="text/csv",
            use_container_width=True,
        )
else:
    st.info("Isi model di atas lalu klik **Selesaikan model**. Contoh awal sudah berisi model produksi sederhana: maksimalkan Z = 40x₁ + 30x₂ dengan dua kendala.")

with st.expander("Tentang model dan batasan MVP"):
    st.markdown(
        """
        - Mendukung Linear Programming kontinu dengan kendala `≤`, `≥`, dan `=`.
        - Dapat digunakan untuk maksimisasi maupun minimisasi.
        - Pilihan batas variabel pada versi ini berlaku seragam untuk semua variabel: non-negatif atau bebas tanda.
        - Solver menggunakan HiGHS melalui `scipy.optimize.linprog`; tabel iterasi metode Simpleks langkah demi langkah belum termasuk dalam MVP ini.
        - Rumus ditampilkan melalui renderer matematika Streamlit, sedangkan ekspor `.tex` dapat dikompilasi menjadi PDF menggunakan distribusi LaTeX seperti TeX Live atau MiKTeX.
        """
    )

st.caption("OptiLab MVP · Python · Streamlit · SciPy HiGHS · Plotly")
