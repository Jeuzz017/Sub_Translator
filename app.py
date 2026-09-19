import streamlit as st
import pysrt
from deep_translator import GoogleTranslator

# Konfigurasi Halaman
st.set_page_config(
    page_title="Penerjemah Subtitle & Dokumen",
    page_icon="🌐",
    layout="centered"
)

st.title("🌐 Penerjemah File Subtitle (SRT & Teks)")
st.write("Unggah file subtitle (`.srt`) atau teks (`.txt`), pilih bahasa tujuan, lalu unduh hasilnya!")

# Daftar Bahasa (Bahasa Asal -> Kode)
LANGUAGES = {
    "Indonesian": "id",
    "English": "en",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese (Simplified)": "zh-CN",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Arabic": "ar"
}

# 1. Upload File
uploaded_file = st.file_uploader("Pilih file subtitle", type=["srt", "txt"])

# 2. Pilih Bahasa
target_lang_name = st.selectbox("Pilih Bahasa Tujuan:", list(LANGUAGES.keys()))
target_lang_code = LANGUAGES[target_lang_name]

# Fungsi Penerjemah SRT
def translate_srt(file_bytes, target_lang):
    content = file_bytes.decode("utf-8", errors="ignore")
    subs = pysrt.from_string(content)
    
    translator = GoogleTranslator(source='auto', target=target_lang)
    
    total_items = len(subs)
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, sub in enumerate(subs):
        if sub.text.strip():
            try:
                sub.text = translator.translate(sub.text)
            except Exception:
                pass # Lewati jika ada baris yang gagal
        
        progress = int(((idx + 1) / total_items) * 100)
        progress_bar.progress(progress)
        status_text.text(f"Menerjemahkan baris {idx + 1} dari {total_items}...")
        
    status_text.success("Penerjemahan Selesai!")
    return subs.text

# Fungsi Penerjemah TXT
def translate_txt(file_bytes, target_lang):
    text = file_bytes.decode("utf-8", errors="ignore")
    translator = GoogleTranslator(source='auto', target=target_lang)
    return translator.translate(text)

# 3. Tombol Eksekusi
if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    if st.button("Mulai Terjemahkan 🚀"):
        file_bytes = uploaded_file.read()
        
        with st.spinner("Sedang memproses..."):
            if file_extension == "srt":
                result_text = translate_srt(file_bytes, target_lang_code)
            else:
                result_text = translate_txt(file_bytes, target_lang_code)
            
            st.subheader("📄 Pratinjau Hasil Terjemahan:")
            st.text_area("Hasil:", result_text, height=200)
            
            original_name = uploaded_file.name.rsplit(".", 1)[0]
            new_filename = f"{original_name}_{target_lang_code}.{file_extension}"
            
            st.download_button(
                label="📥 Unduh File Terjemahan",
                data=result_text,
                file_name=new_filename,
                mime="text/plain"
            )
