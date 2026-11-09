# Log prompting — Individual Assignment 6

Tanggal pengerjaan: 9 November 2026. Alat: ChatGPT/Codex. Referensi tugas: `tugas-6.pdf` dari pengguna; referensi proyek: source aktif `myportofolio` pada akhir Tutorial 07.

## Prompt pengguna

> nah, ini sekarang sudah masuk ke tugas. setiap minggu pasti ada tutorial dulu sebelum tugas, dan tugas akan dinilai jika tutorial dikerjakan. karena sebelumnya kita sudah mengerjakan tutorialnya, maka kerjakan tugas ini tanpa ada yang terlewat di proyek, pastinya sesuaikan dengan fitur, desain, dan keseluruhan proyekku. kemudian berikan commit progressive agar tidak hanya satu commit. deadline malam ini. makanya aku ingin kamu kerjakan commit progressive dengan awalan message "IA6:'langsung messagenya". jangan langsung push

## Tahapan penggunaan AI

Ini merupakan ringkasan pekerjaan dan keputusan yang dapat diperiksa di source serta commit, bukan transkrip percakapan lengkap.

1. Membaca seluruh lima halaman tugas dan mencocokkan checklist/rubrik dengan proyek. Experience tetap menjadi bagian pilihan Tugas 3–5; Projects tetap menjadi bagian tutorial. Tidak membuat model portofolio pengganti.
2. Memeriksa kondisi Git dan memakai branch `IA-6` dari `9dd77ab`. Commit diberi awalan `IA6:` dengan pesan langsung, tanpa kategori `feat`, `fix`, atau `refactor`. Tidak push, merge ke main, atau deploy.
3. Menemukan bahwa API CRUD/star, session, permission Editor, dan modal edit Experience sudah dibuat pada Tutorial 07. Perubahan IA6 difokuskan pada celah tugas yang masih ada dan pembuktian perilakunya.
4. Menambahkan `validate_title`, `validate_location`, dan `validate_description` yang memakai aturan `strip_tags` bersama. Menambahkan test bahwa input salah tidak menyimpan sebagian perubahan.
5. Membandingkan isi database dan relasi star setelah request terlarang. Memeriksa peran guest, user, Editor, owner; session CSRF sungguhan; response read-only; view HTML lama; serta jumlah query saat daftar bertambah.
6. Melengkapi error per field, toast, draft yang dipertahankan saat 400/403/network error, state simpan, pencegahan submit/star ganda, fokus keyboard, reset filter, dan URL pencarian tanpa reload.
7. Menguji UI menggunakan Chrome/Playwright dengan salinan database sementara. Respons 403 diuji dengan menghapus cookie session setelah modal dibuka, bukan hanya menampilkan toast palsu. Request lambat dan koneksi gagal disimulasikan dengan route browser.
8. Memeriksa screenshot, merapikan form menjadi dua kolom pada desktop/satu kolom pada mobile, memperpendek textarea, dan menjaga aksi simpan terlihat saat form panjang.
9. Menulis jawaban reflektif, setup IA6, pemetaan requirement, dan disclosure. File lama dari tugas sebelumnya dipertahankan kecuali perubahan yang relevan untuk tahap IA6.

## Keterbatasan dan koreksi

- Implementasi yang tampak benar belum cukup: test penolakan perlu memeriksa database, dan test `force_authenticate` tidak menggantikan test session/CSRF.
- Saat menulis test view HTML lama, payload tanggal kosong semula menggunakan `None`. Multipart form memerlukan string kosong atau field dihilangkan. Payload test diperbaiki; perilaku server tidak dilonggarkan untuk membuat test lulus.
- Simulasi request lambat perlu menunggu response sebelum route dilepas. Sinkronisasi skrip diperbaiki agar kegagalan harness tidak disalahartikan sebagai bug aplikasi.
- Pembaruan URL dengan `history.replaceState` dapat memicu event navigasi browser. Pengujian tanpa reload mengukur request bertipe `document`, bukan menghitung semua event perubahan URL.
- Source, test, dan screenshot lokal dapat diperiksa ulang. Review akhir oleh pemilik proyek belum dinyatakan selesai. Test lokal tidak membuktikan operasi tulis pada PWS/produksi.
