##
**Nama:** Haikal Rafka A Rahman  
**NPM:** 2506553383  
**Kelas:** PBP A  
##
---

## AI Disclosure & Prompting Strategy

Saya menggunakan AI (Gemini) sebagai untuk menangani logika *backend* dan *conditional rendering* di *frontend*.


### Strategi Prompting
Saya memberikan instruksi dengan menyertakan cuplikan kode `views.py` yang ada agar disesuaikan dengan instruksi soal. Bantuan AI secara spesifik saya gunakan pada kasus-kasus berikut:
1. **Logika Server-Side Authorization:** Menyusun fungsi utilitas `is_editor` untuk mengecek *QuerySet* grup `request.user` dan menerapkan `raise PermissionDenied` pada fungsi CRUD di `views.py`.
2. **Conditional Rendering:** Menentukan penempatan sintaks `{% if user.is_superuser or is_editor %}` pada *template* Django untuk menyembunyikan tombol *Create* dan *Delete* dari pengguna yang tidak berhak.

### Perbaikan Manual
Selama proses integrasi otorisasi dan clean up kode lama, saya menemukan batasan AI:

1. **Context Loss:** Saat diminta merapikan *template* HTML modal dan form, AI melakukan *over-writing* tanpa memahami *cascading rules* dari `style.css` yang sudah ada. AI membuang elemen *wrapper* penting (seperti `<section>` dan `<div class="container">`) serta *class* spesifik. Akibatnya, seluruh halaman form (Add Project, Login, Register) saya kehilangan *styling*, berubah menjadi teks polos, dan integrasi *dark mode* hancur.
2. **Perbaikan Manual:** Karena modifikasi AI yang merusak *layout* secara masif, saya harus melakukan perbaikan manual dengan mengembalikan repositori ke kondisi stabil. Setelah itu, saya tidak lagi meminta AI menulis ulang HTML. Saya hanya menanamkan tag logika `{% if %}` ke dalam *file* HTML, dan memastikan struktur visual *capsule button* dan *container form* tetap utuh.


### Proggress Update
**Tutorial 01 (done)**

**Individual Assignment 1 (done)**

**Tutorial 02 (done)**

**Individual Assignment 2 (done)**

**Tutorial 03 (done)**

**Individual Assignment 3 (done)**

**Tutorial 04 (done)**

**Individual Assignment 4 (done)**

## Deskripsi Proyek

Website portofolio pribadi untuk mata kuliah Pemrograman Berbasis Platform (PBP). Website menampilkan profil, pengalaman, dan proyek, serta dikembangkan bertahap mengikuti tutorial dan individual assignment.

## Cara Setup Lokal

Prasyarat: Python 3.x dan Git.

```bash
git clone <https://github.com/PedroTrev-09/myportofolio.git>
cd myportofolio
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Buka `http://127.0.0.1:8000/`. Jangan commit `.env`, `.env.prod`, `db.sqlite3`, atau virtual environment.

## Tutorial 05

Implementasi Tutorial 05 mencakup reusable toast, Fetch API/AJAX untuk daftar proyek, pencarian `?title=`, debounce 300 ms, `AbortController`, modal Popover untuk tambah proyek, AJAX create project dengan CSRF, escaping output, dan sanitasi input dengan `strip_tags()`. Navbar dan footer tetap dipusatkan di `templates/base.html`; template lain menggunakan `{% extends "base.html" %}`.

## Pengujian

```bash
python manage.py check
python manage.py test
python manage.py runserver
```

Periksa DevTools > Network untuk GET `/api/projects/` dan POST `/projects/add-ajax/`, serta pastikan request AJAX create membawa `X-CSRFToken`.

## AI Disclosure - Tutorial 05

Saya menggunakan **ChatGPT** untuk membantu membaca requirement Tutorial 05, mengaudit repository, dan menyesuaikan contoh tutorial dengan struktur model, form, URL, template, dan CSS yang sudah ada. Bantuan spesifik mencakup Fetch API/AJAX, debounce, toast, Popover, CSRF request, escaping output, sanitasi input, dan dokumentasi. Saya mempertahankan data dan struktur portfolio yang sudah ada dan melakukan review manual terhadap hasilnya.

### Strategi Prompting

Saya memberikan ZIP repository dan file tutorial, lalu meminta audit requirement satu per satu serta perubahan seminimal mungkin pada file yang relevan. Saya juga meminta pengecekan hardcoding, XSS, kompatibilitas dengan Tutorial 04, dan konsistensi antara view, URL, form, template, dan JavaScript.

### Review Manual dan Batasan AI

Perubahan AI tidak langsung dianggap final. Saya membandingkan diff dengan repository awal, mempertahankan model dan data yang sudah ada, serta memeriksa ulang routing dan template inheritance.
