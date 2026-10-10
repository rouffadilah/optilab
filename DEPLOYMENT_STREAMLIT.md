# Deployment OptiLab (private GitHub repository)

## A. Siapkan GitHub

1. Masuk ke akun GitHub Anda.
2. Klik **New repository**.
3. Isi nama `optilab`, pilih **Private**, dan biarkan opsi README / .gitignore / license tidak dicentang karena file proyek sudah tersedia.
4. Klik **Create repository**.
5. Dari folder proyek di komputer, jalankan:

```bash
git init
git add .
git commit -m "Prepare OptiLab for Streamlit Community Cloud"
git branch -M main
git remote add origin https://github.com/rouffadilah/optilab.git
git push -u origin main
```

Jika nama akun berbeda, ganti `rouffadilah` pada alamat remote. Jika folder sudah menjadi Git repository, jangan jalankan `git init` lagi; cukup atur remote dan commit perubahan.

## B. Deploy ke Streamlit Community Cloud

1. Buka https://share.streamlit.io/ dan masuk dengan GitHub.
2. Berikan izin akses ke private repositories jika diminta. Anda perlu hak admin pada repo.
3. Pilih **Create app** lalu repo `rouffadilah/optilab`, branch `main`, file `app.py`.
4. Di Advanced settings / Python version pilih **3.12**.
5. Deploy dan tunggu proses build selesai.

Streamlit Community Cloud menggunakan `requirements.txt` untuk memasang dependensi. Jangan unggah virtual environment `.venv/`, token, password, atau file rahasia.

## C. Jika repo private tidak muncul

Buka pengaturan Streamlit Community Cloud → **Linked accounts** → **Source control**, lalu sambungkan ulang/otorisasi GitHub dengan akses private repositories. Pastikan akun GitHub yang terhubung mempunyai akses admin ke repo.

## D. Pembaruan setelah deployment

Setelah aplikasi aktif, commit dan push perubahan ke branch `main`. Streamlit Community Cloud akan mendeteksi perubahan dan memperbarui aplikasi.
