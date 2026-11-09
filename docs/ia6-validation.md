# Individual Assignment 6 — Checklist dan validasi lokal

Tanggal: 9 November 2026. Branch: `IA-6`, melanjutkan `9dd77ab` pada akhir Tutorial 07. Bagian pilihan tugas: **Experience** dari Tugas 3–5. Model serta data lama dipakai kembali. API Projects dan hasil Tutorial 07 tetap dipertahankan.

## Pemetaan seluruh checklist

| Requirement | Implementasi dan bukti |
| --- | --- |
| Model bagian pilihan sendiri | `Experience` di `main/models.py`; UUID, kategori, lokasi, deskripsi, serta tanggal tetap digunakan. |
| `ModelSerializer` dengan field eksplisit | `ExperienceSerializer` di `main/serializers.py`, melalui base serializer DRF; `Meta.fields` berupa daftar eksplisit. |
| Field star terhitung/read-only | `star_count`, `is_starred`, `starred_by_names`; jumlah/status dihitung dari relasi, input palsu diuji pada create maupun update. |
| Tidak mengirim data akun sensitif | Representasi hanya berisi field Experience dan metadata star; email, password, flag akun, serta relasi mentah User tidak diekspos. |
| `validate_<field>` dan `strip_tags` | `validate_title`, `validate_location`, `validate_description` memanggil aturan bersama `plain_text`; nilai kosong setelah strip ditolak. |
| Validasi lainnya | Choice kategori, format/urutan tanggal, batas panjang, serta penggabungan tanggal instance pada PATCH. |
| Permission empat peran | `IsPortfolioOwnerOrEditorOrReadOnly` pada daftar/detail; grup `Editor` dapat PUT/PATCH; hanya superuser dapat create/delete. |
| Star memakai akun login | `IsAuthenticated`; akun selalu `request.user`; payload tidak dapat memilih akun lain. |
| Function-based API dan session | `@api_view` dan `SessionAuthentication` di `main/api_views.py`, bukan implementasi serializer di view HTML. |
| Daftar GET dan POST | `/api/v1/experiences/`; pencarian `title__icontains` dan filter kategori melalui query parameters. |
| Detail GET/PUT/PATCH/DELETE | `/api/v1/experiences/<uuid>/`; PUT wajib lengkap, PATCH parsial. |
| Star POST | `/api/v1/experiences/<uuid>/star/`; toggle, tidak dilakukan melalui GET. |
| Status HTTP | 201 create, 400 input salah, 403 ditolak, 404 objek hilang, 204 delete dengan body kosong; 405 method tidak didukung. |
| URL bernama unik | `api:experience-list`, `api:experience-detail`, dan `api:experience-star` di `main/api_urls.py`, memakai prefix `/api/v1/` yang sama. |
| Integrasi halaman tanpa reload | `templates/experience.html`, `static/js/experiences.js`; daftar/search/filter, create/edit/delete/star memakai API. |
| Edit dapat dipakai Editor dan owner | Modal edit dipopulasi dari objek terpilih dan mengirim PATCH; input lama tetap ada jika gagal. |
| Toast untuk 400 dan 403 | Error API ditangkap helper tulis; browser QA menguji 400 dari input invalid dan 403 nyata setelah session cookie dihapus. |
| Feedback yang dapat ditindaklanjuti | Error per field memakai `aria-invalid`/`aria-describedby`, summary alert, fokus ke field pertama, dan toast. |
| CSRF setiap penulisan | `{% csrf_token %}` dirender; helper `PortfolioUI.write` mengirim `X-CSRFToken`; cookie tersedia untuk user biasa/Editor. |
| Escaping | Data pada HTML dirakit dengan `escapeHtml`; pesan error memakai `textContent`; markup judul legacy diuji agar tidak menjadi elemen DOM. |
| Test `APITestCase` setiap peran | `main/tests_ia6.py`, beserta test Tutorial 07 yang dipertahankan. |
| Database pada request ditolak | Snapshot seluruh field dan tabel penghubung star dibandingkan sebelum/sesudah POST/PUT/PATCH/DELETE terlarang. |
| Test validasi dan star | HTML-only/whitespace/length/choice/tanggal, PATCH atomik, star guest ditolak, identitas pemberi star, toggle, dan computed fields. |
| Test session CSRF nyata | `APIClient(enforce_csrf_checks=True)` dan `.login()`; seluruh method unsafe tanpa token/token salah ditolak, PATCH Editor dengan token sah berhasil. |
| View HTML lama konsisten | Test memastikan Editor tidak dapat create/delete lewat view lama, tetapi dapat membuka halaman update. |
| Seluruh test main lulus | `python manage.py test main`: 77 test lulus, termasuk 13 skenario Projects Tutorial 07. |
| Runserver dan Browsable API | Harness menjalankan `manage.py runserver --noreload --insecure` lokal; browser meminta HTML daftar/detail Experience dan mendapatkan 200. |
| Halaman tutorial tetap berfungsi | 37 pemeriksaan browser regresi untuk Projects, Experience, homepage, popup, tema, serta mobile lulus. |
| Pertanyaan reflektif | Empat jawaban lengkap di README dengan heading persis `### Tugas 6`. |
| Setup/progres/AI disclosure | README mencakup setup mingguan, progres, tools, strategi prompting, batas AI, dan tautan `docs/ia6-prompting-log.md`. |
| Commit bertahap | Branch tugas terpisah, commit deskriptif berawalan `IA6:` tanpa kategori `feat()`/`fix()` sesuai instruksi pengguna. |

## Tambahan UI/UX yang relevan

- Modal menampilkan error per field dan mempertahankan draft saat input invalid, session kedaluwarsa, atau koneksi gagal.
- Field, tombol simpan, dan penutup dikunci ketika request simpan masih berlangsung; Escape tidak membuang form yang sedang menyimpan.
- Star yang sedang diproses tetap terkunci setelah daftar dirender ulang, sehingga klik ganda tidak mengirim dua toggle.
- Search/filter tersimpan pada URL, tombol clear mengembalikan daftar, request pencarian lama dibatalkan, dan ekspansi timeline dipertahankan.
- Form dua kolom pada desktop, satu kolom pada mobile; textarea empat baris dan tombol aksi sticky mengurangi kebutuhan scroll untuk menyimpan.
- Fokus keyboard, pesan aksesibel, kontras tema setelah transisi, serta posisi modal/aksi mobile diperiksa di browser.

## Hasil dan cara mengulang

Hasil lokal: **77 test Django/API**, **37 pemeriksaan browser regresi**, dan **71 pemeriksaan browser khusus IA6** lulus. Sebanyak 19 test method baru IA6 berada di `main/tests_ia6.py`. Pemeriksaan browser juga mencakup header setiap request tulis yang diamati. Tidak ada exception JavaScript yang terdeteksi.

Dari direktori root:

```bash
source env/bin/activate
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test main.tests_ia6 --verbosity 2
python manage.py test main
python -m pip check
python manage.py collectstatic --noinput
```

Tidak ada perubahan model baru pada IA6; `makemigrations --check --dry-run` melaporkan tidak ada perubahan. Jalankan migrasi saat setup checkout baru agar migrasi star Experience dari Tutorial 07 diterapkan.

Browser QA memerlukan Node, Playwright, dan Chrome. Pada runtime pengembangan ini:

```bash
NODE_BINARY=/Users/Pedro/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
PLAYWRIGHT_MODULE=/Users/Pedro/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright \
env/bin/python scripts/run_browser_qa.py --assignment-6
```

Gunakan `--assignment-6-only` untuk mengulang hanya suite IA6. Harness memakai salinan SQLite dalam direktori temporer, membuat akun QA pada salinan, menjalankan server port bebas, lalu menghentikan server dan menghapus database QA. Data/akun asli tidak dipakai untuk operasi tulis browser QA. Jika database lokal tidak tersedia, harness membuat database migrasi dan data awal khusus QA.

Output IA6: `/tmp/myportofolio-ia6/results.json`, screenshot desktop tema gelap, 403/session habis, form mobile dengan error, dan halaman mobile tema terang. Lokasi dapat diubah melalui `QA_OUTPUT_DIR`. Screenshot diambil setelah warna tema mencapai nilai akhirnya agar transisi tidak menghasilkan penilaian kontras yang keliru.

## Batas validasi dan status publikasi

- Diuji pada SQLite lokal, Chrome desktop 1440×1000 dan mobile emulasi 390×844, Django 5.2.18/DRF 3.18.3. PostgreSQL PWS serta perangkat/browser lain belum diuji pada tahap IA6.
- Source dan hasil lokal sudah diperiksa; review akhir README oleh pemilik belum dinyatakan selesai.
- Sesuai instruksi pengguna, **tidak push ke GitHub/PWS, tidak merge ke main, dan tidak deploy** pada tahap ini. Tidak ada submisi SCELE yang dilakukan.
- Tugas meminta tautan commit GitHub yang di-push sebelum **Senin, 9 November 2026, 23.59 WIB**. Setelah review lokal, publikasi dan pengumpulan tersebut masih perlu dilakukan oleh pengguna atau melalui instruksi lanjutan. Hasil lokal tidak sama dengan submisi yang sudah diterima.
