import streamlit as st
import pysrt
from deep_translator import GoogleTranslator
import io
import time

# Konfigurasi Halaman
st.set_page_config(
    page_title="Penerjemah Subtitle SRT Lengkap",
    page_icon="🌐",
    layout="centered"
)

st.title("🌐 Penerjemah Subtitle SRT")
st.write("Unggah file `.srt`, pilih bahasa asal dan bahasa tujuan untuk menerjemahkan **seluruh baris** tanpa ada yang terlewat.")

# Daftar Bahasa
LANGUAGES = {
    "Indonesian": "id",
    "English": "en",
    "Japanese": "ja",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Korean": "ko",
    "Chinese (Simplified)": "zh-CN"
}

# 1. Input File
uploaded_file = st.file_uploader("Unggah File Subtitle (.srt)", type=["srt"])

# 2. Pilih Bahasa Asal dan Tujuan
col1, col2 = st.columns(2)
with col1:
    source_lang_name = st.selectbox("Bahasa Asal (Auto/Spesifik):", ["Auto Detect", "Japanese", "English"])
with col2:
    target_lang_name = st.selectbox("Bahasa Tujuan:", list(LANGUAGES.keys()))

source_code = "auto" if source_lang_name == "Auto Detect" else LANGUAGES.get(source_lang_name, "auto")
target_code = LANGUAGES[target_lang_name]

# Fungsi untuk menerjemahkan teks tunggal dengan proteksi retry
def safe_translate(translator, text, retries=3):
    for i in range(retries):
        try:
            res = translator.translate(text)
            if res:
                return res
        except Exception:
            time.sleep(0.5 * (i + 1))
    return text

# 3. Eksekusi Penerjemahan
if uploaded_file is not None:
    if st.button("Mulai Terjemahkan 🚀"):
        content = uploaded_file.read().decode("utf-8", errors="ignore")
        
        try:
            subs = pysrt.from_string(content)
            translator = GoogleTranslator(source=source_code, target=target_code)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            total = len(subs)
            
            for idx, sub in enumerate(subs):
                clean_text = sub.text.strip()
                if clean_text:
                    # Terjemahkan baris teks
                    translated_text = safe_translate(translator, clean_text)
                    sub.text = translated_text
                
                # Update status & progress
                progress = int(((idx + 1) / total) * 100)
                progress_bar.progress(progress)
                status_text.text(f"Menerjemahkan baris {idx + 1} dari {total}...")
                
                # Jeda tipis untuk menghindari pemblokiran batas permintaan API
                if idx % 10 == 0:
                    time.sleep(0.1)
            
            status_text.success("Penerjemahan Seluruh Baris Selesai!")
            
            # Format ulang objek SubRipFile ke teks SRT
            output_buffer = io.StringIO()
            subs.write_into(output_buffer)
            result_srt = output_buffer.getvalue()
            
            st.subheader("📄 Pratinjau Hasil SRT:")
            st.text_area("Hasil:", result_srt, height=250)
            
            original_name = uploaded_file.name.rsplit(".", 1)[0]
            new_filename = f"{original_name}_{target_code}.srt"
            
            st.download_button(
                label="📥 Unduh File SRT Terjemahan",
                data=result_srt,
                file_name=new_filename,
                mime="application/x-subrip"
            )
            
        except Exception as e:
            st.error(f"Gagal memproses file SRT: {e}")
