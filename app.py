from flask import Flask, request, jsonify, send_from_directory
import os
import whisper
import difflib
import json
import numpy as np
import librosa
from tensorflow.keras.models import load_model
import traceback

from koreksi_rules import analisis_tajwid, analisis_makhraj, analisis_tartil, AI_FEEDBACK_TEMPLATE

app = Flask(__name__)

AUDIO_BASE_PATH = os.path.join("static", "assets", "audio")
CACHE_FILE = "referensi_cache.json"
model_whisper = whisper.load_model("base")
model_ai = load_model("audio_model.h5")

AYAT_REFERENSI_MAP = {}

def load_or_generate_referensi():
    global AYAT_REFERENSI_MAP
    if os.path.exists(CACHE_FILE):
        print("✅ Memuat referensi dari cache...")
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            AYAT_REFERENSI_MAP = json.load(f)
    else:
        print("🔍 Membuat referensi dari audio...")
        AYAT_REFERENSI_MAP = {}
        for ayat in sorted(os.listdir(AUDIO_BASE_PATH)):
            path = os.path.join(AUDIO_BASE_PATH, ayat)
            if not os.path.isdir(path) or not ayat.isdigit():
                continue
            AYAT_REFERENSI_MAP[ayat] = []
            for file in os.listdir(path):
                audio_path = os.path.join(path, file)
                try:
                    result = model_whisper.transcribe(audio_path, language="ar")
                    text = result["text"].strip()
                    AYAT_REFERENSI_MAP[ayat].append(text)
                except Exception as e:
                    print(f"⚠️ Gagal transkrip {audio_path}: {e}")
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(AYAT_REFERENSI_MAP, f, ensure_ascii=False, indent=2)
        print("✅ Referensi disimpan ke cache.")

def compare_similarity(refs, text):
    best = 0
    for r in refs:
        sim = difflib.SequenceMatcher(None, r, text).ratio()
        if sim > best:
            best = sim
    return best

def extract_features(file_path, target_shape=(64, 94)):
    y, sr = librosa.load(file_path, sr=16000)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=target_shape[0])
    mel_db = librosa.power_to_db(mel, ref=np.max)
    if mel_db.shape[1] < target_shape[1]:
        mel_db = np.pad(mel_db, ((0, 0), (0, target_shape[1] - mel_db.shape[1])), mode='constant')
    else:
        mel_db = mel_db[:, :target_shape[1]]
    mel_db = mel_db.reshape((*target_shape, 1)).astype(np.float32)
    return mel_db

@app.route("/predict", methods=["POST"])
def predict():
    file = request.files.get("audio")
    ayat = request.form.get("ayat")

    if not file or not ayat:
        return jsonify({"error": "Missing audio or ayat"}), 400

    save_path = "temp_audio.wav"
    file.save(save_path)

    try:
        result = model_whisper.transcribe(save_path, language="ar")
        transcribed = result["text"].strip()
    except Exception as e:
        traceback.print_exc()
        return jsonify({"score": 0, "feedback": f"Gagal transkrip: {str(e)}"}), 500

    print(f"🎧 Transkripsi: {transcribed}")

    ref_texts = AYAT_REFERENSI_MAP.get(ayat, [])
    if not ref_texts:
        print("⚠️ Referensi kosong untuk ayat", ayat)
        return jsonify({"score": 0, "feedback": "Ayat tidak ditemukan"}), 404

    similarity = compare_similarity(ref_texts, transcribed)
    score = int(similarity * 100)
    feedback = "✅ Bacaan sesuai" if score >= 85 else "❌ Bacaan belum sesuai"

    try:
        features = extract_features(save_path)
        input_data = np.expand_dims(features, axis=0)
        pred = model_ai.predict(input_data)
        pred_class = int(np.argmax(pred))
        label = f"Class {pred_class}"
        ai_feedback = AI_FEEDBACK_TEMPLATE.get(label, AI_FEEDBACK_TEMPLATE["default"])
    except Exception as e:
        traceback.print_exc()
        return jsonify({"score": score, "feedback": feedback, "error": f"Gagal proses AI: {str(e)}"}), 500

    koreksi = {
        "tajwid": analisis_tajwid(transcribed),
        "makhraj": analisis_makhraj(transcribed),
        "tartil": analisis_tartil(transcribed),
        "ai_class": label,
        "ai_feedback": ai_feedback
    }

    return jsonify({
        "transkripsi": transcribed,
        "ayat": ref_texts,
        "score": score,
        "feedback": feedback,
        "koreksi": koreksi
    })

@app.route("/")
def index():
    return send_from_directory(".", "index.html")  # atau "index (2).html" jika belum diubah namanya

@app.route("/page2")
def page2():
    return send_from_directory(".", "page2.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)

if __name__ == "__main__":
    load_or_generate_referensi()
    app.run(debug=True)
