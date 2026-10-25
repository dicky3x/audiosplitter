import os
import shutil
import subprocess
import streamlit as st

st.set_page_config(
    page_title="AI Music & Stem Separator",
    page_icon="🎵",
    layout="centered"
)

st.title("🎵 AI Real Audio Stem Separator")
st.write("Pisahkan musik, vokal, drum, dan bass secara nyata menggunakan AI **Meta Demucs**.")

# Setup Folder Sementara
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
OUTPUT_DIR = os.path.join(BASE_DIR, "separated")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Form Input
st.subheader("1. Pilih Sumber Audio")
youtube_url = st.text_input("Masukkan Link YouTube:", placeholder="https://www.youtube.com/watch?v=...")

st.subheader("2. Pilih Mode Pemisahan")
split_mode = st.radio(
    "Mode Stem:",
    ("2 Stems (Vokal + Instrumen)", "4 Stems (Vokal, Drum, Bass, Lainnya)"),
    index=0
)

num_stems = 2 if "2 Stems" in split_mode else 4

if st.button("🚀 Mulai Pisahkan Audio", type="primary"):
    if not youtube_url.strip():
        st.error("Silakan masukkan URL YouTube terlebih dahulu!")
    else:
        try:
            job_id = f"job_{int(os.urandom(4).hex(), 16)}"
            audio_path = os.path.join(DOWNLOAD_DIR, f"{job_id}.mp3")

            # Status Progress
            status_box = st.status("Sedang memproses audio...", expanded=True)
            
            # Step 1: Download dari YouTube
            status_box.write("📥 Unduh audio dari YouTube via yt-dlp...")
            ydl_cmd = [
                "yt-dlp",
                "-x", "--audio-format", "mp3",
                "-o", audio_path,
                youtube_url.strip()
            ]
            subprocess.run(ydl_cmd, check=True)

            # Step 2: Pemisahan dengan Demucs
            status_box.write("🧠 Menjalankan Model AI Demucs (Sabar, butuh beberapa saat)...")
            demucs_cmd = ["demucs", "-o", OUTPUT_DIR, "-n", "htdemucs"]
            if num_stems == 2:
                demucs_cmd.extend(["--two-stems", "vocals"])
            demucs_cmd.append(audio_path)

            subprocess.run(demucs_cmd, check=True)

            status_box.update(label="✅ Pemisahan Audio Berhasil!", state="complete", expanded=False)

            # Step 3: Tampilkan Hasil Audio Player & Download
            st.divider()
            st.subheader("🎧 Hasil Pemisahan Audio")

            stem_folder = os.path.join(OUTPUT_DIR, "htdemucs", job_id)
            if os.path.exists(stem_folder):
                files = os.listdir(stem_folder)
                for file_name in sorted(files):
                    if file_name.endswith((".wav", ".mp3")):
                        file_path = os.path.join(stem_folder, file_name)
                        stem_title = os.path.splitext(file_name)[0].capitalize()

                        st.write(f"### 🎛️ {stem_title}")
                        
                        # Read audio bytes
                        with open(file_path, "rb") as f:
                            audio_bytes = f.read()

                        # Audio Player Native Browser
                        st.audio(audio_bytes, format="audio/wav")

                        # Download Button
                        st.download_button(
                            label=f"⬇️ Unduh Track {stem_title}",
                            data=audio_bytes,
                            file_name=f"{job_id}_{file_name}",
                            mime="audio/wav"
                        )
                        st.divider()

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses: {str(e)}")