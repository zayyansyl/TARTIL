# koreksi_rules.py

AI_FEEDBACK_TEMPLATE = {
    "Class 0": {
        "tajwid": "✅ Bacaan sesuai kaidah tajwid, termasuk pengucapan hukum nun sukun, mim sukun, mad thabi’i, dan lainnya dengan benar.",
        "makhraj": "✅ Semua huruf diucapkan dengan makhraj dan sifat yang tepat, termasuk huruf-huruf tafkhim dan tarqiq.",
        "tartil": "✅ Bacaan tartil, tempo dan intonasi sesuai, tidak terburu-buru dan jelas serta disertai penghayatan.",
    },
    "Class 1": {
        "tajwid": "❌ Hukum mad kurang tepat. Perhatikan penerapan mad thabi’i, mad wajib, atau mad jaiz. Pastikan panjang bacaan sesuai harakat yang benar.",
        "makhraj": "⚠️ Beberapa huruf seperti ح, خ, غ terdengar kurang jelas atau keluar dari makhraj yang benar. Latih artikulasi huruf halqi (tenggorokan).",
        "tartil": "⚠️ Bacaan agak cepat, kurang memperhatikan jeda antar ayat dan kalimat. Disarankan membaca lebih perlahan dan berirama.",
    },
    "Class 2": {
        "tajwid": "❌ Kesalahan dalam hukum nun sukun seperti ikhfa’, idgham, dan iqlab. Perhatikan pelafalan dan suara ghunnah.",
        "makhraj": "❌ Beberapa huruf tebal seperti ص, ض, ط, dan ظ tidak dibaca dengan penekanan yang tepat. Perhatikan sifat tafkhim huruf-huruf tersebut.",
        "tartil": "⚠️ Bacaan kurang stabil, ada bagian terburu-buru dan bagian yang terlalu lambat. Usahakan konsistensi tempo.",
    },
    "Class 3": {
        "tajwid": "❌ Banyak hukum tajwid tidak diterapkan, seperti idgham bilaghunnah, ghunnah lemah, dan mad tidak jelas.",
        "makhraj": "❌ Kesalahan serius dalam pengucapan huruf, terutama huruf-huruf seperti ع, ح, ق, خ, dan غ yang membutuhkan tekanan dan nafas khusus.",
        "tartil": "❌ Bacaan terburu-buru, tidak memperhatikan waqaf (berhenti) dan ibtida’ (memulai) yang benar. Disarankan latihan tartil dengan guru.",
    },
    "default": {
        "tajwid": "⚠️ Tajwid tidak dapat dianalisis dengan jelas. Mohon ulangi bacaan dengan suara yang lebih jelas dan sesuai.",
        "makhraj": "⚠️ Makhraj tidak terdeteksi dengan baik. Pastikan semua huruf diucapkan jelas dan tidak tertelan.",
        "tartil": "⚠️ Tartil belum bisa dianalisis. Bacaan terlalu cepat atau tidak terdengar utuh.",
    }
}
def analisis_tajwid(text):
    label = klasifikasi_dummy(text)
    return AI_FEEDBACK_TEMPLATE.get(label, AI_FEEDBACK_TEMPLATE["default"])["tajwid"]

def analisis_makhraj(text):
    label = klasifikasi_dummy(text)
    return AI_FEEDBACK_TEMPLATE.get(label, AI_FEEDBACK_TEMPLATE["default"])["makhraj"]

def analisis_tartil(text):
    label = klasifikasi_dummy(text)
    return AI_FEEDBACK_TEMPLATE.get(label, AI_FEEDBACK_TEMPLATE["default"])["tartil"]

def klasifikasi_dummy(text):
    # Fungsi dummy sementara, nanti diganti AI beneran
    import random
    return random.choice(["Class 0", "Class 1", "Class 2", "Class 3"])
