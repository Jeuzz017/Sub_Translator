import streamlit as st
import pysrt
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Penerjemah Subtitle SRT", page_icon="🌐")

st.title("🌐 Penerjemah Subtitle SRT")

LANGUAGES = {
    "Indonesian": "id",
    "English": "en",
    "Japanese": "ja",
    "Spanish": "es"
}

uploaded_file = st.file_uploader("Unggah File SRT", type=["srt"])
target_lang_name = st.selectbox("Pilih Bahasa Tujuan:", list(LANGUAGES.keys()))
target_lang_code = LANGUAGES[target_lang_name]

if uploaded_file is not None and st.button("Mulai Terjemahkan 🚀"):
    content = uploaded_file.read().decode("utf-8", errors="ignore")
    
    # Parse file SRT menggunakan pysrt agar timestamp tetap terjaga
    subs = pysrt.from_string(content)
    translator = GoogleTranslator(source='auto', target=target_lang_code)
    
    progress_bar = st.progress(0)
    total = len(subs)
    
    for idx, sub in enumerate(subs):
        if sub.text.strip():
            try:
                # Terjemahkan teks tanpa mengubah timestamp
                sub.text = translator.translate(sub.text)
            except Exception:
                pass
        progress_bar.progress(int(((idx + 1) / total) * 100))
    
    # Hasil akhir format SRT lengkap dengan timestamp
    result_srt = subs.to_string()
    
    st.success("Selesai Diterjemahkan!")
    st.text_area("Pratinjau Hasil SRT:", result_srt, height=250)
    
    st.download_button(
        label="📥 Unduh File SRT Baru",
        data=result_srt,
        file_name=f"translated_{uploaded_file.name}",
        mime="application/x-subrip"
    )
