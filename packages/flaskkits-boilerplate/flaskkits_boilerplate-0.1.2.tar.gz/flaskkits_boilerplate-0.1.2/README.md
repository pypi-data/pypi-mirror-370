# Flaskkit

**Flaskkit** adalah *project generator* untuk Flask yang membantu pengembang memulai proyek dengan cepat. Alat ini menyediakan struktur folder yang terorganisir, integrasi dengan **Tailwind CSS**, dan perintah **CLI** yang sederhana untuk mempermudah alur kerja Anda.

## Instalasi

Sebelum memulai, pastikan Anda telah menginstal **Python 3.8+** dan **pip**. Anda juga memerlukan **Node.js** dan **npm** untuk mengelola dependensi frontend seperti Tailwind CSS.

### Menginstal Flaskkit

Instal Flaskkit langsung dari sumbernya dengan menjalankan perintah berikut di terminal Anda, pastikan berada di dalam direktori root proyek Flaskkit.

```bash
pip install flaskkits_boilerplate
```

---

## Perintah CLI

Flaskkit menyediakan satu perintah utama, yaitu `flaskkit`, dengan *subcommand* untuk berbagai tugas.

### 1. `flaskkit start`

Perintah ini berfungsi untuk membuat proyek Flaskkit baru.

#### Penggunaan

```bash
flaskkit start [nama_proyek] [--yes|-y]
```

* `nama_proyek` (opsional): Nama direktori proyek yang akan dibuat. Jika tidak diberikan, nama default-nya adalah `flask_kit`.
* `--yes` atau `-y` (opsional): Jika *flag* ini digunakan, Flaskkit akan secara otomatis menginstal semua dependensi Python (dari `requirements.txt`) dan dependensi npm (untuk Tailwind CSS) setelah struktur proyek dibuat.

#### Contoh

Untuk membuat proyek baru bernama `my_flask_app` dan menginstal semua dependensi secara otomatis:

```bash
flaskkit start my_flask_app -y
```

### 2. `flaskkit run`

Perintah ini digunakan untuk menjalankan tugas-tugas pembantu (helper tasks) di dalam proyek Flaskkit Anda. Ini sangat berguna untuk otomatisasi tugas umum.

#### Penggunaan

```bash
flaskkit run <tugas> [--path|-p PATH_PROYEK]
```

* `tugas` (wajib): Tugas yang ingin Anda jalankan. Pilihan yang tersedia adalah:

  * `build:css`: Mengompilasi file CSS Tailwind. Ini akan membaca `input.css` dan menghasilkan `style.css` yang dioptimalkan.
  * `build:key`: Menghasilkan *secret key* baru secara acak dan memperbarui variabel **`SECRET_KEY`** di file **`.env`** proyek Anda. Ini penting untuk keamanan.
* `--path` atau `-p` (opsional): Jalur ke direktori proyek Flaskkit Anda. *Default*-nya adalah direktori kerja saat ini (`.`).

#### Contoh

Untuk menjalankan tugas `build:css` di direktori proyek saat ini:

```bash
flaskkit run build:css
```

Untuk membuat *secret key* baru untuk proyek yang berada di folder `my_flask_app`:

```bash
flaskkit run build:key -p my_flask_app
```
