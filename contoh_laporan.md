# Laporan OptiLab

**Jenis model:** Maksimisasi

## Fungsi tujuan

`Z = 40x_{1} + 30x_{2}`

## Kendala

1. `2x_{1} + x_{2} \leq 100`
2. `x_{1} + 2x_{2} \leq 80`

## Hasil

Nilai objektif optimal: **2200**

| Variabel | Nilai optimal |
|---|---:|
| x1 | 40 |
| x2 | 20 |

### Analisis kendala

| Kendala | LHS | Relasi | RHS | Slack/Surplus | Status |
|---:|---:|:---:|---:|---:|---|
| 1 | 100 | ≤ | 100 | 0 | Aktif |
| 2 | 80 | ≤ | 80 | 0 | Aktif |

## Metode

Diselesaikan menggunakan SciPy `linprog` dengan metode HiGHS.