import streamlit as st
import pysrt
from google import genai
import io

st.set_page_config(
    page_title="Penerjemah Subtitle SRT (Gemini AI)",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Penerjemah Subtitle SRT menggunakan Gemini AI")
st.write("Hasil terjemahan sangat akurat, alami, dan tidak akan melewati baris apa pun.")

# Input API Key dari pengguna di sidebar
api_key = st.sidebar.text_input("Masukkan Google Gemini API Key:", type="password")

LANGUAGES = {
    "Indonesian": "Indonesian",
    "English": "English",
    "Japanese": "Japanese",
    "Spanish": "Spanish",
    "French": "French",
    "German": "German",
    "Korean": "Korean",
    "Chinese": "Chinese"
}

uploaded_file = st.file_uploader("Unggah file Subtitle (.srt)", type=["srt"])
target_lang = st.selectbox("Pilih Bahasa Tujuan:", list(LANGUAGES.keys()))

if uploaded_file is not None:
    if st.button("Mulai Terjemahkan dengan AI 🚀"):
        if not api_key:
            st.error("Silakan masukkan Gemini API Key di sidebar terlebih dahulu.")
        else:
            content = uploaded_file.read().decode("utf-8", errors="ignore")
            
            try:
                subs = pysrt.from_string(content)
                client = genai.Client(api_key=api_key)
                
                # Menggabungkan seluruh teks subtitle untuk dikirim sekaligus ke AI
                lines = [f"{i+1}|||{sub.text.replace('\n', ' ')}" for i, sub in enumerate(subs) if sub.text.strip()]
                full_prompt_text = "\n".join(lines)
                
                prompt = f"""You are a professional subtitle translator.
Translate the following text into {target_lang}.
Maintain the exact line format 'NUMBER|||TRANSLATED_TEXT'. Do not omit any lines.

Text to translate:
{full_prompt_text}"""

                with st.spinner("AI sedang menerjemahkan seluruh subtitle..."):
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    
                    translated_raw = response.text.strip().split("\n")
                    
                    # Memetakan kembali hasil terjemahan ke objek SRT
                    trans_dict = {}
                    for line in translated_raw:
                        if "|||" in line:
                            parts = line.split("|||", 1)
                            try:
                                idx = int(parts[0].strip()) - 1
                                trans_dict[idx] = parts[1].strip()
                            except ValueError:
                                pass
                    
                    for idx, sub in enumerate(subs):
                        if idx in trans_dict:
                            sub.text = trans_dict[idx]

                st.success("Penerjemahan AI Selesai!")
                
                output_buffer = io.StringIO()
                subs.write_into(output_buffer)
                result_srt = output_buffer.getvalue()
                
                st.subheader("📄 Pratinjau Hasil SRT:")
                st.text_area("Hasil:", result_srt, height=250)
                
                original_name = uploaded_file.name.rsplit(".", 1)[0]
                new_filename = f"{original_name}_{target_lang}.srt"
                
                st.download_button(
                    label="📥 Unduh File SRT Terjemahan",
                    data=result_srt,
                    file_name=new_filename,
                    mime="application/x-subrip"
                )
                
            except Exception as e:
                st.error(f"Gagal memproses penerjemahan: {e}")
