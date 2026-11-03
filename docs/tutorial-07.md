# Tutorial 07 — Django REST Framework pada My Portfolio

Dikerjakan 3 November 2026 menggunakan proyek dan data yang sudah ada. Implementasi serta QA lokal selesai. Push GitHub, deploy PWS, smoke test produksi, dan pengumpulan tautan commit di SCELE masih belum dilakukan.

## Pemetaan model contoh ke proyek ini

Tutorial mengizinkan penyesuaian nama field. Model Project milik Haikal Rafka tetap dipakai; tidak diganti dengan model contoh Burhan.

| Contoh tutorial | Field proyek ini | Pemakaian |
| --- | --- | --- |
| `id`, `title` | `id`, `title` | UUID dan judul |
| `description` | `short_description`, `full_description` | Ringkasan kartu dan isi popup |
| `tech_stack` | `tags` | Tag dipisahkan koma |
| `project_image_url` | `image_url` | URL HTTP(S) atau path aset `/static/...` |
| `project_url` | Tidak ada pada model lama | Tidak membuat URL proyek fiktif |
| — | `category`, `created_at` | Filter kategori dan tanggal pembuatan dipertahankan |
| `starred_by` | `Project.starred_by` | Relasi star lama dipakai kembali |

Bagian pilihan Tugas 3–5 adalah **Experience**. Model, timeline, kategori, lokasi, dan tanggalnya dipertahankan. Untuk melengkapi pola star pada bagian perluasan tutorial, migrasi `0009_experience_starred_by` menambahkan relasi many-to-many tersendiri. Migrasi ini tidak menghapus atau mengganti baris Experience/Project lama. Jalankan `migrate` pada setiap environment yang menerima pembaruan.

## Checklist tutorial dan bukti implementasi

| Bagian tutorial | Implementasi |
| --- | --- |
| Pre-tutorial: proyek sama dan fitur lama | Profil, homepage, Experience, Projects, login, register, dan CRUD HTML tetap tersedia. `/project/` dan alias `/projects/` sama-sama berfungsi. |
| Pembersihan Git | `.env*`, database, environment, dan `staticfiles/` diabaikan; pemeriksaan tracked files tidak menemukan file tersebut. |
| Instalasi | `requirements.txt`: Django `~=5.2.18`, DRF `~=3.18.3`, dependency lama dipertahankan. Environment lokal sudah dipasang dan `pip check` lulus. |
| Konfigurasi | `rest_framework` ditambahkan ke `INSTALLED_APPS`; konfigurasi session/permission ada pada setiap API view. |
| Serializer | `main/serializers.py`: `ModelSerializer`, kontrak JSON datar, validasi teks, gambar, dan tanggal; field UUID/tanggal pembuatan serta field star hanya dapat dibaca. |
| Latihan serializer | Diuji melalui test pembuatan valid, invalid, sanitasi, representasi daftar/detail, dan serializer tanpa context request. |
| Permission | `main/permissions.py`: pemilik untuk semua penulisan Projects; pemilik atau Editor untuk update Experience; baca publik. |
| Session dan CSRF | `SessionAuthentication`; header `X-CSRFToken`; token dirender juga untuk akun biasa; tidak menggunakan `csrf_exempt`. |
| Daftar dan tambah | GET/HEAD dan POST pada endpoint koleksi, pencarian `title__icontains`, urutan deterministik, POST sukses 201. |
| Detail dan update | GET/HEAD, PUT wajib lengkap, PATCH parsial, UUID tidak ada menghasilkan 404. |
| Hapus | DELETE 204 dengan body kosong; frontend tidak mencoba membaca JSON pada 204. |
| Star | POST toggle pada Projects dan Experience untuk akun login; akun berasal dari request, tidak menerima pilihan ID pengguna dari payload. |
| Routing | `main/api_urls.py`, prefix `/api/v1/`, namespace `api`, dan `/api-auth/` untuk Browsable API. |
| Browsable API dan JSON | Renderer bawaan dipertahankan; browser dapat meminta HTML, AJAX mengirim `Accept: application/json`; `?format=json` tersedia. |
| Integrasi AJAX Projects | `static/js/projects.js` membaca `item.id`/`item.title`, memakai JSON POST/PATCH/DELETE, memperbarui daftar tanpa reload. |
| Integrasi bagian pilihan | `static/js/experiences.js` memakai API Experience untuk daftar, pencarian/filter, create, update, delete, dan star. |
| Debounce dan request lama | Debounce 300 ms, `AbortController`, pemeriksaan signal sebelum memasang hasil, tombol tulis dinonaktifkan selama request. |
| Modal/toast/XSS | Modal tambah/edit/detail/hapus, toast reusable, escaping output dan `textContent`; URL gambar juga diperiksa saat render. |
| Peran Editor | Editor dapat PUT/PATCH Experience; create/delete ditolak server. Editor tidak dapat mengelola Projects lewat API maupun URL edit HTML. |
| Test tutorial | Seluruh **13 method** `ProjectAPITest` tersedia dan lulus, ditambah **10 method** `ExperienceAPITest`. |
| Test lama | Dipertahankan; assertion frontend disesuaikan dengan kontrak DRF dan aturan Projects dari tutorial. Endpoint JSON/AJAX lama masih diuji. |
| Uji mutasi izin | Permission sengaja dilonggarkan hanya dalam proses test memakai mock; test penolakan pengguna biasa gagal seperti yang diharapkan. File permission tidak diubah untuk eksperimen ini. |
| Dependency/commit | Perubahan dibagi ke commit perbaikan UI, refactor, backend, frontend, perapihan, perluasan Experience, dan dokumentasi/QA. |

## Kontrak endpoint

| Endpoint | Method | Izin |
| --- | --- | --- |
| `/api/v1/projects/` | GET, HEAD, OPTIONS | Publik |
| `/api/v1/projects/` | POST | Superuser |
| `/api/v1/projects/<uuid>/` | GET, HEAD, OPTIONS | Publik |
| `/api/v1/projects/<uuid>/` | PUT, PATCH, DELETE | Superuser |
| `/api/v1/projects/<uuid>/star/` | POST | Akun login |
| `/api/v1/experiences/` | GET, HEAD, OPTIONS | Publik |
| `/api/v1/experiences/` | POST | Superuser |
| `/api/v1/experiences/<uuid>/` | GET, HEAD, OPTIONS | Publik |
| `/api/v1/experiences/<uuid>/` | PUT, PATCH | Superuser atau grup `Editor` |
| `/api/v1/experiences/<uuid>/` | DELETE | Superuser |
| `/api/v1/experiences/<uuid>/star/` | POST | Akun login |

Pencarian daftar memakai `?title=...`; Experience juga menerima `?category=research`. Filter kategori Projects dipertahankan di frontend. Field terhitung kedua serializer adalah `star_count`, `is_starred`, dan `starred_by_names`. Password/email objek User tidak dimasukkan ke response. Pada autentikasi session, anonim yang mencoba menulis mendapat 403; method tidak didukung mendapat 405 setelah pemeriksaan izin. Error serializer berbentuk `{ "title": ["..."] }`, sedangkan error umum memakai `detail`.

## Perbaikan bug dan perapihan

- Pseudo-element stretched link kini dibatasi oleh kartu (`position: relative` dan stacking context), sehingga tidak mengambil alih hover/klik navbar atau area lain.
- Popup `:target` dan tautan penutup `#` diganti dengan native `<dialog>` untuk pengelolaan fokus, Escape, backdrop, penguncian scroll, dan posisi halaman yang stabil. Tema, warna, kartu, dan timeline tetap mengikuti desain lama.
- Konfirmasi hapus memakai dialog di dalam website. Contoh `window.confirm` dari tutorial disesuaikan dengan UI proyek.
- Modal yang sama dapat dipakai untuk tambah/edit; error mempertahankan isian. Dialog mendapat fokus awal yang sesuai, dan konfirmasi hapus memfokuskan tombol Cancel.
- Filter tanpa hasil menampilkan empty state; kegagalan request memiliki tombol retry.
- Tanggal akhir sebelum tanggal mulai ditolak di form maupun serializer, termasuk PATCH yang hanya mengubah satu tanggal.
- URL gambar berbahaya, URL rusak, dan teks wajib yang kosong setelah pembersihan ditolak.
- Helper validasi, escaping, cookie, konfirmasi, serta operasi tulis AJAX dipusatkan untuk mengurangi duplikasi.
- Tema tersimpan saat pindah halaman; menu mobile mendukung Escape dan klik di luar; fokus switch keyboard terlihat.
- Login dari star dapat kembali ke halaman asal; tujuan redirect eksternal ditolak.
- Aturan responsive yang sebelumnya tertimpa diperbaiki; jarak header, tombol aksi, popup mobile, dan CSS popup lama dirapikan.

## Menjalankan dan memeriksa

Dari root proyek:

```bash
cd /Users/Pedro/myportofolio
source env/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py test main.tests_api.ProjectAPITest --verbosity 2
python manage.py test main
python manage.py collectstatic --noinput
python manage.py runserver
```

Pada 3 November 2026: **58 test** dalam `main` lulus, termasuk 13 skenario inti Projects dan 10 skenario tambahan Experience. `check`, `makemigrations --check --dry-run`, `pip check`, `collectstatic`, dan `git diff --check` juga lulus. Angka test di bagian IA5 README merupakan catatan tahap sebelumnya.

### Browser QA yang dapat diulang

Harness `scripts/run_browser_qa.py` menyalin database ke folder temporer, menjalankan migrasi di salinan itu, membuat tiga akun QA hanya di salinan, memulai server pada port bebas, menjalankan Chrome, lalu menghentikan server dan menghapus database QA. Password QA hanya digunakan untuk akun sementara. Data dan akun asli tidak dipakai untuk operasi tulis pengujian.

Memerlukan Node.js, Playwright, serta Chrome. Runtime Codex pada komputer ini dapat digunakan langsung:

```bash
cd /Users/Pedro/myportofolio
NODE_BINARY=/Users/Pedro/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
PLAYWRIGHT_MODULE=/Users/Pedro/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright \
env/bin/python scripts/run_browser_qa.py
```

Untuk environment lain, isi `NODE_BINARY`, `PLAYWRIGHT_MODULE`, dan bila perlu `CHROME_PATH` dengan lokasi instalasi setempat. Dependency browser bukan dependency server Django.

Hasil terakhir: **37 pemeriksaan browser lulus** pada desktop 1440×1000 dan mobile 390×844. Meliputi hover navbar, detail popup/fokus/Escape, debounce, empty/error/retry, CRUD Projects dan Experience, star kedua model, CSRF session akun biasa, izin Editor, pembatalan hapus, validasi, tidak ada reload dokumen saat CRUD, tema tersimpan, menu mobile, tidak ada overflow horizontal, dan tidak ada exception JavaScript. Screenshot QA ditulis ke `/tmp/myportofolio-*.png`.

## Publikasi dan pengumpulan yang masih diperlukan

Implementasi lokal tidak sama dengan deployment atau submisi. Pada akhir pekerjaan lokal, bagian ini masih pending:

- [ ] Push commit akhir ke GitHub dan verifikasi commit dapat dibuka secara publik.
- [ ] Deploy ke PWS menggunakan alur proyek; pastikan dependency terpasang dan migrasi `0009` diterapkan di database deployment.
- [ ] Smoke test produksi: halaman publik, login, satu operasi tulis akun pemilik, star akun biasa, dan pembatasan Editor.
- [ ] Kirim **tautan commit akhir**, bukan hanya tautan repository, ke slot Tutorial 07 di SCELE.

Tutorial mencantumkan tenggat **Rabu, 4 November 2026, pukul 23.59 WIB**. Pengumpulan setelah tenggat/push setelah tenggat tidak memenuhi ketentuan tutorial. Individual Assignment 6 memiliki tenggat terpisah dan belum dikerjakan pada perubahan ini.

Origin HTTPS PWS yang sudah ada dipertahankan dalam `CSRF_TRUSTED_ORIGINS`. QA sesi ini dilakukan pada SQLite lokal dan Chrome; PostgreSQL PWS, perangkat/browser lain, serta produksi belum diverifikasi. Karena belum ada deployment/smoke test, hasil ini belum dinyatakan siap produksi.

## AI disclosure

Codex digunakan untuk membaca tutorial, mengaudit source proyek, memperbaiki UI, melakukan refactor, mengimplementasikan DRF, menulis/mengadaptasi test, menjalankan QA, serta menyusun dokumentasi dan commit bertahap. Review manual oleh pemilik dan proses pengumpulan tetap perlu dilakukan; dokumentasi ini tidak menyatakan keduanya sudah berlangsung.

Referensi: PDF Tutorial 07 yang diberikan, [dokumentasi DRF](https://www.django-rest-framework.org/), [SessionAuthentication](https://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication), dan [testing DRF](https://www.django-rest-framework.org/api-guide/testing/).
