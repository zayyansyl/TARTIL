import numpy as np
import librosa
from tensorflow.keras.models import load_model
from pydub import AudioSegment
import io

MODEL_PATH = "audio_model.h5"
TARGET_SHAPE = (64, 94)

model = load_model(MODEL_PATH)

# Fungsi baru untuk load mp3 atau wav
def load_audio_file(file_path, sr=16000):
    if file_path.lower().endswith(".mp3"):
        audio = AudioSegment.from_mp3(file_path)
        raw = io.BytesIO()
        audio.export(raw, format="wav")
        raw.seek(0)
        y, _ = librosa.load(raw, sr=sr)
    else:
        y, _ = librosa.load(file_path, sr=sr)
    return y

def extract_features(file_path):
    y = load_audio_file(file_path)
    mel = librosa.feature.melspectrogram(y=y, sr=16000, n_mels=TARGET_SHAPE[0])
    mel_db = librosa.power_to_db(mel, ref=np.max)
    if mel_db.shape[1] < TARGET_SHAPE[1]:
        mel_db = np.pad(mel_db, ((0, 0), (0, TARGET_SHAPE[1] - mel_db.shape[1])), mode='constant')
    else:
        mel_db = mel_db[:, :TARGET_SHAPE[1]]
    return mel_db.reshape((1, *TARGET_SHAPE, 1)).astype(np.float32)

if __name__ == "__main__":
    file_path = input("Masukkan path file mp3/wav: ").strip()
    features = extract_features(file_path)
    pred = model.predict(features)
    pred_class = np.argmax(pred)
    print(f"✅ Prediksi kelas: {pred_class}")
    print(f"🔢 Output prediksi: {pred}")
