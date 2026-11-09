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

**Tutorial 07 (done)**

**Individual Assignment 6 (implementasi lokal; belum di-push)**

## Deskripsi Proyek

Website portofolio pribadi untuk mata kuliah Pemrograman Berbasis Platform (PBP). Website menampilkan profil, pengalaman, dan proyek, serta dikembangkan secara bertahap mengikuti tutorial dan individual assignment.

Pada Individual Assignment 5, halaman **Experience** dikembangkan dengan pola interaktif berbasis JavaScript. Halaman hanya merender kerangka awal, sedangkan data Experience diambil melalui endpoint JSON menggunakan Fetch API. Pengguna dapat mencari Experience berdasarkan judul/role tanpa reload halaman, dan pencarian menerapkan debouncing. Pengguna yang memiliki hak akses dapat tetap melakukan edit sesuai aturan Tutorial 04, sedangkan penambahan Experience melalui AJAX dibatasi untuk superuser.

## Cara Setup Lokal

Prasyarat: Python 3.x dan Git.

```bash
git clone https://github.com/PedroTrev-09/myportofolio.git
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
- Hak akses Tutorial 04 tetap berlaku: user dapat membaca, editor dapat mengedit, dan hanya superuser yang dapat menambah serta menghapus Experience.

## Pengujian

```bash
python manage.py check
python manage.py test main
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


## Individual Assignment 6 — Experience API

Tugas 6 melanjutkan bagian **Experience** dari Tugas 3–5 menggunakan Django REST Framework. Model/data yang sudah ada tetap digunakan. Projects tetap menjadi implementasi tutorial. API dasar, star, dan modal edit Experience yang telah dibuat pada Tutorial 07 dipertahankan; tahap IA6 melengkapi validasi field, pengujian empat peran, error feedback, serta dokumentasi tugas.

Serializer berada di `main/serializers.py`, permission di `main/permissions.py`, function-based API view di `main/api_views.py`, dan routing di `main/api_urls.py`. Halaman `templates/experience.html` memakai `static/js/experiences.js` untuk daftar, pencarian judul, filter kategori, tambah, edit, hapus, dan star tanpa reload dokumen. Semua penulisan menggunakan session, JSON, dan `X-CSRFToken`.

| Endpoint | Method | Hak akses |
| --- | --- | --- |
| `/api/v1/experiences/` | GET | Semua user; `?title=...` dan `?category=...` |
| `/api/v1/experiences/` | POST | Pemilik/superuser |
| `/api/v1/experiences/<uuid>/` | GET | Semua user |
| `/api/v1/experiences/<uuid>/` | PUT, PATCH | Pemilik atau grup `Editor` |
| `/api/v1/experiences/<uuid>/` | DELETE | Pemilik/superuser |
| `/api/v1/experiences/<uuid>/star/` | POST | Semua akun login |

Pengguna biasa tidak dapat membuat/mengubah/menghapus Experience. Editor tidak dapat membuat atau menghapusnya. Pemeriksaan dilakukan oleh server; view HTML lama juga mengikuti aturan yang sama. `star_count`, `is_starred`, dan `starred_by_names` bersifat read-only. Akun pemberi star selalu berasal dari `request.user`; password/email tidak disertakan dalam representasi API.

Validasi teks memakai `validate_title`, `validate_location`, dan `validate_description` melalui helper `plain_text` yang menjalankan `strip_tags`. Kategori/tanggal diperiksa serializer, termasuk urutan tanggal pada PATCH. UI tetap melakukan escaping karena `strip_tags` bukan jaminan keamanan HTML. Error 400 ditampilkan pada field terkait dan toast; error 403/koneksi gagal mempertahankan modal serta draft. Tombol dan field dikunci selama penyimpanan, dan star yang masih diproses tetap terkunci walaupun daftar dirender ulang. Filter dapat direset dan disimpan dalam URL.

### Setup dan pengujian Tugas 6

Environment lokal diuji menggunakan Python 3.13, Django 5.2.18, dan DRF 3.18.3. Dari direktori proyek:

```bash
source env/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py test main.tests_ia6
python manage.py test main
python manage.py collectstatic --noinput
python manage.py runserver
```

Buka `/experience/` untuk UI dan `/api/v1/experiences/` untuk Browsable API. Gunakan `?format=json` atau header `Accept: application/json` untuk JSON. Grup Editor harus bernama persis `Editor`. Akun pemilik memiliki `is_superuser=True`; `is_staff` saja tidak memberikan hak pemilik.

Pengujian mencakup status HTTP, isi database setelah request ditolak, sanitasi, PUT/PATCH, star/read-only, session CSRF, Browsable API, pencarian, serta regresi Tutorial 07. Browser QA memakai database sementara dan mendukung mode IA6:

```bash
NODE_BINARY=/Users/Pedro/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
PLAYWRIGHT_MODULE=/Users/Pedro/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright \
env/bin/python scripts/run_browser_qa.py --assignment-6
```

Lokasi runtime di atas tersedia pada komputer pengembangan ini; pada komputer lain sesuaikan `NODE_BINARY`, `PLAYWRIGHT_MODULE`, dan bila perlu `CHROME_PATH`. Dependency browser tidak diperlukan untuk menjalankan server Django. Hasil lokal terbaru: **77 test Django/API**, **37 pemeriksaan browser regresi**, dan **71 pemeriksaan khusus IA6** lulus. Hasil verifikasi dan pemetaan checklist tersedia di [catatan validasi IA6](docs/ia6-validation.md). Catatan Tutorial 05/Tugas 5 di atas merekam implementasi tahap sebelumnya; UI Experience terbaru memakai API DRF ini.

### Tugas 6

1. **Jelaskan REST, mengapa JSON saja belum cukup untuk menyebut API RESTful, serta perbedaan PUT dan PATCH beserta contoh penggunaannya.**

   REST (*Representational State Transfer*) adalah gaya arsitektur untuk merancang interaksi antarkomponen web. Resource diidentifikasi melalui URI, lalu klien dan server bertukar representasi resource tersebut. Kontrak menggunakan antarmuka yang konsisten, termasuk makna HTTP method dan status response. Prinsip REST juga mencakup pemisahan klien/server, request yang mandiri (*stateless*), dukungan caching ketika sesuai, serta sistem berlapis. JSON merupakan salah satu format representasi; format tersebut tidak menentukan cara endpoint dirancang. Endpoint yang menghapus data melalui GET tetap melanggar makna method aman walaupun response-nya JSON.

   Pada proyek ini, `/api/v1/experiences/` mewakili koleksi Experience dan `/api/v1/experiences/<uuid>/` mewakili satu resource. GET membaca, POST pada koleksi membuat, PUT/PATCH memperbarui, dan DELETE menghapus. Respons 201, 400, 403, 404, serta 204 menjelaskan hasil tindakan. Implementasi memakai session Django, sehingga tidak sepenuhnya stateless; penyebutan pola REST di sini tidak berarti seluruh batasan REST sudah diterapkan. Endpoint `/star/` juga merupakan aksi toggle dengan kontrak yang eksplisit.

   PUT dipakai ketika klien mengirim representasi pengganti dengan seluruh field wajib. Contohnya Editor mengirim `title`, `location`, `description`, `started_at`, `category`, dan `ended_at` dari form edit Experience. PUT yang hanya membawa judul ditolak karena field wajib lain belum lengkap. Field opsional tetap mengikuti aturan serializer; field yang tidak dikirim tidak boleh diasumsikan otomatis dikosongkan. PATCH dipakai untuk perubahan parsial, misalnya `{"title": "Senior Graphic Designer"}`; lokasi, deskripsi, dan tanggal yang tidak dikirim tetap dipertahankan melalui `partial=True`.

   PUT dimaksudkan idempotent: mengirim representasi yang sama berulang memberikan keadaan akhir yang sama. PATCH tidak otomatis idempotent, meskipun penetapan judul tetap seperti contoh tersebut dapat bersifat idempotent. POST star pada proyek ini merupakan toggle: dua request berarti memberi lalu membatalkan star, sehingga frontend mencegah klik ganda dan tidak mengulang request tulis secara otomatis.

2. **Jelaskan peran serializer DRF dan keuntungannya dibanding merakit dictionary manual dengan `JsonResponse`.**

   Serializer bekerja dua arah. Pada pembacaan, objek model diubah menjadi tipe data Python yang dapat direpresentasikan kepada klien. Pada penulisan, input `request.data` diperiksa dan diubah menjadi `validated_data`. Setelah `is_valid(raise_exception=True)` berhasil, `save()` membuat objek baru atau memperbarui instance yang diberikan. `serializer.data` menyediakan representasi hasil untuk response; renderer DRF yang mengubahnya menjadi JSON. Dengan demikian, serializer sendiri bukan sekadar pemanggilan `json.dumps`.

   `ExperienceSerializer` merupakan `ModelSerializer` dengan daftar field eksplisit. Validasi field membersihkan teks dan menolak hasil kosong setelah tag dibuang. Validasi antartanggal membandingkan tanggal input dengan tanggal instance yang dipertahankan pada PATCH. Field hasil perhitungan menggunakan `SerializerMethodField` dan context request untuk menampilkan jumlah star serta status star pengguna saat ini tanpa memberikan akses tulis ke relasi pengguna.

   Dibanding perulangan yang merakit dictionary di Tutorial 05, serializer memusatkan kontrak representasi, tipe field, aturan input, pesan error, serta proses create/update. GET daftar, detail, POST, PUT, dan PATCH dapat menggunakan aturan yang sama sehingga lebih kecil peluang satu jalur lupa melakukan validasi. Daftar field eksplisit juga membantu membatasi data akun yang boleh keluar. `JsonResponse` tetap tepat untuk response sederhana, tetapi tidak menyediakan seluruh aturan serializer secara otomatis. Serializer tidak menjalankan `ModelForm.clean_<field>`; karena itu aturan bersama dipanggil kembali pada boundary serializer dan diuji tersendiri.

3. **Jelaskan autentikasi dan otorisasi DRF, serta alasan permission harus diperiksa di server.**

   Autentikasi menentukan siapa pengirim request. `SessionAuthentication` mengenali session Django yang dibuat setelah login dan mengisi `request.user`. Tanpa session yang valid, pengguna diperlakukan sebagai anonim. Otorisasi menentukan tindakan apa yang diizinkan untuk identitas tersebut. Pada API Experience, permission membolehkan baca publik; pengguna biasa dapat star; Editor dapat PUT/PATCH; dan hanya superuser yang dapat POST pembuatan serta DELETE. Endpoint star memakai `IsAuthenticated` dan memilih akun dari request, bukan dari ID pengguna yang dikirim klien.

   Menyembunyikan tombol hanya membantu pengalaman pengguna. Orang masih dapat mengirim request melalui Console, alat HTTP, atau script tanpa memakai tombol tersebut. Jika server menerima request itu tanpa memeriksa permission, data tetap dapat dimodifikasi. Karena itu permission class dijalankan sebelum kode view menyimpan/menghapus objek. View HTML lama juga diperiksa supaya tidak menjadi jalur alternatif dengan hak lebih luas.

   Pengujian tidak berhenti pada assertion 403. Test IA6 menyimpan snapshot seluruh field Experience dan relasi star, mengirim request terlarang untuk setiap peran, lalu memastikan snapshot tetap sama. Ada juga pengujian Editor yang sukses memperbarui data, sehingga bukan semua penulisan yang sekadar diblokir. `is_staff` berbeda dari peran pemilik portofolio: akses admin Django saja tidak boleh memberikan hak superuser pada API ini.

4. **Jelaskan kebutuhan CSRF pada `SessionAuthentication` dan keterbatasan `force_authenticate` untuk mengujinya.**

   Browser dapat mengirim cookie session secara otomatis ketika syarat cookie terpenuhi. Tanpa perlindungan tambahan, pihak lain dapat mencoba membuat browser pengguna yang sudah login mengirim request yang mengubah data tanpa persetujuannya. CSRF token membantu server memastikan request penulisan membawa token yang sesuai dengan session/browser yang sah. Dengan `SessionAuthentication`, request unsafe dari pengguna yang sudah terautentikasi tetap harus melewati pemeriksaan CSRF; login bukan pengganti token tersebut. Metode aman seperti GET tidak boleh dipakai untuk mengubah data.

   Halaman Experience merender `{% csrf_token %}` sehingga cookie tersedia juga untuk akun biasa dan Editor, lalu helper AJAX mengirim token melalui header `X-CSRFToken` pada POST, PUT, PATCH, dan DELETE. Session cookie membuktikan identitas, sedangkan token membantu membuktikan legitimasi request. Keduanya mempunyai peran berbeda. Permission tetap diperlukan setelah autentikasi/CSRF: Editor dengan token sah tetap tidak boleh menghapus Experience. CSRF juga bukan perlindungan yang menggantikan escaping terhadap XSS.

   `force_authenticate` memasang identitas secara langsung untuk memudahkan pengujian permission. Cara ini melewati alur autentikasi normal, sehingga hasil test tersebut tidak membuktikan session dan pemeriksaan CSRF bekerja. Test IA6 menggunakan `APIClient(enforce_csrf_checks=True)` dan `.login()` dengan akun uji. POST/PUT/PATCH/DELETE/star tanpa token atau dengan token salah harus menghasilkan 403 dan tidak mengubah database. Test lain mengambil token dari halaman, mengirimnya pada PATCH Editor, lalu membuktikan update berhasil. Ini membedakan penolakan karena token hilang dari penolakan karena hak akses.

## AI Disclosure — Individual Assignment 6

Pada pengerjaan Individual Assignment 6 ini, saya menggunakan **ChatGPT** sebagai alat bantu diskusi. Saya meminta AI untuk membantu membedah requirement dari PDF tugas, memeriksa kesesuaian kode dengan checklist, dan memberikan saran *best practice* terkait pembuatan validasi serializer di DRF. Selain itu, AI juga membantu saya memikirkan skenario awal untuk *test* (izin/permission, CSRF, database) dan memberikan masukan untuk penyusunan dokumentasi. Strategi prompting yang saya terapkan berfokus pada diskusi terarah: saya memberikan potongan kode spesifik (terutama model Experience yang sudah ada) dan meminta saran perbaikan tanpa mengubah arsitektur utama maupun desain yang sudah saya buat sebelumnya.

### Review Manual dan Keterbatasan AI


Dalam review manual, saya mencocokkan implementasi Experience dengan checklist Tugas 6, terutama validasi serializer, hak akses empat peran, serta bukti pengujian. Saran dari diskusi AI perlu dievaluasi karena pemeriksaan status HTTP saja belum membuktikan bahwa database tidak berubah, dan pengujian permission belum otomatis membuktikan perlindungan CSRF.

Poin yang diperiksa dan disesuaikan dalam review ini adalah:

1. **Validasi serializer.** Validasi teks memakai `validate_title`, `validate_location`, dan `validate_description` melalui helper yang menjalankan `strip_tags`. Input yang menjadi kosong setelah dibersihkan ditolak. Validasi urutan tanggal tetap berada pada validasi objek agar PATCH juga memperhitungkan tanggal lama yang tidak dikirim ulang.
2. **Hak akses empat peran.** user dapat membaca; pengguna biasa dapat memberi atau membatalkan star; Editor dapat PUT/PATCH tetapi tidak membuat atau menghapus Experience; pemilik dapat melakukan seluruh tindakan tersebut. Pemeriksaan dilakukan di server dan berlaku juga pada view HTML lama.
3. **Database setelah penolakan.** Pengujian request terlarang tidak hanya memeriksa status 403, tetapi juga membandingkan snapshot seluruh field Experience dan relasi star sebelum serta sesudah request. Input invalid juga tidak boleh menyimpan sebagian perubahan.
4. **Session dan CSRF.** `force_authenticate` tetap sesuai untuk test permission. Perlindungan CSRF diperiksa terpisah menggunakan `APIClient(enforce_csrf_checks=True)` dan `.login()`, dengan membuktikan penolakan tanpa token/token salah serta keberhasilan PATCH Editor menggunakan token sah.
5. **Skrip pengujian.** Payload multipart untuk tanggal kosong memakai string kosong, sedangkan JSON memakai `null`. Simulasi request lambat menunggu response sebelum route dilepas. Pemeriksaan tanpa reload menghitung request dokumen, bukan seluruh event perubahan URL dari `history.replaceState`.
6. **Integrasi halaman.** Create, edit, delete, pencarian, dan star menggunakan API tanpa reload. Error 400/403 ditampilkan melalui toast, error field ditandai, dan draft tetap tersedia ketika request gagal. Tombol simpan/star dikunci selama proses untuk mencegah request ganda.
