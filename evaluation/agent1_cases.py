
CASES = [
    {
        "id": "M01",
        "category": "Single complete task",
        "notes": (
            "Rapat 9 November 2026. Maya meminta Andi "
            "memperbaiki API login paling lambat "
            "12 November 2026."
        ),
        "expected": [
            ("Memperbaiki API login", "Andi", "2026-11-12")
        ]
    },
    {
        "id": "M02",
        "category": "Multiple complete tasks",
        "notes": (
            "Rapat 9 November 2026. Andi ditugaskan "
            "memperbaiki login sebelum 12 November 2026. "
            "Budi harus menguji dashboard pada 13 November "
            "2026. Sinta bertanggung jawab merevisi "
            "desain laporan tanggal 14 November 2026."
        ),
        "expected": [
            ("Memperbaiki login", "Andi", "2026-11-12"),
            ("Menguji dashboard", "Budi", "2026-11-13"),
            ("Merevisi desain laporan", "Sinta", "2026-11-14")
        ]
    },
    {
        "id": "M03",
        "category": "Missing PIC",
        "notes": (
            "Rapat 9 November 2026. Tim menyepakati "
            "dokumentasi API perlu diperbarui sebelum "
            "15 November 2026, tetapi PIC belum ditentukan."
        ),
        "expected": [
            ("Memperbarui dokumentasi API", None, "2026-11-15")
        ]
    },
    {
        "id": "M04",
        "category": "Missing deadline",
        "notes": (
            "Rapat 9 November 2026. Sinta ditugaskan "
            "memperbaiki desain template email. "
            "Tenggat waktu belum ditentukan."
        ),
        "expected": [
            ("Memperbaiki desain template email", "Sinta", None)
        ]
    },
    {
        "id": "M05",
        "category": "Missing PIC and deadline",
        "notes": (
            "Rapat 9 November 2026. Tim menyepakati "
            "perlunya melakukan audit dokumentasi sistem. "
            "PIC dan deadline belum ditentukan."
        ),
        "expected": [
            ("Melakukan audit dokumentasi sistem", None, None)
        ]
    },
    {
        "id": "M06",
        "category": "No action items",
        "notes": (
            "Rapat 9 November 2026. Maya menyampaikan "
            "bahwa sistem login sudah selesai. "
            "Dashboard sudah berjalan stabil. "
            "Tidak ada penugasan baru."
        ),
        "expected": []
    },
    {
        "id": "M07",
        "category": "Task versus undecided proposal",
        "notes": (
            "Rapat 9 November 2026. Andi harus "
            "memperbaiki bug login pada 12 November 2026. "
            "Tim juga mempertimbangkan penambahan chatbot, "
            "tetapi belum memutuskan apakah akan dibuat."
        ),
        "expected": [
            ("Memperbaiki bug login", "Andi", "2026-11-12")
        ]
    },
    {
        "id": "M08",
        "category": "Relative deadline",
        "notes": (
            "Rapat dilaksanakan 9 November 2026. "
            "Maya meminta Budi mengirim laporan "
            "pengujian besok, 10 November 2026."
        ),
        "expected": [
            ("Mengirim laporan pengujian", "Budi", "2026-11-10")
        ]
    },
    {
        "id": "M09",
        "category": "Repeated assignment",
        "notes": (
            "Rapat 9 November 2026. Andi diminta "
            "memperbaiki API login sebelum 12 November "
            "2026. Pada akhir rapat, Maya kembali "
            "mengingatkan bahwa Andi harus menyelesaikan "
            "perbaikan API login pada 12 November 2026. "
            "Keduanya merujuk pada pekerjaan yang sama."
        ),
        "expected": [
            ("Memperbaiki API login", "Andi", "2026-11-12")
        ]
    },
    {
        "id": "M10",
        "category": "Mixed meeting context",
        "notes": (
            "Rapat evaluasi 9 November 2026. "
            "Andi menyampaikan modul autentikasi telah "
            "selesai, tetapi Maya meminta Andi memperbaiki "
            "refresh token sebelum 12 November 2026. "
            "Budi harus memperbaiki filter dashboard "
            "pada 13 November 2026. "
            "Tim menyepakati dokumentasi API perlu "
            "diperbarui, tetapi PIC dan deadline belum ada. "
            "Sinta ditugaskan merevisi template email "
            "tanpa tenggat waktu yang ditentukan. "
            "Tim mempertimbangkan grafik progres mingguan, "
            "tetapi belum memutuskan implementasinya."
        ),
        "expected": [
            ("Memperbaiki refresh token", "Andi", "2026-11-12"),
            ("Memperbaiki filter dashboard", "Budi", "2026-11-13"),
            ("Memperbarui dokumentasi API", None, None),
            ("Merevisi template email", "Sinta", None)
        ]
    }
]
