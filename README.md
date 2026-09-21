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
modelnya berubah harus edit HTML-nya juga.

Untuk `{% csrf_token %}`, itu buat mencegah serangan CSRF. Jadi kalau ada website
lain yang coba kirim request POST ke aplikasi saya diam-diam pakai session user yang
lagi login, request-nya bakal ditolak karena token-nya tidak cocok. Django menyisipkan
token unik per session, dan situs jahat tidak tahu isinya, jadi request palsu langsung
ke-block dengan 403.

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
balik.

Serialization perlu karena objek `Experience` itu objek Python yang punya method
dan referensi ke database, sedangkan HTTP cuma bisa kirim teks. Jadi objeknya harus
diubah dulu jadi struktur data sederhana (dict, list, string, number) yang bisa
ditulis sebagai JSON dan dibaca sama siapa aja — browser, aplikasi mobile, atau
program lain.