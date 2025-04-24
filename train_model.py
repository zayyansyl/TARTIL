import os
import numpy as np
import librosa
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from pydub import AudioSegment
import io

DATASET_PATH = "dataset"
TARGET_SHAPE = (64, 94)
NUM_CLASSES = 4


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
    return mel_db.reshape((*TARGET_SHAPE, 1)).astype(np.float32)

def load_dataset():
    X, y = [], []
    for label in range(NUM_CLASSES):
        folder = os.path.join(DATASET_PATH, f"class_{label}")
        if not os.path.exists(folder):
            continue
        for fname in os.listdir(folder):
            if fname.endswith(('.wav', '.mp3')):
                path = os.path.join(folder, fname)
                try:
                    features = extract_features(path)
                    X.append(features)
                    y.append(label)
                    print(f"✅ Loaded {path}")
                except Exception as e:
                    print(f"⚠️ Failed {path}: {e}")
    return np.array(X), to_categorical(y, NUM_CLASSES)

def build_model(input_shape):
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(64, activation='relu'),
        Dense(NUM_CLASSES, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

if __name__ == "__main__":
    print("🔍 Membaca semua audio dari folder dataset...")
    X, y = load_dataset()
    print(f"📊 Jumlah data: {len(X)}")

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    model = build_model(X.shape[1:])
    model.fit(X_train, y_train, epochs=20, validation_data=(X_val, y_val))

    model.save("audio_model.h5")
    print("💾 Menyimpan model ke audio_model.h5")
