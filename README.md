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