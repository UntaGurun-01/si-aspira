from flask import Blueprint, render_template
from flask_login import login_required
from ..models import Complaint

category_bp = Blueprint('category', __name__)


@category_bp.route('/categories')
@login_required
def index():
    # Hitung jumlah pengaduan per kategori untuk statistik visual
    categories = [
        {
            'key': 'akademik',
            'name': 'Akademik',
            'icon': 'bi-book-half',
            'color': '#3b82f6',
            'bg_light': 'rgba(59, 130, 246, 0.1)',
            'border_color': 'rgba(59, 130, 246, 0.3)',
            'desc': 'Permasalahan terkait jadwal perkuliahan, pengisian KRS, nilai mata kuliah, transkrip, proses remedial, dan kegiatan akademik lainnya.',
            'scopes': [
                'Jadwal kuliah atau ujian bentrok / perubahan mendadak',
                'Kendala pengisian dan validasi KRS oleh dosen PA',
                'Keterlambatan input nilai KHS atau nilai remedial',
                'Prosedur cuti kuliah dan semester pendek (SP)'
            ],
            'example': 'Nilai mata kuliah Pemrograman Web belum diinput ke portal, padahal sudah mengikuti UAS dan remedial.'
        },
        {
            'key': 'dosen',
            'name': 'Dosen & Pengajaran',
            'icon': 'bi-person-video3',
            'color': '#8b5cf6',
            'bg_light': 'rgba(139, 92, 246, 0.1)',
            'border_color': 'rgba(139, 92, 246, 0.3)',
            'desc': 'Kendala yang berkaitan dengan pelaksanaan proses pembelajaran di kelas serta kelancaran komunikasi akademik antara dosen dan mahasiswa.',
            'scopes': [
                'Kehadiran dan kedisiplinan dosen dalam proses belajar-mengajar',
                'Kesesuaian materi perkuliahan dengan silabus / RPS',
                'Kejelasan kriteria penilaian tugas, kuis, dan ujian',
                'Komunikasi pembimbingan akademik, proposal, dan skripsi'
            ],
            'example': 'Dosen pengampu tidak hadir dalam perkuliahan berturut-turut tanpa pemberitahuan atau jadwal kelas pengganti.'
        },
        {
            'key': 'fasilitas',
            'name': 'Fasilitas & Laboratorium',
            'icon': 'bi-cpu-fill',
            'color': '#06b6d4',
            'bg_light': 'rgba(6, 182, 212, 0.1)',
            'border_color': 'rgba(6, 182, 212, 0.3)',
            'desc': 'Kerusakan atau kendala sarana ruang kelas, laboratorium komputer praktikum informatika, serta infrastruktur teknologi pendukung.',
            'scopes': [
                'Komputer, monitor, dan periferal Lab Komputer bermasalah',
                'Jaringan internet (Wi-Fi kampus atau LAN praktikum) lambat/putus',
                'Fasilitas ruang kuliah (AC rusak, proyektor LCD buram/mati)',
                'Perangkat keras praktikum robotika / IoT dan lisensi software'
            ],
            'example': 'Beberapa PC di Lab Rekayasa Perangkat Lunak sering restart sendiri saat praktikum pemrograman berlangsung.'
        },
        {
            'key': 'administrasi',
            'name': 'Administrasi',
            'icon': 'bi-file-earmark-text-fill',
            'color': '#10b981',
            'bg_light': 'rgba(16, 185, 129, 0.1)',
            'border_color': 'rgba(16, 185, 129, 0.3)',
            'desc': 'Kendala layanan tata usaha, permohonan persuratan resmi, dan administrasi akademik pada Program Studi Teknik Informatika.',
            'scopes': [
                'Pengurusan Surat Keterangan Aktif Kuliah mahasiswa',
                'Penerbitan Surat Pengantar Kerja Praktik (KP / Magang)',
                'Administrasi pendaftaran Seminar Proposal dan Sidang Skripsi',
                'Legalisasi dokumen akademik dan surat rekomendasi prodi'
            ],
            'example': 'Pengajuan surat pengantar magang di instansi belum selesai diproses setelah lebih dari 5 hari kerja.'
        },
        {
            'key': 'saran',
            'name': 'Saran & Kritik',
            'icon': 'bi-lightbulb-fill',
            'color': '#f59e0b',
            'bg_light': 'rgba(245, 158, 11, 0.1)',
            'border_color': 'rgba(245, 158, 11, 0.3)',
            'desc': 'Masukan konstruktif, kritik membangun, serta ide inovatif untuk meningkatkan kualitas layanan dan kegiatan kemahasiswaan prodi.',
            'scopes': [
                'Usulan workshop / pelatihan teknologi terbaru (AI, Cloud, Cyber)',
                'Saran perbaikan alur birokrasi dan keterbukaan informasi prodi',
                'Ide kegiatan perlombaan atau seminar internal mahasiswa TI',
                'Masukan peningkatan kualitas kurikulum sesuai kebutuhan industri'
            ],
            'example': 'Usulan mengadakan pelatihan persiapan sertifikasi Cloud Computing bagi mahasiswa tingkat akhir.'
        },
        {
            'key': 'lainnya',
            'name': 'Lainnya',
            'icon': 'bi-question-circle-fill',
            'color': '#ec4899',
            'bg_light': 'rgba(236, 72, 153, 0.1)',
            'border_color': 'rgba(236, 72, 153, 0.3)',
            'desc': 'Laporan, pertanyaan, atau permasalahan relevan lainnya yang belum tercakup secara khusus pada kategori utama di atas.',
            'scopes': [
                'Ketertiban dan kenyamanan di lingkungan gedung kampus',
                'Permasalahan area parkir kendaraan mahasiswa',
                'Kebersihan fasilitas umum kampus di sekitar prodi',
                'Laporan umum non-akademik yang membutuhkan perhatian prodi'
            ],
            'example': 'Kendaraan mahasiswa sering terhalang keluar akibat penataan parkir di depan gedung TI yang tidak teratur.'
        }
    ]

    # Hitung total pengaduan di sistem untuk info counter
    for cat in categories:
        cat['count'] = Complaint.query.filter_by(category=cat['key']).count()

    return render_template('categories/index.html', categories=categories)
