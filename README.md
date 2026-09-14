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