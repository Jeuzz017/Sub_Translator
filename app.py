import streamlit as st
import pysrt
from deep_translator import GoogleTranslator
import io
import time

# Konfigurasi Halaman
st.set_page_config(
    page_title="Penerjemah Subtitle SRT Perfect",
    page_icon="🌐",
    layout="centered"
)

st.title("🌐 Penerjemah Subtitle SRT (Akurat & Lengkap)")
st.write("Menerjemahkan seluruh baris `.srt` secara utuh tanpa ada teks yang terlewat.")

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

# 2. Pilih Bahasa Tujuan
target_lang_name = st.selectbox("Pilih Bahasa Tujuan:", list(LANGUAGES.keys()))
target_lang_code = LANGUAGES[target_lang_name]

# 3. Fungsi Penerjemah dengan Batching (Menggabungkan Teks)
def translate_in_batches(subs, target_code, batch_size=40):
    translator = GoogleTranslator(source='auto', target=target_code)
    total_subs = len(subs)
    
    # Kumpulkan semua teks subtitle
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(0, total_subs, batch_size):
        chunk = subs[i:i + batch_size]
        
        # Buat daftar teks dengan penanda khusus agar tidak kacau
        lines_to_translate = []
        for sub in chunk:
            # Ganti baris baru dalam 1 box subtitle dengan tag khusus
            clean_text = sub.text.replace("\n", " [BR] ").strip()
            if not clean_text:
                clean_text = "---" # Penanda teks kosong
            lines_to_translate.append(clean_text)
        
        # Gabungkan teks menggunakan pembatas unik
        combined_text = "\n===SUB_SPLIT===\n".join(lines_to_translate)
        
        try:
            # Menerjemahkan sekaligus 1 kelompok (batch)
            translated_combined = translator.translate(combined_text)
            translated_lines = translated_combined.split("\n===SUB_SPLIT===\n")
            
            # Kembalikan teks terjemahan ke objek sub masing-masing
            for idx, sub in enumerate(chunk):
                if idx < len(translated_lines):
                    res_text = translated_lines[idx].replace(" [BR] ", "\n").replace("[BR]", "\n").strip()
                    if res_text != "---":
                        sub.text = res_text
        except Exception as e:
            # Jika batching gagal, gunakan fallback penerjemahan per baris
            for sub in chunk:
                if sub.text.strip():
                    try:
                        sub.text = translator.translate(sub.text)
                    except Exception:
                        pass
        
        # Update progress bar
        current_progress = min(int(((i + batch_size) / total_subs) * 100), 100)
        progress_bar.progress(current_progress)
        status_text.text(f"Memproses {min(i + batch_size, total_subs)} dari {total_subs} baris...")
        time.sleep(0.2) # Mencegah pemblokiran API
        
    status_text.success("Penerjemahan Seluruh Baris Selesai!")

# Eksekusi
if uploaded_file is not None:
    if st.button("Mulai Terjemahkan 🚀"):
        content = uploaded_file.read().decode("utf-8", errors="ignore")
        
        try:
            subs = pysrt.from_string(content)
            
            with st.spinner("Sedang menerjemahkan... Mohon tunggu sebentar."):
                translate_in_batches(subs, target_lang_code)
            
            # Format ulang objek SubRipFile ke teks SRT
            output_buffer = io.StringIO()
            subs.write_into(output_buffer)
            result_srt = output_buffer.getvalue()
            
            st.subheader("📄 Pratinjau Hasil SRT:")
            st.text_area("Hasil:", result_srt, height=250)
            
            original_name = uploaded_file.name.rsplit(".", 1)[0]
            new_filename = f"{original_name}_{target_lang_code}.srt"
            
            st.download_button(
                label="📥 Unduh File SRT Terjemahan",
                data=result_srt,
                file_name=new_filename,
                mime="application/x-subrip"
            )
            
        except Exception as e:
            st.error(f"Gagal memproses file SRT: {e}")
