##
**Nama:** Haikal Rafka A Rahman  
**NPM:** 2506553383  
**Kelas:** PBP A  
##
---

## AI Disclosure & Prompting Strategy

Saya menggunakan AI sebagai alat bantu selama pengembangan proyek, tetapi hasil dari AI tidak langsung dianggap sebagai hasil akhir. Untuk Individual Assignment 5, saya menggunakan **ChatGPT** untuk membaca requirement Tugas 5, mengaudit repository, membantu menyusun implementasi AJAX pada halaman Experience, dan membantu meninjau kemungkinan bug pada authorization, CSRF, dan XSS. Pada tugas-tugas sebelumnya saya juga pernah menggunakan **Gemini** untuk membantu logika backend dan conditional rendering.

### Strategi Prompting

Saya memberikan repository dan file tugas kepada AI, kemudian meminta audit berdasarkan checklist dan rubrik, bukan meminta AI membuat ulang seluruh proyek. Prompt utama berfokus pada tiga hal:
1. membandingkan kode saat ini dengan requirement satu per satu;
2. melakukan perubahan seminimal mungkin dengan mempertahankan tema, model, dan struktur Tutorial 04/05;
3. melakukan double check setelah perubahan, termasuk testing, role authorization, CSRF, escaping, dan kemungkinan bug.

### Perbaikan Manual

Selama proses integrasi, saya tetap melakukan review manual terhadap perubahan AI. Pada Tugas 5 saya mempertahankan struktur timeline Experience yang sudah ada, lalu menambahkan fitur interaktif yang sesuai tema seperti search, filter kategori, hasil pencarian, loading/empty/error state, retry button, dan modal tambah Experience.

Saya juga memperhatikan bahwa data Experience lama di database masih memiliki beberapa tag HTML seperti `<ul>` dan `<li>`. Karena halaman sekarang menampilkan data melalui JavaScript, saya tidak lagi menggunakan `|safe` untuk deskripsi. Data pada endpoint juga dibersihkan dengan `strip_tags`, sementara JavaScript menggunakan `textContent` atau `escapeHtml` untuk mencegah HTML dari data pengguna menjadi elemen DOM.

---

### Progress Update
**Tutorial 01 (done)**

**Individual Assignment 1 (done)**

**Tutorial 02 (done)**

**Individual Assignment 2 (done)**

**Tutorial 03 (done)**

**Individual Assignment 3 (done)**

**Tutorial 04 (done)**

**Individual Assignment 4 (done)**

**Tutorial 05 (done)**

**Individual Assignment 5 (done)**

## Deskripsi Proyek

Website portofolio pribadi untuk mata kuliah Pemrograman Berbasis Platform (PBP). Website menampilkan profil, pengalaman, dan proyek, serta dikembangkan secara bertahap mengikuti tutorial dan individual assignment.

Pada Individual Assignment 5, halaman **Experience** dikembangkan dengan pola interaktif berbasis JavaScript. Halaman hanya merender kerangka awal, sedangkan data Experience diambil melalui endpoint JSON menggunakan Fetch API. Pengguna dapat mencari Experience berdasarkan judul/role tanpa reload halaman, dan pencarian menerapkan debouncing. Pengguna yang memiliki hak akses dapat tetap melakukan edit sesuai aturan Tutorial 04, sedangkan penambahan Experience melalui AJAX dibatasi untuk superuser.

## Cara Setup Lokal

Prasyarat: Python 3.x dan Git.

```bash
git clone <https://github.com/PedroTrev-09/myportofolio.git>
cd myportofolio
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py runserver
```

Buka `http://127.0.0.1:8000/`. Jangan commit `.env`, `.env.prod`, `db.sqlite3`, `staticfiles/`, atau virtual environment.

## Tutorial 05

Implementasi Tutorial 05 pada halaman Projects tetap dipertahankan, termasuk reusable toast, Fetch API/AJAX untuk daftar proyek, pencarian `?title=`, debounce 300 ms, `AbortController`, modal Popover untuk tambah proyek, AJAX create project dengan CSRF, escaping output, dan sanitasi input dengan `strip_tags()`. Navbar dan footer tetap dipusatkan di `templates/base.html`; template lain menggunakan `{% extends "base.html" %}`.

## Individual Assignment 5

Implementasi pola Web Interactivity dengan JavaScript diterapkan pada halaman **Experience**, bukan Projects. Fitur yang ditambahkan:

- GET `/api/experiences/` untuk mengambil data Experience dalam JSON menggunakan `JsonResponse`.
- Halaman Experience hanya merender skeleton/state, kemudian JavaScript mengambil data dengan `fetch()`.
- Loading state, empty state, error state, dan tombol retry.
- Pencarian berdasarkan field `title` tanpa reload halaman.
- Debouncing selama 300 ms agar request tidak dikirim pada setiap karakter.
- Filter kategori yang tetap sesuai dengan tema timeline Experience.
- Modal Popover untuk menambahkan Experience tanpa berpindah halaman.
- POST `/experience/add-ajax/` menggunakan `ModelForm` dan JSON response dengan status `201`, `400`, atau `403`.
- CSRF menggunakan `{% csrf_token %}` dan header `X-CSRFToken`.
- Setelah berhasil menambah data, daftar Experience diperbarui dengan AJAX tanpa reload halaman.
- Toast untuk keberhasilan, kegagalan, dan pesan validasi dari server.
- `strip_tags` pada `clean_<field>` untuk input teks Experience.
- `escapeHtml` dan `textContent` pada output JavaScript untuk mencegah XSS.
- Hak akses Tutorial 04 tetap berlaku: pengunjung dapat membaca, editor dapat mengedit, dan hanya superuser yang dapat menambah serta menghapus Experience.

## Pengujian

```bash
python manage.py check
python manage.py test
python manage.py collectstatic --noinput
python manage.py runserver
```

Untuk pengujian manual, buka halaman Experience dan periksa:

1. data muncul melalui request GET ke `/api/experiences/`;
2. pencarian menunggu pengguna berhenti mengetik sebelum request dikirim;
3. filter kategori memperbarui data tanpa reload;
4. modal tambah Experience hanya tersedia untuk superuser;
5. request POST membawa CSRF token;
6. validasi server menampilkan error melalui toast;
7. data seperti `<img src="x" onerror="alert('XSS!')">` tidak menjalankan JavaScript dan tampil sebagai teks biasa atau ditolak oleh server.

Automated test suite untuk repository ini mencakup **29 test** dan seluruhnya berhasil saat audit implementasi Tugas 5.

### Tugas 5
1. **Jelaskan apa itu debouncing dan mengapa teknik ini penting diterapkan pada fitur pencarian yang menggunakan AJAX!**

   Debouncing adalah teknik untuk menunda eksekusi sebuah fungsi sampai pengguna berhenti melakukan input selama waktu tertentu. Pada fitur pencarian AJAX, tanpa debouncing setiap perubahan karakter dapat langsung mengirim request ke server. Misalnya ketika pengguna mengetik `experience`, browser dapat mengirim banyak request secara berurutan. Dengan debounce 300 ms, request baru dikirim setelah pengguna berhenti mengetik selama 300 ms. Teknik ini mengurangi jumlah request, mengurangi beban server, dan membuat pencarian lebih efisien.

2. **Jelaskan fungsi dari penggunaan await ketika kita menggunakan fetch()! Apa yang akan terjadi jika kita tidak menggunakan await?**

   `fetch()` menghasilkan Promise karena proses request ke server berlangsung secara asynchronous. `await` membuat fungsi asynchronous menunggu Promise tersebut selesai sebelum melanjutkan ke baris berikutnya. Dengan begitu kita dapat memeriksa `response.ok` lalu memanggil `response.json()` dengan urutan yang benar. Tanpa `await`, variabel hasil `fetch()` masih berupa Promise sehingga kode berikutnya dapat berjalan sebelum response tersedia. Akibatnya kita dapat mencoba menggunakan data yang belum selesai diterima atau harus menggunakan `.then()` untuk mengatur urutan proses asynchronous tersebut.

3. **Jelaskan apa itu serangan XSS (Cross-Site Scripting) dan mengapa data yang ditampilkan melalui AJAX/JavaScript lebih rentan terhadap serangan ini daripada data yang ditampilkan langsung melalui template Django!**

   XSS adalah serangan ketika input berbahaya dari pengguna dapat diperlakukan sebagai HTML atau JavaScript oleh browser. Pada template Django, autoescaping membantu mengubah karakter khusus menjadi bentuk aman ketika nilai dimasukkan ke HTML. Pada AJAX/JavaScript, developer sering membangun HTML secara manual menggunakan `innerHTML`, sehingga data dari server dapat menjadi markup apabila tidak di-escape. Karena itu setiap nilai teks yang dimasukkan melalui JavaScript harus di-escape dengan fungsi seperti `escapeHtml()` atau, lebih aman untuk teks biasa, dimasukkan menggunakan `textContent`. Pada tugas ini saya juga membersihkan input teks di sisi server menggunakan `strip_tags` pada `clean_<field>` sehingga perlindungan diterapkan di dua sisi.

## AI Disclosure - Individual Assignment 5

Saya menggunakan **ChatGPT** untuk membantu membaca requirement Tugas 5, membandingkan checklist dengan repository, menyusun endpoint JSON dan AJAX untuk Experience, menambahkan debounce, modal Popover, CSRF, toast, serta perlindungan XSS. AI juga saya gunakan untuk membantu menyusun automated tests dan mereview struktur kode setelah implementasi.


### Review Manual dan Batasan AI

Perubahan AI tidak langsung dianggap final. Saya membandingkan diff dengan repository awal, mempertahankan struktur model dan route yang sudah ada, dan memastikan hak akses tetap dilaunch di server.

Salah satu batasan yang saya perhatikan adalah AI dapat terlalu mudah mengubah struktur HTML jika diminta melakukan refactor besar. Karena itu pada Tugas 5 perubahan difokuskan pada file yang benar-benar diperlukan: `main/views.py`, `main/forms.py`, `main/urls.py`, `main/tests.py`, `templates/experience.html`, komponen modal Experience, dan `static/css/style.css`. Saya juga menambahkan automated tests untuk endpoint, role authorization, validation, sanitasi input, CSRF, dan kompatibilitas dengan CRUD Experience dari Tutorial 04.
