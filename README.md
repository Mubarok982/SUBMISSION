
# Mubarok Collection Dashboard 

Panduan untuk menyiapkan lingkungan pengembangan dan menjalankan aplikasi dashboard.

## Setup Environment

### Menggunakan Anaconda
1. Buat environment baru dengan Python 3.9:
   ```bash
   conda create --name main-ds python=3.9
   ```
2. Aktivasi environment:
   ```bash
   conda activate main-ds
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Menggunakan Shell/Terminal
1. Pindah ke direktori proyek:
   ```bash
   masuk ke directory yang aktif(DASHBOARD)
   lalu jalankan perintah "streamlit run DASHBOARD/Dashboard.py"
   ```
2. Install dependencies menggunakan Pipenv:
   ```bash
   pipenv install
   pipenv shell
   pip install -r requirements.txt
   ```

## Menjalankan Aplikasi Dashboard
1. Pastikan dependencies sudah terinstall.
2. Jalankan aplikasi Streamlit:
   ```bash
   streamlit run Dashboard.py
   ```

---
