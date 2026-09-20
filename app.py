import streamlit as st
import google.generativeai as genai

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Tanya Hardy - AI Assistant",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Link Ikon Khusus (Tajam & terbaca di semua jenis HP)
AVATAR_AI = "https://api.iconify.design/solar:magic-stick-3-bold-duotone.svg?color=%238b5cf6"
AVATAR_USER = "https://api.iconify.design/solar:user-circle-bold-duotone.svg?color=%233b82f6"

# --- 2. GAYA TAMPILAN CUSTOM (CSS) & ANIMASI LOADING ---
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
    /* Animasi denyut teks status berpikir */
    @keyframes pulseText {
        0% { opacity: 0.4; }
        50% { opacity: 1; }
        100% { opacity: 0.4; }
    }
    .thinking-status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: #8b5cf6;
        font-weight: 500;
        font-size: 0.95rem;
        animation: pulseText 1.4s infinite ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. PENGATURAN API KEY & SIDEBAR ---
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        st.subheader("⚙️ Pengaturan")
        api_key = st.text_input("Google Gemini API Key:", type="password")
        st.markdown("[Dapatkan API Key Gratis](https://aistudio.google.com/)")

with st.sidebar:
    st.markdown("### ✨ **Tanya Hardy**")
    st.caption("🚀 *Personal AI Assistant*")
    st.markdown("""
    Halo! Saya **Tanya Hardy**, rekan berpikir digital yang siap membantu menjawab pertanyaan, tugas, pemrograman, hingga diskusi ide kreatif kapan saja.
    """)
    st.divider()
    if st.button("💬 Obrolan Baru", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 4. SESI DAN RIWAYAT CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilan Menu Awal jika Belum Ada Chat
if not st.session_state.messages:
    st.markdown('<div class="hero-title">✨ Tanya Hardy</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Tanyakan apa saja, dari konsep ilmu pengetahuan hingga pembuatan kode program.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💡 Jelaskan cara kerja Machine Learning", use_container_width=True):
            st.session_state.temp_prompt = "Jelaskan cara kerja Machine Learning secara sederhana untuk pemula"
        if st.button("💻 Buatkan fungsi Python membaca file CSV", use_container_width=True):
            st.session_state.temp_prompt = "Buatkan fungsi Python untuk membaca dan memproses file CSV beserta penjelasannya"
    with col2:
        if st.button("✍️ Buatkan draf permohonan izin", use_container_width=True):
            st.session_state.temp_prompt = "Buatkan contoh draf surat izin resmi tidak masuk kegiatan"
        if st.button("🚀 Tips jago problem solving coding", use_container_width=True):
            st.session_state.temp_prompt = "Berikan strategi terbaik untuk melatih logika algoritma dan problem solving di programming"

# Tampilkan Riwayat Obrolan
for msg in st.session_state.messages:
    avatar = AVATAR_USER if msg["role"] == "user" else AVATAR_AI
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- 5. PEMROSESAN PESAN PENGGUNA ---
prompt = st.chat_input("Ketik pesan atau pertanyaanmu di sini...")

if "temp_prompt" in st.session_state and st.session_state.temp_prompt:
    prompt = st.session_state.temp_prompt
    st.session_state.temp_prompt = None

if prompt:
    if not api_key:
        st.error("API Key belum disetel. Masukkan API Key di sidebar atau pasang di Secrets Streamlit.")
    else:
        # Tampilkan Pesan Pengguna
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=AVATAR_USER):
            st.markdown(prompt)

        # Inisialisasi Model Gemini
        genai.configure(api_key=api_key)
        system_instruction = (
            "Nama kamu adalah Tanya Hardy, asisten AI cerdas serba bisa yang dibangun oleh Hardy. "
            "Gaya bicaramu to-the-point, berwawasan luas, ramah, dan menggunakan bahasa Indonesia yang natural."
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

        # Tampilkan Pesan AI dengan Animasi Status Berpikir
        with st.chat_message("assistant", avatar=AVATAR_AI):
            response_container = st.empty()
            
            # Animasi saat AI mulai memproses
            response_container.markdown(
                '<div class="thinking-status">🌀 <i>Tanya Hardy sedang berpikir...</i></div>', 
                unsafe_allow_html=True
            )
            
            try:
                response_stream = chat_session.send_message(prompt, stream=True)
                full_response = ""
                first_chunk = True
                
                for chunk in response_stream:
                    if chunk.text:
                        if first_chunk:
                            response_container.empty()
                            first_chunk = False
                        full_response += chunk.text
                        response_container.markdown(full_response + "▌")
                
                response_container.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                response_container.empty()
                st.error(f"Terjadi kesalahan: {str(e)}")
