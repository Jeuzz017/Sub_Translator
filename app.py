import streamlit as st
import pysrt
from deep_translator import GoogleTranslator
import io

# Konfigurasi Halaman
st.set_page_config(
    page_title="Penerjemah Subtitle SRT",
    page_icon="🌐",
    layout="centered"
)

st.title("🌐 Penerjemah Subtitle SRT")
st.write("Unggah file `.srt`, pilih bahasa tujuan, lalu unduh hasilnya lengkap dengan timestamp!")

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

# 2. Pilih Bahasa
target_lang_name = st.selectbox("Pilih Bahasa Tujuan:", list(LANGUAGES.keys()))
target_lang_code = LANGUAGES[target_lang_name]

# 3. Eksekusi Penerjemahan
if uploaded_file is not None:
    if st.button("Mulai Terjemahkan 🚀"):
        # Membaca isi file sebagai teks UTF-8
        content = uploaded_file.read().decode("utf-8", errors="ignore")
        
        try:
            # Parse menggunakan pysrt
            subs = pysrt.from_string(content)
            translator = GoogleTranslator(source='auto', target=target_lang_code)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            total = len(subs)
            
            # Terjemahkan teks di setiap blok subtitle
            for idx, sub in enumerate(subs):
                if sub.text.strip():
                    try:
                        sub.text = translator.translate(sub.text)
                    except Exception:
                        pass # Jika ada 1 baris gagal, tetap lanjut ke baris berikutnya
                
                # Update progress
                progress = int(((idx + 1) / total) * 100)
                progress_bar.progress(progress)
                status_text.text(f"Menerjemahkan baris {idx + 1} dari {total}...")
            
            status_text.success("Penerjemahan Selesai!")
            
            # Mengonversi objek SubRipFile kembali ke format teks SRT
            output_buffer = io.StringIO()
            subs.write_into(output_buffer)
            result_srt = output_buffer.getvalue()
            
            # Tampilkan Pratinjau
            st.subheader("📄 Pratinjau Hasil SRT:")
            st.text_area("Hasil:", result_srt, height=250)
            
            # Nama File Output
            original_name = uploaded_file.name.rsplit(".", 1)[0]
            new_filename = f"{original_name}_{target_lang_code}.srt"
            
            # Tombol Download
            st.download_button(
                label="📥 Unduh File SRT Terjemahan",
                data=result_srt,
                file_name=new_filename,
                mime="application/x-subrip"
            )
            
        except Exception as e:
            st.error(f"Gagal memproses file SRT. Pastikan file terunggah memiliki format SRT yang valid. Error: {e}")
