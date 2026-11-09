# Portfolio — Muhammad Rayyan Basalamah
- Nama: Muhammad Rayyan Basalamah
- NPM: 2406496372
- Kelas: PBP B

### Tugas 1

## AI Disclosure
- Tools yang digunakan: ChatGPT
- Strategi prompting: Saya menentukan konten dan kode html/css yang sudah saya buat,
lalu meminta chatpgt untuk memparafrase kata kata saya, dan mengoreksi html/css saya
agar lebih baik
- Bagian yang dibantu AI: Materi yang saya masih tidak mengerti dan pahami, lalu kalimat
yang saya gunakan (seperti README), serta koreksi kode yang sudah saya buat

## Pertanyaan Reflektif
1. Iya, saya sengaja menggunakan `<section>`, `<article>`, dan `<aside>` supaya struktur
HTML-nya lebih jelas dan gampang dibaca. Menurut saya elemen tersebut cukup membantu untuk
membedakan bagian-bagian di website, misalnya section untuk bagian Skills atau Interests.
Jadi bukan cuma pakai `<div>` semua. Selain itu menurut saya juga lebih rapih kalau nanti
mau dikembangin lagi.

2. Tantangan yang saya temui paling banyak di bagian responsive, terutama waktu ngatur grid
Skills dan bagian Interests. Di desktop kelihatan enak kalau dibuat beberapa kolom, tapi
pas masuk mobile ukurannya jadi terlalu sempit. Jadi saya ubah jumlah kolomnya dan beberapa
elemen dibuat jadi satu kolom supaya lebih gampang dibaca. Untuk posisi elemen, saya lebih
ngikutin mana yang paling penting untuk dilihat dulu di mobile, terutama bagian hero dan
informasi utama. Kadang harus coba-coba ukuran dan spacing-nya juga sampai dapat yang pas.

3. Karena website ini masih static web, keterbatasannya adalah data dan isi website masih
harus diubah langsung dari kode. Jadi belum bisa ada interaksi yang benar-benar dinamis,
misalnya data user, login, atau data yang tersimpan di database. Untuk iterasi selanjutnya
saya paling ingin menambahkan fitur yang berhubungan dengan Assignment 2, terutama
menggunakan Django dan MVT supaya data di website bisa diambil dari database dan tidak
semuanya ditulis secara static di HTML.

### Tugas 2

## AI Disclosure
- Tools yang digunakan: ChatGPT dan Claude
- Strategi prompting: Saya mencari sumber youtube yang membahas lebih dalam, tentang materi
saat ini. Saya pelajarin, dan bertanya tanya apa maksud dari istilah tertentu. Setelahnya,
saya mulai menulis kode sendiri tanpa bantuan AI, dan meminta AI mengoreksi apakah sudah benar.
Hasil koreksiannya, lalu saya tulis ke kode saya dan saya koreksi ulang.
- Bagian yang dibantu AI: Materi yang saya masih tidak mengerti dan pahami, lalu kalimat
yang saya gunakan (seperti README), serta koreksi kode yang sudah saya buat
- Data konten: Data project (nama, deskripsi, teknologi, tahun, link) berasal dari project
nyata yang sudah saya kerjakan, bukan hasil karangan AI

## Pertanyaan Reflektif
1. Saat user membuka `/project/`, request masuk ke `urls.py` milik project, lalu diteruskan
ke `urls.py` milik aplikasi `main`. Dari situ, URL yang cocok akan memanggil view
`show_project`. View mengambil seluruh data `Project` dari model, memasukkannya ke dalam
context, lalu meneruskannya ke template `project.html`. Template kemudian melakukan
perulangan atas data tersebut dan hasil render HTML-nya dikirim kembali ke browser.

2. Menurut saya lebih baik disimpan di model karena datanya jadi lebih terstruktur dan gampang
diubah. Kalau ditulis langsung di template, nanti kalau project-nya banyak bakal susah
maintenance karena harus edit satu-satu di kode HTML.

3. `makemigrations` digunakan untuk membuat file migration berdasarkan perubahan pada model,
sedangkan `migrate` digunakan untuk menerapkan perubahan tersebut ke database. Contohnya
saat saya menambahkan model `Project`, saya perlu menjalankan `makemigrations` lalu
`migrate` supaya tabel `Project` dibuat di database.

### Tugas 3

## AI Disclosure
- Tools yang digunakan: ChatGPT dan Claude
- Strategi prompting: Saya mencari sumber youtube yang membahas lebih dalam, tentang materi
saat ini. Saya pelajarin, dan bertanya tanya apa maksud dari istilah tertentu. Setelahnya,
saya mulai menulis kode sendiri tanpa bantuan AI, dan meminta AI mengoreksi apakah sudah benar.
Hasil koreksiannya, lalu saya tulis ke kode saya dan saya koreksi ulang.
- Bagian yang dibantu AI: Materi yang saya masih tidak mengerti dan pahami, lalu kalimat
yang saya gunakan (seperti README), serta koreksi kode yang sudah saya buat
- Data konten: Data project (nama, deskripsi, teknologi, tahun, link) berasal dari project
nyata yang sudah saya kerjakan, bukan hasil karangan AI
- Claude sempat menyarankan menghapus data Experience lama untuk mengatasi prompt migrasi
`auto_now_add` — ternyata itu **tidak menyelesaikan masalah** karena Django tetap butuh
default value walaupun tabelnya kosong. Solusi yang benar (`1` → `timezone.now`) baru
keluar setelah saya lapor bahwa prompt masih muncul. Ini pelajaran: AI kadang percaya
diri dengan solusi yang salah, dan saya sebagai pengguna harus tetap kritis + memberi
feedback ketika sarannya tidak bekerja.
- Beberapa perubahan file (misalnya `urls.py`) sempat tidak tersimpan di editor saya, tapi
saya sempat lupa itu dan menyalahkan kodenya. Setelah dicek pakai `type main\urls.py`,
ternyata memang buffer VS Code-nya belum ke-save. Dari sini saya belajar untuk selalu
memverifikasi file di disk, bukan sekadar tampilan di editor.

## Pertanyaan Reflektif

1. `ModelForm` itu praktis banget karena Django langsung baca field dari model, jadi
saya tidak perlu tulis satu-satu `<input>` di HTML. Validasinya juga otomatis sesuai
tipe field, misalnya `URLField` bakal nolak input yang bukan URL, dan `form.save()`
bisa langsung simpan ke database dalam satu baris. Kalau bikin form HTML manual,
semua konversi tipe, validasi, sampai penyimpanan harus diurus sendiri, dan kalau
modelnya berubah harus edit HTML-nya juga. Untuk `{% csrf_token %}`, itu buat mencegah serangan CSRF. 
Jadi kalau ada website lain yang coba kirim request POST ke aplikasi saya diam-diam pakai 
session user yang lagi login, request-nya bakal ditolak karena token-nya tidak cocok. 
Django menyisipkan token unik per session, dan situs jahat tidak tahu isinya, jadi request 
palsu langsung ke-block dengan 403.

2. JSON lebih ringkas dan lebih gampang dibaca. Dia tidak butuh tag pembuka-penutup
seperti XML, jadi ukuran datanya lebih kecil. Selain itu JSON juga native di JavaScript
(tinggal `JSON.parse()`) dan struktur datanya mirip banget sama `dict` di Python atau
object di JS, jadi konversinya hampir gratis. XML masih dipakai di beberapa sistem
lama atau yang butuh metadata rumit, tapi untuk API web sekarang JSON jauh lebih
praktis.

3. Waktu user buka `/api/experience/`, request masuk ke `urls.py`, dipetakan ke view
`get_experience_json`. View ambil data pakai `Experience.objects.all()`, terus
di-serialize jadi string JSON pakai `django.core.serializers.serialize`, lalu
dibungkus dalam `HttpResponse` dengan `content_type="application/json"` dan dikirim
balik. Serialization perlu karena objek `Experience` itu objek Python yang punya method
dan referensi ke database, sedangkan HTTP cuma bisa kirim teks. Jadi objeknya harus
diubah dulu jadi struktur data sederhana (dict, list, string, number) yang bisa
ditulis sebagai JSON dan dibaca sama siapa aja — browser, aplikasi mobile, atau
program lain.

### Tugas 4

## AI Disclosure
- Tools yang digunakan: ChatGPT dan Claude 
- Strategi prompting: Saya mengupload file tugas ke-4 ke ChatGPT, dan memintanya memberikan garis 
besar langkah-langkah pengerjaan, dari awal sampai akhir. Setelahnya saya membaca satu per satu, 
langkah-langkah yang diberikan ChatGPT, lalu menanyakan langkah yang saya masih bingung ke ChatGPT.
ChatGPT kemudian menjelaskan bagian bagian yang saya tidak pahamin. Setelahnya, saya mulai mengerjakan
kode-kode program saya, dan menanyakan apakah sudah benar atau tidak ke Claude. Claude akan memberikan
kode yang lebih efisien dan lebih baik kepada saya. Setelahnya saya akan menganalisa kembali kode-kodenya
lalu menuliskan ulang tanpa copy paste secara langsung.
- Bagian yang dibantu AI: CSS badge peran, pengecekan otomatis lewat Django test client
(4 peran, kode status 302/403/200), test Selenium di `test_e2e.py`, dan draft README ini.
- Bagian yang saya kerjakan sendiri: Bagian `permissions.py` dan `context_processors.py`, penyesuaian
guard pada `views.py`, halaman `starred.html`, membuat akun superuser, membuat Group `Editor` dan
memasukkan user ke dalamnya lewat Django Admin, menguji alur di browser, serta memutuskan mana saran 
AI yang dipakai dan mana yang dibuang.
- Data konten: Data project dan Experience tetap berasal dari pekerjaan saya sendiri, bukan hasil
karangan AI.
- Saya sempat meminta perbaikan tampilan navbar. Claude merekomendasikan beberapa opsi yang kompleks, 
tapi saya tidak jadi menggunakannya.


### Tugas 5

1. **Debouncing** adalah teknik menunda pemanggilan sebuah fungsi sampai event berhenti terjadi selama jeda tertentu. Setiap event baru membatalkan timer lama dan memulai hitungan dari awal, jadi fungsi hanya berjalan sekali setelah pengguna diam. Pada pencarian AJAX, tanpa debouncing setiap ketukan tombol mengirim satu request: mengetik `backend` berarti tujuh request ke server dan tujuh query ke database, padahal yang dibutuhkan hanya hasil untuk kata terakhir. Debouncing memangkas beban server dan database, menghemat kuota pengguna, dan mengurangi tampilan yang berkedip. Di halaman Experience saya memakai jeda 400 ms lewat helper `debounce()` di `static/js/utils.js`. Tombol Enter membatalkan timer dan langsung mencari, dan `AbortController` membatalkan request lama yang masih berjalan sehingga hasil lama tidak menimpa hasil baru.
```javascript
   const debouncedSearch = debounce(() => loadPage({ reset: true }), 400);
   searchInput.addEventListener('input', debouncedSearch);
```

2. `fetch()` tidak langsung mengembalikan data, melainkan sebuah **Promise** yang baru selesai setelah server membalas. `await` (hanya bisa dipakai di dalam fungsi `async`) menghentikan sementara eksekusi fungsi itu sampai Promise selesai, lalu mengembalikan nilainya, yaitu objek `Response`. `response.json()` juga mengembalikan Promise, jadi butuh `await` kedua. Tanpa `await`, variabel berisi Promise yang masih *pending*, bukan data. Akibatnya `response.ok` bernilai `undefined`, `response.json()` gagal karena Promise tidak punya method itu, kode di bawahnya berjalan sebelum data tiba, dan error dari request yang gagal tidak tertangkap oleh `try/catch` di sekitarnya (menjadi *unhandled rejection*).
```javascript
   const response = fetch(url);        // Promise { <pending> }
   console.log(response.ok);           // undefined
   response.json();                    // TypeError: response.json is not a function

   const ok = await fetch(url);        // Response
   const data = await ok.json();       // objek JSON
```

3. **XSS (Cross-Site Scripting)** adalah serangan ketika penyerang berhasil menyisipkan kode JavaScript ke halaman, lalu kode itu dijalankan di browser pengguna lain. Jenis yang paling berbahaya adalah *stored XSS*: payload seperti `<img src="x" onerror="alert('XSS!')">` disimpan di database dan berjalan setiap kali data itu ditampilkan. Karena berjalan di halaman kita sendiri, skrip penyerang bisa membaca cookie `csrftoken` dan mengirim request atas nama korban, sehingga perlindungan CSRF ikut tidak berguna.

   Template Django melakukan **auto-escaping** secara default: `{{ experience.title }}` mengubah `<` menjadi `&lt;`, sehingga payload tampil sebagai teks. Saat data ditampilkan lewat JavaScript, Django tidak lagi terlibat. Developer sendiri yang memasukkan data ke DOM, dan kalau itu dilakukan lewat `innerHTML` atau penggabungan string, browser mem-parse data sebagai HTML sungguhan. Tidak ada escaping otomatis, jadi tanggung jawabnya pindah ke developer.
```javascript
   card.innerHTML = `<h2>${item.title}</h2>`;    // rentan: payload dieksekusi
   const h2 = document.createElement('h2');
   h2.textContent = item.title;                   // aman: selalu teks
```
   Pencegahan yang saya terapkan: (a) di klien, kartu Experience dibangun dengan `createElement` + `textContent` tanpa `innerHTML`, sedangkan halaman Projects memakai `escapeHtml()`. (b) Di server, `ExperienceForm` membersihkan `title`, `company`, dan `description` dengan `strip_tags` di method `clean_<field>`, dan menolak nilai yang kosong setelah dibersihkan, sehingga payload di atas dibalas `400`. (c) `URLField` menolak skema `javascript:`.

## AI Disclosure

- **Tools:** Claude (Anthropic). 
- **Strategi prompting:** Saya menulis prompt terstruktur berisi peran, konteks proyek, aturan kerja, rincian tiap commit, standar kualitas, dan permintaan tabel verifikasi akhir. 
- **Bagian yang dibantu AI:** `static/js/utils.js`, `static/js/experience.js`, view JSON dan AJAX di `main/views.py`, `clean_*` di `ExperienceForm`, template dan modal Experience, CSS tambahan, serta draft README ini.


### Tugas 6

**Bagian yang dikerjakan:** Experience, dengan model dan data yang sudah ada sejak Tugas 3. API-nya ada di `/api/v1/experiences/`, di samping API Projects dari Tutorial 07.

| Method | Endpoint | Visitor | Member | Editor | Owner |
|---|---|:-:|:-:|:-:|:-:|
| `GET` | `/api/v1/experiences/?title=...&page=...` | ✓ | ✓ | ✓ | ✓ |
| `POST` | `/api/v1/experiences/` | 403 | 403 | 403 | 201 |
| `GET` | `/api/v1/experiences/<uuid>/` | ✓ | ✓ | ✓ | ✓ |
| `PUT` / `PATCH` | `/api/v1/experiences/<uuid>/` | 403 | 403 | 200 | 200 |
| `DELETE` | `/api/v1/experiences/<uuid>/` | 403 | 403 | 403 | 204 |
| `POST` | `/api/v1/experiences/<uuid>/star/` | 403 | 200 | 200 | 200 |

**Ringkasan perubahan:**
- `ExperienceSerializer` dengan `fields` eksplisit, `star_count`/`is_starred` read-only, `validate_title`/`validate_description` memakai `strip_tags`, dan `validate()` untuk memastikan tanggal selesai tidak mendahului tanggal mulai (termasuk saat `PATCH` sebagian).
- `IsPortfolioOwnerOrEditorOrReadOnly` memakai helper `is_owner`/`is_editor` yang sama dengan view HTML, jadi aturan peran hanya didefinisikan sekali.
- Daftar memakai `PageNumberPagination` (5 per halaman) supaya tombol "Muat lebih banyak" dari Tugas 5 tetap ada; frontend tinggal mengikuti link `next`. Jumlah star dan status star dihitung dengan `annotate(Count(...), Exists(...))` sehingga satu halaman cukup satu query, bukan satu query per kartu.
- Halaman Experience sekarang menampilkan, mencari, menambah, mengedit (`PATCH` hanya field yang berubah, lewat modal yang sama dengan tambah), memberi star, dan menghapus lewat API tanpa reload. Error `400` muncul di bawah input dan di toast, `403` di toast.
- Endpoint JSON lama (`/api/experience/`, `/experience/add-ajax/`, `/experience/<id>/star/`) dihapus supaya hanya ada satu jalur. Ini sekaligus memperbaiki bug Tugas 5: kode lama memakai field `company` yang tidak ada di model, sehingga daftar Experience selalu gagal dimuat.
- Empat test lama di `main/tests.py` disesuaikan karena halaman Projects sudah dirender lewat JavaScript; isinya sekarang dicek lewat API.

**Menjalankan:**
```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py test main      # bukan "test" saja, supaya test_e2e.py (Selenium) tidak ikut
python manage.py runserver      # lalu buka /experience/ dan /api/v1/experiences/
```

1. **REST** (*Representational State Transfer*) adalah gaya arsitektur untuk merancang API, bukan format data atau library. Data diperlakukan sebagai *resource* yang punya alamat (`/api/v1/experiences/` untuk kumpulan, `/api/v1/experiences/<uuid>/` untuk satu item), HTTP method menyatakan tindakannya (`GET` membaca, `POST` membuat, `PUT`/`PATCH` mengubah, `DELETE` menghapus), dan klien serta server bertukar *representasi* data. Mengembalikan JSON saja belum cukup. Endpoint seperti `POST /experience/add-ajax/` atau `POST /project/5/delete/` memang membalas JSON, tetapi tindakannya ditulis di URL dan semuanya memakai `POST`, jadi method dan status code tidak punya arti yang konsisten. API yang RESTful juga memakai status code yang tepat (`201`, `204`, `400`, `403`, `404`) dan idealnya stateless. Proyek saya tidak sepenuhnya stateless karena memakai session, dan itu wajar untuk AJAX di website yang sama.

   **PUT** mengganti seluruh representasi resource, jadi semua field wajib harus dikirim; `PUT` yang hanya berisi `title` dibalas `400`. **PATCH** hanya mengirim field yang ingin diubah, dan field lain tetap (`partial=True` di serializer). `PUT` cocok ketika klien memang memegang data lengkap, misalnya form edit penuh atau sinkronisasi data dari sistem lain. `PATCH` cocok untuk perubahan kecil, misalnya Editor hanya membetulkan judul. Modal edit saya memakai `PATCH` dan hanya mengirim field yang berubah, sehingga perubahan orang lain pada field lain tidak ikut tertimpa.

2. **Serializer** adalah kontrak antara model dan JSON yang bekerja dua arah. Saat membaca, serializer mengubah objek `Experience` menjadi data Python yang siap dirender ke JSON. Saat menulis, serializer menerima `request.data`, memvalidasinya per field (`validate_title`) dan lintas field (`validate`), lalu `save()` memanggil `create()` atau `update()`. Dibandingkan merakit dictionary manual dengan `JsonResponse`, keuntungannya: (a) satu definisi `fields` dipakai untuk list, detail, create, dan update, sehingga tidak ada dictionary yang tertinggal saat model berubah (bug `company` di Tugas 5 terjadi persis karena dictionary manual tidak ikut berubah); (b) validasi tipe, `choices`, `URLField`, dan `required` otomatis diambil dari model; (c) error `400` keluar dalam bentuk seragam `{"field": ["pesan"]}`; (d) `read_only_fields` dan `SerializerMethodField` membuat field seperti `id` dan `star_count` tidak bisa dipalsukan klien; (e) Browsable API ikut tersedia.

3. **Autentikasi** menjawab "siapa kamu": `SessionAuthentication` membaca cookie session lalu mengisi `request.user`. **Otorisasi** menjawab "boleh melakukan apa": permission class seperti `IsPortfolioOwnerOrEditorOrReadOnly` memutuskan apakah request boleh diteruskan, dan dijalankan sebelum isi view. Menyembunyikan tombol di template hanya mengatur tampilan. Siapa pun tetap bisa mengirim request langsung lewat `fetch()` di Console, `curl`, atau Browsable API tanpa pernah melihat tombolnya. Karena itu aturan harus ditegakkan di server. Saya membuktikannya dengan test: Member yang mengirim `PATCH` mendapat `403`, dan isi database dicek tetap sama. Saat permission saya ubah sementara supaya semua akun login boleh menulis, test itu gagal.

4. Dengan `SessionAuthentication`, browser **otomatis** mengirim cookie session ke domain kita, termasuk ketika request dipicu oleh situs lain (misalnya form tersembunyi di situs jahat yang mengirim `DELETE` atau `POST` ke portofolio saya). Cookie saja tidak bisa membedakan request asli dari request palsu. Token CSRF bisa membedakannya karena situs lain tidak dapat membaca token itu dari halaman atau cookie kita. Karena itu DRF memeriksa CSRF untuk setiap `POST`/`PUT`/`PATCH`/`DELETE` dari pengguna yang login lewat session, dan frontend saya selalu mengirim header `X-CSRFToken`. `force_authenticate` melewati seluruh proses autentikasi: user langsung "ditempelkan" ke request tanpa session dan tanpa pemeriksaan CSRF, sehingga test yang memakainya akan lulus walaupun perlindungan CSRF rusak. Untuk membuktikan CSRF berjalan, test saya memakai `APIClient(enforce_csrf_checks=True)` dan `.login()` agar ada session sungguhan. `PATCH` dan star tanpa token ditolak `403` (database dicek tidak berubah), sedangkan `PATCH` dengan token dari cookie halaman Experience berhasil.

## AI Disclosure

- **Bagian yang dibantu AI:** `ExperienceSerializer`, `IsPortfolioOwnerOrEditorOrReadOnly`, dan draft README ini.
- **Keterbatasan AI dan hal yang saya periksa:** Claude menemukan bahwa kode Tugas 5 (yang juga dibuat dengan bantuan AI) memakai field `company` yang tidak pernah ada di model. Bug ini lolos karena tidak ada test untuk endpoint JSON Experience. 