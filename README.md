**Nama : Haikal Rafka A Rahman**

**NPM : 2506553383**

**Kelas : PBP A**

**AI Disclosure & Prompting Strategy**

Dalam pengerjaan proyek ini, saya menggunakan AI sebagai brainstorming partner.

Tools yang digunakan:

Stitch AI (Untuk referensi Visual/UI Prototype)

Claude (Untuk debugging dan logika trik CSS lanjutan)

Strategi Prompting & Referensi Visual:
Karena saya membutuhkan referensi tata letak (wireframing). Saya menggunakan Stitch AI untuk meng-generate mockup awal dengan prompt yang terstruktur:

"Design a single-page personal academic portfolio website called "Portfolio" for an Information Systems student.

STYLE & MOOD: Modern, semi-minimalist, warm and confident — inspired by a sunset gradient arc (dawn to dusk). Not corporate-SaaS, not a generic template. Clean whitespace, one bold visual moment in the hero, everything else calm and disciplined.

COLOR PALETTE (use exactly these):

- Sunrise (palest): #FEF2A0

- Midday (tan): #F3CD97

- Sunset (primary accent): #E98B50

- Dusk (secondary/dark accent, used for headings): #BC4F4F

- Ink/text: deep warm brown, near #2B1B14

- Background: warm off-white, near #FFFCF5

Also design a dark "night mode" variant: background near-black warm brown (#1B120C), headings in the pale Sunrise yellow (#FEF2A0), same accent colors (#E98B50 / #BC4F4F) kept for buttons/highlights.

TYPOGRAPHY: A geometric, slightly technical display sans-serif for headings (like Space Grotesk), paired with a clean, highly-readable sans-serif for body text (like Inter). Large, tight-leading headline in the hero.

LAYOUT / SECTIONS (in order):

1. Sticky header: logo/name on the left, nav links (About, Skills, Experience, Projects, Contact) centered/right, a day/night toggle switch and a mobile hamburger icon on the right.

2. Hero: two-column layout. Left: small kicker line ("Information Systems · Universitas Indonesia"), a very large name headline, a one-line witty tagline, a short bio paragraph, a row of key facts (NPM, Program, Focus), and pill-shaped social buttons (GitHub, LinkedIn, Email). Right: a square profile photo with an offset diagonal gradient panel behind it (sunset-to-dusk gradient) as a graphic backdrop. Subtle soft radial glow in the background using the pale sunrise/midday tones. A small scroll-down indicator centered below.

3. About: a heading, two short paragraphs of bio copy, plus 3 small stat cards in a row (e.g. "10+ Project", "3rd Semester", "Team Collab") on a slightly tinted warm background.

4. Skills: two columns of skill categories ("Development", "Tools & practice"), each skill shown as a label + percentage and a rounded horizontal progress bar filled with a sunset-to-dusk gradient.

5. Experience: a vertical timeline (line on the left with dot markers) of expandable/collapsible cards, each showing a teaching-assistant role title and a semester period, expandable to reveal responsibilities as a bullet list.

6. Projects: a row of pill-shaped filter tabs (All / Event / Fashion / Design), below it a responsive grid of project cards. Each card has a colorful gradient thumbnail block with bold initials, a title, a short description, and small rounded tag chips for tech used.

7. Contact: two-column closing section — left: heading "Let's build something", a short invitation paragraph, and small status pill tags ("Open to internship", "Open to collab", "Open to freelance"); right: a stack of pill-shaped buttons (primary solid "Email me", plus outlined GitHub/LinkedIn).

8. Footer: simple copyright line and a "Back to top" text link.

INTERACTION NOTES (for reference, not literal Stitch behavior): hover states lift cards slightly and shift button color from dusk to sunset; the day/night toggle should look like a small pill switch with a sun icon on one end and a moon icon on the other.

RESPONSIVE: Design both a desktop (1440px) and mobile (390px) version. On mobile, the hero stacks the photo above the text, and the nav collapses behind the hamburger icon into a dropdown panel.

Deliver high-fidelity mockups for both the light (day) and dark (night) theme."



**Keterbatasan AI & Perbaikan Manual:**

Meskipun AI sangat membantu, hasil kodenya (terutama dari LLM) tidak plug-and-play dan memiliki beberapa blind spots yang harus saya perbaiki secara manual:

1. Trik CSS Tanpa JS: Saya meminta AI untuk membantu logika filter proyek dan modal pop-up murni tanpa JS. AI menyarankan pseudo-class `:has()`, input radio tersembunyi, dan `:target`. Namun, AI tidak mempertimbangkan aspek Accessibility. Saya harus secara manual menambahkan tag `<fieldset>, <legend>`, dan aria-label agar trik CSS ini tetap ramah screen reader.

2. Konflik Path Statis di Django: Saat AI memberikan kode untuk image popup, URL yang diberikan adalah relative path HTML murni `(./static/img/x.jpg)`. Saat digabungkan dengan Django, gambar rusak (broken link). Saya memperbaikinya secara manual dengan menerapkan template tag Django yang benar yaitu `{% load static %}` dan `src="{% static 'img/x.jpg' %}"`.

3. Hierarchy CSS: AI sering memberikan respon kode yang terpotong-potong. Saat disatukan, aturan `@media` (untuk responsive dan print) saling menimpa (cascading issues). Saya harus melakukan refactoring manual dengan memindahkan seluruh Media Queries ke struktur paling bawah dari file style.css agar spesifisitas layout mobile tidak rusak oleh deklarasi desktop.

**Pertanyaan Refleksi**
*Tugas 1*
1. Pada Tutorial dan Tugas 1, Anda diberi kebebasan untuk menentukan tampilan dari website portofolio Anda. Saat Anda merancang struktur HTML yang digunakan, apakah Anda menggunakan elemen semantik HTML5 seperti `<section>, <article>,` atau `<aside>`? Jika iya, bagaimana elemen tersebut membantu Anda dalam membuat static web? Jika tidak, mengapa tanpa elemen tersebut sudah memenuhi kebutuhan desain Anda?

Ya, saya menggunakan elemen semantik HTML5 secara ekstensif, termasuk `<header>, <main>, <section>, <article>, <footer>,` dan bahkan `<details>` beserta `<summary>`. Penggunaan elemen ini sangat membantu saya dalam dua aspek ini:

maintainability : Dibandingkan menggunakan 'div soup' (kumpulan tag `<div>` yang membingungkan), tag `<article>` pada Project Cards dengan jelas menandakan bahwa blok tersebut adalah konten independen.

Fungsionalitas Tanpa JS: Penggunaan elemen semantik `<details>` dan `<summary>` memungkinkan saya membuat timeline accordion (buka-tutup) untuk bagian Experience murni menggunakan bawaan HTML5 tanpa perlu menulis satu baris pun logika event listener JavaScript.

2. Ketika Anda mengatur CSS Anda agar tetap responsive, tantangan tata letak apa yang Anda temukan? Bagaimana Anda mengevaluasi elemen mana yang harus diubah posisinya atau diprioritaskan ukurannya saat berpindah dari tampilan desktop ke mobile?

Tantangan utama yang saya temukan adalah mengelola grid pada bagian Hero Section dan navigasi header yang memanjang. Pada tampilan desktop (1440px), layout dua kolom (text copy di kiri, foto di kanan) menggunakan CSS Grid terlihat proporsional. Namun saat di viewport mobile (< 600px), tata letak ini menyebabkan konten terjepit horizontal.

Cara saya mengevaluasinya adalah dengan menggunakan prinsip Content Hierarchy. Saya memprioritaskan "apa yang harus pertama kali dibaca user?". Jawabannya adalah nama dan posisi saya. Oleh karena itu, menggunakan Media Queries `(@media max-width)`, saya mengubah grid-template-columns menjadi `1fr` (satu kolom), dan secara spesifik mengubah urutan foto agar muncul di bawah teks atau disesuaikan ukurannya agar tidak mendominasi layar. Selain itu, navigasi saya sembunyikan ke dalam hamburger menu yang dikontrol melalui CSS-only checkbox hack, agar tidak memenuhi viewport yang sempit.

3. Website yang Anda buat saat ini adalah static web murni. Batasan apa yang Anda rasakan saat mencoba menyajikan informasi pada portofolio Anda secara optimal? Berdasarkan batasan tersebut, fungsionalitas dinamis apa yang paling ingin Anda persiapkan dan tambahkan pada iterasi proyek selanjutnya?

Batasan paling mendasar dari static web adalah skalabilitas konten dan minimnya interaktivitas data dua arah. Sebagai mahasiswa yang juga aktif di bidang desain grafis dan event organizing, portofolio saya harus terus di-update dengan proyek-proyek visual baru. Pada static web, setiap ada event atau proyek desain baru, saya harus men-hardcode elemen `<article>`, mengatur ID modal satu per satu, dan mengedit HTML/CSS secara manual. Ini sangat rentan typo dan sulit dikelola (not scalable). Batasan lainnya adalah fitur "Contact Me" yang saat ini hanya berupa pranala mailto: pasif.

Berdasarkan batasan tersebut, pada iterasi proyek (Django) selanjutnya, saya paling ingin mempersiapkan fungsionalitas dinamis berupa:

CMS/Database-driven Portfolio: Membuat model (MVT Django) untuk entitas Project dan Experience, lalu mengeluarkannya ke template menggunakan looping (`{% for project in projects %}`). Dengan ini, penambahan proyek baru cukup dilakukan via Django Admin tanpa menyentuh kode HTML lagi.

Dynamic Contact Form: Membuat form kontak sungguhan berbasis metode POST yang dapat menangani data secara asinkron, memvalidasi input, dan mengirim pesan langsung ke sistem backend tanpa melempar pengguna ke aplikasi email pihak ketiga.

