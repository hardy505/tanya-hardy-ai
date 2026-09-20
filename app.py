import streamlit as st
import google.generativeai as genai

# --- 1. KONFIGURASI TAMPILAN ---
st.set_page_config(
    page_title="Tanya Hardy - AI Assistant",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom Styling (CSS)
st.markdown("""
<style>
    .hero-title {
        font-size: 2.3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.2rem;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-sub {
        text-align: center;
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. PENGATURAN API KEY ---
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
with st.sidebar:
    st.markdown("### 🤖 **Tanya Hardy**")
    st.caption("Developed by Hardy • AI Assistant")
    st.markdown("""
    Selamat datang di **Tanya Hardy**! Ruang eksplorasi digital serba ada untuk kebutuhan akademis, pemrograman, hingga solusi praktis harian.
    
    **Panduan Prompt:**
    1. Sebutkan konteks masalahmu dengan jelas.
    2. Butuh kode program? Sebutkan bahasa yang diinginkan.
    3. Butuh penjelasan singkat? Ketik *"jelaskan secara ringkas"*.
    """)
    st.divider()
    if st.button("✨ Halaman Baru", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 3. STATE PESAN ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilan Awal jika Belum Ada Chat
if not st.session_state.messages:
    st.markdown('<div class="hero-title">✨ Tanya Hardy</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Tanyakan apa saja, dari konsep ilmu pengetahuan hingga pembuatan kode program.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💡 Jelaskan cara kerja Machine Learning", use_container_width=True):
            st.session_state.temp_prompt = "Jelaskan cara kerja Machine Learning secara sederhana untuk pemula"
        if st.button("💻 Buatkan fungsi Python membaca file CSV", use_container_width=True):
            st.session_state.temp_prompt = "Buatkan fungsi Python untuk membaca dan memproses file CSV dengan contoh datanya"
    with col2:
        if st.button("✍️ Buatkan draf permohonan izin", use_container_width=True):
            st.session_state.temp_prompt = "Buatkan contoh draf surat izin resmi tidak masuk kegiatan"
        if st.button("🚀 Tips jago problem solving coding", use_container_width=True):
            st.session_state.temp_prompt = "Berikan strategi terbaik untuk melatih logika algoritma dan problem solving di programming"

# Tampilkan Riwayat Chat
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- 4. PROSES INPUT PENGGUNA ---
prompt = st.chat_input("Ketik pesan atau pertanyaanmu di sini...")

if "temp_prompt" in st.session_state and st.session_state.temp_prompt:
    prompt = st.session_state.temp_prompt
    st.session_state.temp_prompt = None

if prompt:
    if not api_key:
        st.error("API Key belum disetel. Masukkan API Key di sidebar atau pasang di Secrets Streamlit.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        genai.configure(api_key=api_key)
        
        system_instruction = (
            "Nama kamu adalah Tanya Hardy, asisten AI cerdas serba bisa yang dibangun oleh Hardy. "
            "Kamu memiliki wawasan luas seperti ChatGPT dan Gemini. "
            "Gaya bicaramu to-the-point, jelas, cerdas, membantu, dan menggunakan bahasa Indonesia yang sangat natural."
        )

        model = genai.GenerativeModel(
            model_name="models/gemini-3.6-flash",
            system_instruction=system_instruction
        )

        chat_history = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [m["content"]]})

        chat_session = model.start_chat(history=chat_history)

        with st.chat_message("assistant", avatar="✨"):
            try:
                response_stream = chat_session.send_message(prompt, stream=True)
                full_response = ""
                response_container = st.empty()
                
                for chunk in response_stream:
                    if chunk.text:
                        full_response += chunk.text
                        response_container.markdown(full_response + "▌")
                
                response_container.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Terjadi kesalahan: {str(e)}")
