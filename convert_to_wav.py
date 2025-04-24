import os
from pydub import AudioSegment

INPUT_DIR = "dataset"
SUPPORTED_FORMATS = [".mp3", ".m4a", ".flac", ".ogg"]
TARGET_SAMPLE_RATE = 16000

for root, dirs, files in os.walk(INPUT_DIR):
    for file in files:
        ext = os.path.splitext(file)[-1].lower()
        if ext in SUPPORTED_FORMATS:
            source_path = os.path.join(root, file)
            target_path = os.path.splitext(source_path)[0] + ".wav"

            try:
                print(f"🔄 Konversi {source_path} → {target_path}")
                audio = AudioSegment.from_file(source_path)
                audio = audio.set_frame_rate(TARGET_SAMPLE_RATE).set_channels(1)
                audio.export(target_path, format="wav")
            except Exception as e:
                print(f"⚠️ Gagal konversi {file}: {e}")
