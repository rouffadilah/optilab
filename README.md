# OptiLab

**OptiLab** adalah dashboard berbasis Python untuk mata kuliah **Modelling and Optimization**. MVP ini menyelesaikan masalah Linear Programming, menampilkan formulasi matematis, menganalisis slack kendala, memvisualisasikan model dua variabel, dan mengekspor laporan LaTeX.

## Fitur

- Maksimisasi dan minimisasi fungsi tujuan linear.
- 2–6 variabel keputusan dan 1–8 kendala.
- Kendala `≤`, `≥`, dan `=`.
- Batas variabel non-negatif atau bebas tanda.
- Solver `scipy.optimize.linprog` dengan metode HiGHS.
- Tabel nilai variabel, nilai objektif, slack/surplus, dan kendala aktif.
- Grafik daerah layak untuk model dua variabel non-negatif.
- Ekspor laporan LaTeX (`.tex`), Markdown (`.md`), dan hasil variabel (`.csv`).
- Cache hasil model yang identik untuk mengurangi perhitungan berulang.

## Deployment ke Streamlit Community Cloud

Repositori ini disiapkan untuk Streamlit Community Cloud dan bisa tetap **private**.

1. Buat repositori GitHub baru bernama `optilab` dan pilih **Private**.
2. Unggah seluruh isi folder proyek ke root repositori. Pastikan `app.py`, `requirements.txt`, folder `optilab/`, dan folder `.streamlit/` berada di root.
3. Buka <https://share.streamlit.io/> dan masuk menggunakan akun GitHub yang memiliki akses admin ke repositori tersebut.
4. Jika repositori private belum muncul, izinkan Streamlit Community Cloud mengakses private repositories melalui **Settings → Linked accounts → Source control**.
5. Klik **Create app** dan pilih repositori `rouffadilah/optilab` (atau sesuaikan jika menggunakan akun lain), branch `main`, dan main file path `app.py`.
6. Pada pengaturan deployment, pilih **Python 3.12**.
7. Deploy aplikasi. Setelah selesai, buka URL yang diberikan Streamlit.

**Catatan privasi:** Streamlit Community Cloud mewarisi akses dari repositori GitHub. Untuk aplikasi yang dibuat dari repositori private, ikuti pengaturan akses private aplikasi di Streamlit. Dokumentasi Streamlit saat ini menyebutkan akun Community Cloud dibatasi satu aplikasi private aktif pada satu waktu; periksa pengaturan akun sebelum deployment jika Anda sudah memiliki aplikasi private lain.

Panduan resmi:
- <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy>
- <https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/connect-your-github-account>
- <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies>

## Struktur proyek

```text
optilab/
├── app.py
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
├── .github/
│   └── workflows/
│       └── tests.yml
├── optilab/
│   ├── __init__.py
│   ├── solver.py
│   ├── plotting.py
│   └── latex_report.py
└── tests/
    └── test_solver.py
```

## Menjalankan lokal

Python 3.12 direkomendasikan. Di terminal pada folder proyek:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m streamlit run app.py
```

macOS/Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m streamlit run app.py
```

Aplikasi akan tersedia di <http://localhost:8501>.

## Contoh model bawaan

Maksimalkan:

\[
\max Z = 40x_1 + 30x_2
\]

Dengan kendala:

\[
\begin{aligned}
2x_1 + x_2 &\leq 100\\
x_1 + 2x_2 &\leq 80\\
x_1,x_2 &\geq 0
\end{aligned}
\]

Solusi optimal adalah `x1 = 40`, `x2 = 20`, dan `Z = 2200`.

## Pengujian

```bash
python -m pytest -q
```

GitHub Actions juga menjalankan pengujian solver ketika ada push atau pull request ke branch `main`.

## Catatan akademik

MVP ini memakai solver HiGHS untuk mendapatkan solusi Linear Programming. Ia belum menampilkan tabel Simpleks untuk setiap iterasi; tabel Simpleks pedagogis, analisis sensitivitas lanjutan, Integer Programming, optimasi multiobjektif, dan metaheuristik merupakan tahap pengembangan berikutnya.
