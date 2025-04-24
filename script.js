// ✅ Versi script.js terbaru (kompatibel dengan app.py + whisper + page2.html)
let mediaRecorder;
let audioChunks = [];

const startBtn = document.getElementById("btnStart");
const stopBtn = document.getElementById("btnStop");
const playBtn = document.getElementById("btnPlay");
const popup = document.getElementById("popup-hasil");
const ayatSelect = document.getElementById("ayatSelect");

startBtn.addEventListener("click", startRecording);
stopBtn.addEventListener("click", stopRecording);
playBtn.addEventListener("click", playRecording);
document.getElementById("btnClose")?.addEventListener("click", () => (popup.style.display = "none"));

function startRecording() {
  popup.style.display = "none";
  navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    mediaRecorder.onstop = handleStop;
    mediaRecorder.start();

    toggleButtons(true);
    console.log("🎤 Rekaman dimulai");
  }).catch(err => {
    alert("Izin mikrofon ditolak: " + err);
  });
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    console.log("🛑 Rekaman dihentikan");
  }
}

function playRecording() {
  if (window.recordedAudio) {
    new Audio(window.recordedAudio).play();
  }
}

async function handleStop() {
  const blob = new Blob(audioChunks, { type: "audio/webm" });
  const url = URL.createObjectURL(blob);
  window.recordedAudio = url;

  const formData = new FormData();
  formData.append("audio", blob, "recording.wav");
  formData.append("ayat", ayatSelect.value);

  try {
    const res = await fetch("/https://tartil-backend.onrender.com/predict", { method: "POST", body: formData });
    const result = await res.json();

    console.log("🎯 Hasil:", result);
    tampilkanHasil(result);
  } catch (err) {
    alert("❌ Gagal kirim audio ke server");
    console.error(err);
  }

  toggleButtons(false);
}

function tampilkanHasil(data) {
  document.getElementById("bar-score").style.width = `${data.score || 0}%`;
  document.getElementById("similarity-score").textContent = `${data.score || 0}`;
  document.getElementById("popup-tajwid").textContent = data.koreksi?.tajwid || "-";
  document.getElementById("popup-makhraj").textContent = data.koreksi?.makhraj || "-";
  document.getElementById("popup-tartil").textContent = data.koreksi?.tartil || "-";
  document.getElementById("popup-ai").textContent = data.koreksi?.ai_class || "-";
  document.getElementById("popup-feedback").textContent = data.koreksi?.ai_feedback?.tajwid || "-";

  popup.style.display = "flex";
}

function toggleButtons(isRecording) {
  startBtn.classList.toggle("hidden", isRecording);
  stopBtn.classList.toggle("hidden", !isRecording);
  playBtn.classList.toggle("hidden", isRecording);
}
