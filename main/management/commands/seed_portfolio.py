"""Fill the portfolio with sample experiences and projects.

Run it with ``python manage.py seed_portfolio`` (locally, or from the PWS
Terminal tab). Entries are matched by title, so running it again adds nothing
and never changes data that already exists, including edits made on the site.
"""

from datetime import date

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from main.models import Experience, Project
from main.permissions import EDITOR_GROUP_NAME

EXPERIENCES = [
    {
        "title": "Kepala Biro MDC @ FUKI FASILKOM UI",
        "description": (
            "Memimpin Biro Media, Design & Communication (MDC) FUKI Fasilkom UI yang "
            "beranggotakan 12 staf. Menyusun kalender konten bulanan, meninjau setiap desain "
            "sebelum terbit, dan menjaga konsistensi identitas visual FUKI di media sosial."
        ),
        "category": "volunteer",
        "started_at": date(2026, 1, 5),
        "ended_at": None,
    },
    {
        "title": "Vice Person in Charge Sponsorship @ COMPFEST",
        "description": (
            "Melanjutkan peran di tim sponsorship COMPFEST sebagai wakil penanggung jawab. "
            "Mengoordinasikan delapan staf, menyusun paket sponsor berjenjang, dan memantau "
            "progres kerja sama dengan lebih dari 30 calon sponsor hingga acara selesai."
        ),
        "category": "volunteer",
        "started_at": date(2026, 2, 1),
        "ended_at": date(2026, 10, 31),
    },
    {
        "title": "Research Assistant @ Lab MLCV Fasilkom UI",
        "description": (
            "Membantu riset klasifikasi teks berbahasa Indonesia di Lab Machine Learning & "
            "Computer Vision. Membersihkan dan melabeli data ulasan aplikasi, lalu menjalankan "
            "eksperimen perbandingan model klasik dan model berbasis transformer."
        ),
        "category": "research",
        "started_at": date(2026, 2, 2),
        "ended_at": date(2026, 6, 30),
    },
    {
        "title": "Web Developer @ PT. Kharisma Cipta Kreasi",
        "description": (
            "Merawat website perusahaan setelah diluncurkan dan membangun dashboard internal "
            "untuk memantau titik reklame beserta status sewanya. Menangani perbaikan bug, "
            "pembaruan konten, dan permintaan fitur dari tim pemasaran."
        ),
        "category": "part-time",
        "started_at": date(2025, 9, 1),
        "ended_at": None,
    },
    {
        "title": "Asisten Dosen Dasar-Dasar Pemrograman 1 @ Fasilkom UI",
        "description": (
            "Mendampingi satu kelas lab DDP 1 berisi 30 mahasiswa baru. Menjawab pertanyaan "
            "saat lab Python, memeriksa tugas pemrograman mingguan, dan memberi umpan balik "
            "tertulis untuk setiap submisi."
        ),
        "category": "part-time",
        "started_at": date(2025, 8, 25),
        "ended_at": date(2025, 12, 19),
    },
    {
        "title": "Pengajar @ Bimbingan Belajar Gratis Fasilkom UI",
        "description": (
            "Mengajar matematika dasar untuk siswa SMA di sekitar kampus UI setiap Sabtu. "
            "Menyiapkan latihan soal, membahas materi yang belum dipahami, dan memantau "
            "perkembangan nilai siswa selama program berlangsung."
        ),
        "category": "volunteer",
        "started_at": date(2025, 9, 6),
        "ended_at": date(2025, 11, 29),
    },
    {
        "title": "Data Analyst Intern @ PT. Kharisma Cipta Kreasi",
        "description": (
            "Mengolah data sewa titik reklame tiga tahun terakhir menjadi laporan okupansi per "
            "lokasi. Membuat visualisasi dengan Excel dan Python yang dipakai tim pemasaran "
            "untuk menentukan lokasi yang perlu diprioritaskan."
        ),
        "category": "internship",
        "started_at": date(2025, 6, 2),
        "ended_at": date(2025, 8, 29),
    },
    {
        "title": "Freelance Web Developer @ PT. Kharisma Cipta Kreasi",
        "description": (
            "Membangun website company profile PT. Kharisma Cipta Kreasi bersama dua teman, "
            "mulai dari menyusun struktur halaman, membuat tampilan dengan Next.js, hingga "
            "menyiapkan domain dan deployment."
        ),
        "category": "freelance",
        "started_at": date(2025, 3, 3),
        "ended_at": date(2025, 7, 31),
    },
    {
        "title": "Freelance Web Developer @ Kedai Kopi Sudut Depok",
        "description": (
            "Membuat katalog menu online untuk kedai kopi lokal di Depok agar pelanggan bisa "
            "melihat menu dan harga sebelum memesan lewat WhatsApp. Halamannya dibuat "
            "responsif dan ringan supaya cepat dibuka di ponsel."
        ),
        "category": "freelance",
        "started_at": date(2025, 1, 6),
        "ended_at": date(2025, 2, 14),
    },
    {
        "title": "Freelance Web Developer @ PT. Graha Arcadia Raya",
        "description": (
            "Membangun website PT. Graha Arcadia Raya dari desain sampai rilis. Bekerja "
            "langsung dengan tim pemasaran untuk menyusun konten halaman dan memastikan "
            "informasi kontak serta penawaran mudah ditemukan calon klien."
        ),
        "category": "freelance",
        "started_at": date(2024, 9, 2),
        "ended_at": date(2024, 12, 20),
    },
    # The five entries below already exist on the site; they are listed so a
    # fresh database (for example on PWS) gets the full portfolio too.
    {
        "title": "Staff MDC @ FUKI FASILKOM UI",
        "description": (
            "Bergabung dalam divisi Media, Design & Communication (MDC) FUKI Fasilkom UI, "
            "membantu produksi konten publikasi, materi visual untuk kegiatan kerohanian, serta "
            "pengelolaan komunikasi ke warga Fasilkom melalui berbagai kanal media sosial."
        ),
        "category": "volunteer",
        "started_at": date(2025, 1, 1),
        "ended_at": date(2025, 12, 31),
    },
    {
        "title": "Staff Penunjang @ SIWAKNG",
        "description": (
            "Mendukung kelancaran operasional acara SIWAKNG 2025 (Silaturahmi Warga Kampung UI), "
            "termasuk membantu persiapan teknis di lapangan, koordinasi antar-divisi, dan "
            "memastikan setiap rangkaian acara berjalan sesuai rundown yang direncanakan."
        ),
        "category": "volunteer",
        "started_at": date(2025, 1, 1),
        "ended_at": date(2025, 12, 31),
    },
    {
        "title": "Staff Sponsorship @ COMPFEST",
        "description": (
            "Bagian dari tim yang menjaring dukungan sponsor untuk COMPFEST, event teknologi "
            "tahunan terbesar mahasiswa Fasilkom UI. Terlibat dalam penyusunan proposal, riset "
            "calon sponsor, serta menjalin komunikasi dan negosiasi dengan perusahaan untuk "
            "mengamankan kerja sama."
        ),
        "category": "volunteer",
        "started_at": date(2025, 1, 1),
        "ended_at": date(2025, 12, 31),
    },
    {
        "title": "Marketing @ PT. Graha Arcadia Raya",
        "description": (
            "Menangani strategi pemasaran dan pengembangan relasi klien, termasuk penyusunan "
            "materi promosi, riset kebutuhan pasar, dan follow-up prospek hingga tahap "
            "penawaran. Aktif menjembatani komunikasi antara tim internal dan klien untuk "
            "memastikan penawaran yang tepat sasaran."
        ),
        "category": "full-time",
        "started_at": date(2024, 4, 22),
        "ended_at": None,
    },
    {
        "title": "Tax Officer @ PT. Kharisma Cipta Kreasi",
        "description": (
            "Mengelola administrasi perpajakan perusahaan mulai dari perhitungan PPN dan PPh, "
            "penyusunan SPT bulanan & tahunan, hingga pelaporannya melalui sistem DJP Online. "
            "Membantu menjaga kepatuhan pajak perusahaan tetap tepat waktu dan sesuai regulasi "
            "yang berlaku."
        ),
        "category": "full-time",
        "started_at": date(2020, 1, 1),
        "ended_at": None,
    },
]

PROJECTS = [
    {
        "title": "Website PT. Kharisma Cipta Kreasi",
        "description": "Saya membuat website PT. Kharisma Cipta Kreasi bersama dua teman saya",
        "tech_stack": "HTML, CSS, NextJS",
        "year": 2025,
        "url": "https://www.kharismacipta.com/",
    },
    {
        "title": "Website PT. Graha Arcadia Raya",
        "description": "Saya membuat website untuk PT. Graha Arcadia Raya",
        "tech_stack": "HTML, CSS, NextJS",
        "year": 2024,
        "url": "https://www.arcadiaraya.com/",
    },
    {
        "title": "MyPortfolio",
        "description": (
            "Website portofolio pribadi yang saya kembangkan sepanjang mata kuliah PBP: halaman "
            "Experience dan Projects, autentikasi dengan peran Owner, Editor, dan Member, AJAX, "
            "HTMX, serta REST API dengan Django REST Framework."
        ),
        "tech_stack": "Django, Django REST Framework, HTMX, JavaScript",
        "year": 2026,
        "url": "https://github.com/muhrayyan43/myportofolio",
    },
    {
        "title": "MyPortfolio Mobile",
        "description": (
            "Aplikasi Flutter pendamping MyPortfolio yang membaca dan menambah data lewat API "
            "Django dengan autentikasi token, dilengkapi CI/CD GitHub Actions yang menghasilkan "
            "APK."
        ),
        "tech_stack": "Flutter, Dart, Provider, GitHub Actions",
        "year": 2026,
        "url": "https://github.com/muhrayyan43/myportofolio_mobile",
    },
    {
        "title": "PilihYuk",
        "description": (
            "Proyek kelompok PBP berupa aplikasi web dan mobile. Saya mengerjakan modul Antrean "
            "Data, tempat koreksi data dari pengguna diantrekan dan ditinjau sebelum diterapkan."
        ),
        "tech_stack": "Django, Flutter, PostgreSQL",
        "year": 2026,
        "url": None,
    },
    {
        "title": "Analisis Pola Mobilitas Rumah Tangga",
        "description": (
            "Tugas kelompok analisis data: membersihkan dataset perjalanan dan mobilitas rumah "
            "tangga, lalu mengelompokkan pola perjalanan dengan K-Means dan menafsirkan "
            "karakteristik tiap klaster."
        ),
        "tech_stack": "Python, pandas, scikit-learn, Jupyter",
        "year": 2026,
        "url": None,
    },
    {
        "title": "Klasifikasi Sentimen Ulasan Aplikasi",
        "description": (
            "Membandingkan TF-IDF dengan Logistic Regression dan model transformer untuk "
            "mengklasifikasikan sentimen ulasan aplikasi berbahasa Indonesia, sebagai bagian "
            "dari riset di Lab MLCV."
        ),
        "tech_stack": "Python, scikit-learn, Hugging Face Transformers",
        "year": 2026,
        "url": None,
    },
    {
        "title": "Sistem Peminjaman Ruangan Kampus",
        "description": (
            "Proyek mata kuliah Basis Data: merancang skema relasional, menulis query dan "
            "trigger untuk mencegah jadwal bentrok, lalu menghubungkannya ke antarmuka web "
            "sederhana."
        ),
        "tech_stack": "PostgreSQL, SQL, Django",
        "year": 2026,
        "url": None,
    },
    {
        "title": "Dashboard Titik Reklame PT. Kharisma Cipta Kreasi",
        "description": (
            "Dashboard internal yang menampilkan lokasi titik reklame di peta beserta status "
            "sewa dan masa kontraknya, sehingga tim pemasaran bisa melihat titik yang kosong "
            "dalam satu layar."
        ),
        "tech_stack": "Django, PostgreSQL, Leaflet, Chart.js",
        "year": 2025,
        "url": None,
    },
    {
        "title": "Otomasi Rekap Pajak Bulanan",
        "description": (
            "Skrip yang menggabungkan data faktur bulanan menjadi rekap PPN dan PPh dalam "
            "format Excel, sehingga penyusunan SPT bulanan tidak lagi dikerjakan manual."
        ),
        "tech_stack": "Python, pandas, openpyxl",
        "year": 2025,
        "url": None,
    },
    {
        "title": "Website Pendaftaran Kegiatan FUKI",
        "description": (
            "Halaman pendaftaran kegiatan FUKI Fasilkom UI dengan formulir, kuota peserta, dan "
            "rekap pendaftar yang bisa diunduh panitia."
        ),
        "tech_stack": "Next.js, Tailwind CSS",
        "year": 2025,
        "url": None,
    },
    {
        "title": "Katalog Menu Online Kedai Kopi Sudut Depok",
        "description": (
            "Katalog menu statis dengan foto, harga, dan tombol pesan lewat WhatsApp, dibuat "
            "untuk kedai kopi lokal di Depok."
        ),
        "tech_stack": "HTML, CSS, JavaScript",
        "year": 2025,
        "url": None,
    },
    {
        "title": "Bot Pengingat Deadline Tugas",
        "description": (
            "Bot Telegram yang mengirim pengingat tenggat tugas kuliah ke grup angkatan "
            "berdasarkan jadwal yang diisi panitia akademik angkatan."
        ),
        "tech_stack": "Python, Telegram Bot API",
        "year": 2025,
        "url": None,
    },
]


def create_missing(model, rows):
    """Create every row whose title is not in the database yet; return how many."""
    existing_titles = set(model.objects.values_list("title", flat=True))
    created = 0
    for row in rows:
        if row["title"] not in existing_titles:
            model.objects.create(**row)
            created += 1
    return created


class Command(BaseCommand):
    help = "Add sample experiences and projects, plus the Editor group, without duplicates."

    @transaction.atomic
    def handle(self, *args, **options):
        _, group_created = Group.objects.get_or_create(name=EDITOR_GROUP_NAME)
        experiences = create_missing(Experience, EXPERIENCES)
        projects = create_missing(Project, PROJECTS)

        self.stdout.write(self.style.SUCCESS(
            f"Ditambahkan {experiences} experience dan {projects} project "
            "(judul yang sudah ada dilewati)."
        ))
        if group_created:
            self.stdout.write(f'Grup "{EDITOR_GROUP_NAME}" dibuat.')