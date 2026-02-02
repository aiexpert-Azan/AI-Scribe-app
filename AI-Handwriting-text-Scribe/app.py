import streamlit as st
import os
import time
import base64
from PIL import Image

# ==========================================
# 1. SETUP & STYLE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Text ↔ Handwriting Converter",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (DARK PORTFOLIO THEME) ---
st.markdown("""
    <style>
    /* 1. MAIN BACKGROUND (Deep Dark Purple/Black Gradient) */
    .stApp {
        background-color: #110C1D;
        background-image: radial-gradient(circle at 50% 0%, #2a1b3d 0%, #110C1D 70%);
        color: #FFFFFF;
    }
    
    /* 2. HIDE DEFAULT HEADER */
    header[data-testid="stHeader"] {
        background-color: transparent;
    }
    
    /* 3. TYPOGRAPHY (Elegant & Clean) */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;600&display=swap');
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif;
        color: #FFFFFF !important;
        letter-spacing: 0.5px;
    }
    
    p, div, label, span, li, button {
        font-family: 'Inter', sans-serif;
        color: #E2E8F0 !important; /* Light gray for readability */
    }

    /* 4. HERO SECTION STYLES (Landing Page) */
    .hero-container {
        text-align: center;
        padding: 4rem 0 2rem 0;
        animation: fadeIn 1s ease-in;
    }
    
    .badge {
        background-color: rgba(255, 255, 255, 0.1);
        color: #A0AEC0 !important;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        display: inline-block;
        margin-bottom: 1.5rem;
    }
    
    .hero-title {
        font-size: 4.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem; 
        color: #FFFFFF !important;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.1);
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: #CBD5E0 !important;
        
        /* === FIX: CENTERING === */
        text-align: center !important;  /* Forces text to center */
        display: block;
        margin-left: auto !important;   /* Push from left */
        margin-right: auto !important;  /* Push from right */
        margin-top: 1rem;
        margin-bottom: 3rem;
        max-width: 750px;               /* Keeps text in a nice block */
        line-height: 1.6;
        font-weight: 400;
    }

    /* 5. CUSTOM BUTTONS (Neon Pink Accent - INCREASED SIZE) */
    div.stButton > button {
        border-radius: 50px;
        /* Larger padding makes the button physically bigger */
        padding: 0.75rem 3rem; 
        font-weight: 600;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
        background-color: rgba(255,255,255,0.05);
        color: white !important;
        /* Larger font size */
        font-size: 1.2rem; 
    }
    
    /* Primary Action Button (Neon Hover) */
    div.stButton > button:hover {
        transform: translateY(-2px);
        border-color: #FF2E63;
        background-color: #FF2E63 !important; /* Neon Pink/Red */
        box_shadow: 0 4px 25px rgba(255, 46, 99, 0.5);
        color: white !important;
    }

    /* 6. PREVIEW BOX (70% Width, Dark Mode Optimized) */
    .preview-box {
        border: 1px solid #2D3748;
        border-radius: 12px;
        padding: 10px;
        background-color: #FFFFFF; /* White background so ink is visible */
        box_shadow: 0 4px 15px rgba(0,0,0,0.3);
        display: flex;
        justify-content: center;
        align-items: center;
        width: 70% !important; 
        margin: 0 auto !important;
        min-height: 90px;
    }
    
    .preview-box img {
        width: 100%; 
        height: auto; 
        object-fit: contain;
    }

    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BACKEND LOADING
# ==========================================
try:
    from main_app import HandwritingBot, save_response_as_pdf
    import ocr_page
    BACKEND_READY = True
except ImportError as e:
    st.error(f"❌ Backend Error: {e}")
    BACKEND_READY = False

# Initialize Bot
if BACKEND_READY and "bot_engine" not in st.session_state:
    st.session_state.bot_engine = HandwritingBot()

# Helper for SVG (Renders inside the 70% box)
def render_svg(svg_path):
    with open(svg_path, "r") as f: svg_content = f.read()
    b64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
    return f'<div class="preview-box"><img src="data:image/svg+xml;base64,{b64}"/></div>'

# ==========================================
# 3. NAVIGATION STATE MANAGEMENT
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def go_home(): st.session_state.page = 'home'
def go_writer(): st.session_state.page = 'writer'
def go_reader(): st.session_state.page = 'reader'

# ==========================================
# 4. PAGE: LANDING / HOME
# ==========================================
def show_home_page():
    # Navbar Placeholder
    col_nav1, col_nav2 = st.columns([6, 1])
    with col_nav1:
        st.markdown("### ✍️ AI Scribe")
    with col_nav2:
        pass 

    st.markdown("<br>", unsafe_allow_html=True)
    
    # HERO SECTION
    st.markdown("""
        <div class="hero-container">
            <span class="badge">✨ Future of Digital Ink</span>
            <div class="hero-title">Text ↔ Handwriting<br>Converter</div>
            <div class="hero-subtitle">
                Transform your digital documents with AI-powered handwriting synthesis.
                Experience the perfect blend of human touch and machine precision.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ACTION BUTTONS (Centered Layout)
    # Adjusted columns to bring buttons closer together while keeping them centered
    col1, col2, col3, col4, col5 = st.columns([0.5, 2, 0.2, 2, 0.5])
    
    with col2:
        # Primary Action (Will glow Pink on hover)
        if st.button("Open Handwriting Studio →", use_container_width=True):
            go_writer()
            st.rerun()

    with col4:
        # Secondary Action
        if st.button("Open OCR Reader →", use_container_width=True):
            go_reader()
            st.rerun()

# ==========================================
# 5. PAGE: WRITER (Text -> Hand)
# ==========================================
def show_writer_page():
    # Top Nav
    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("← Home"):
            go_home()
            st.rerun()
    with col2:
        st.subheader("🖊️ Text to Handwriting Studio")
    
    st.markdown("---")

    # --- TOP: SETTINGS ---
    with st.expander("⚙️ Handwriting Settings", expanded=True):
        col_controls, col_preview = st.columns([1, 2])
        
        with col_controls:
            st.subheader("1. Choose Style")
            style_id = st.selectbox(
                "Select Handwriting Personality:",
                options=list(range(13)),
                format_func=lambda x: f"Handwriting Style {x}"
            )
            st.subheader("2. Adjust Neatness")
            bias_val = st.slider("Neatness (Bias)", 0.5, 2.0, 0.9)

        with col_preview:
            st.subheader("Preview")
            preview_path = f"style_gallery/style_{style_id}.svg"
            if os.path.exists(preview_path):
                st.markdown(render_svg(preview_path), unsafe_allow_html=True)
            else:
                st.info("ℹ️ Run `generate_gallery.py` to generate previews.")

    # --- SPLIT LAYOUT ---
    col_left, col_right = st.columns(2, gap="large")

    # LEFT: DIRECT INPUT
    with col_left:
        st.markdown("#### 📝 Direct Input")
        user_text = st.text_area("Type text here...", height=400)
        
        if st.button("Generate PDF (Left)"):
            if user_text and BACKEND_READY:
                with st.spinner("Writing..."):
                    ts = int(time.time())
                    fname = f"manual_{ts}.svg"
                    pdfname = f"manual_{ts}.pdf"
                    
                    st.session_state.bot_engine.hand_model.write(
                        filename=fname, lines=user_text, biases=[bias_val], styles=[style_id],
                        page_width=1860, page_height=3508, ruled=True
                    )
                    
                    # PDF Helper
                    base = fname.replace(".svg", "")
                    pages = [f for f in os.listdir(".") if f.startswith(base) and f.endswith(".svg")]
                    save_response_as_pdf(pages, pdfname)
                    
                    if os.path.exists(pdfname):
                        with open(pdfname, "rb") as f:
                            st.download_button("📥 Download PDF", f, "handwriting.pdf", "application/pdf")

    # RIGHT: AI CHATBOT
    with col_right:
        st.markdown("#### 🤖 AI Assistant")
        if "messages" not in st.session_state: st.session_state.messages = []

        chat_container = st.container(height=400)
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])

        if prompt := st.chat_input("Ask me to write something..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container: st.chat_message("user").markdown(prompt)

            if BACKEND_READY:
                with chat_container:
                    with st.chat_message("assistant"):
                        placeholder = st.empty()
                        placeholder.markdown("Thinking...")
                        try:
                            sys_msg = "You are a helpful assistant. Output must be plain text suitable for handwriting."
                            resp = st.session_state.bot_engine.client.chat.completions.create(
                                model="google/gemini-2.0-flash-001",
                                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages
                            )
                            bot_text = resp.choices[0].message.content.strip()
                            placeholder.markdown(bot_text)
                            st.session_state.messages.append({"role": "assistant", "content": bot_text})
                            
                            with st.status("✍️ Synthesizing...", expanded=True):
                                ts = int(time.time())
                                fname = f"bot_{ts}.svg"
                                pdfname = f"bot_{ts}.pdf"
                                st.session_state.bot_engine.hand_model.write(
                                    filename=fname, lines=bot_text, biases=[bias_val], styles=[style_id],
                                    page_width=1860, page_height=3508, ruled=True
                                )
                                base = fname.replace(".svg", "")
                                pages = [f for f in os.listdir(".") if f.startswith(base) and f.endswith(".svg")]
                                save_response_as_pdf(pages, pdfname)
                                if os.path.exists(pdfname):
                                    with open(pdfname, "rb") as f:
                                        st.download_button("📥 Download Bot PDF", f, "bot_reply.pdf", "application/pdf", key=f"btn_{ts}")
                        except Exception as e: st.error(f"Error: {e}")

# ==========================================
# 6. PAGE: READER (OCR)
# ==========================================
def show_reader_page():
    # Top Nav
    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("← Home"):
            go_home()
            st.rerun()
    with col2:
        st.subheader("📄 Handwriting to Text (OCR)")
    
    st.markdown("---")

    uploaded_file = st.file_uploader("Upload Image or PDF", type=["png", "jpg", "pdf"])

    if uploaded_file:
        tname = f"temp_{uploaded_file.name}"
        with open(tname, "wb") as f: f.write(uploaded_file.getbuffer())

        col1, col2 = st.columns([1, 2])
        with col1:
            if uploaded_file.type != "application/pdf":
                st.image(Image.open(uploaded_file), caption="Preview", use_container_width=True)
            else:
                st.info("📄 PDF Loaded")

        with col2:
            if st.button("🔍 Extract Text"):
                if BACKEND_READY:
                    with st.spinner("Processing..."):
                        if "ocr_proc" not in st.session_state:
                            p, m = ocr_page.load_model()
                            st.session_state.ocr_proc = p
                            st.session_state.ocr_mod = m
                        
                        txt = ""
                        if tname.endswith(".pdf"):
                            doc = ocr_page.fitz.open(tname)
                            for i, page in enumerate(doc):
                                pix = page.get_pixmap(dpi=200)
                                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                                txt += ocr_page.process_single_image(img, st.session_state.ocr_proc, st.session_state.ocr_mod, i+1) + "\n\n"
                        else:
                            img = Image.open(tname)
                            txt = ocr_page.process_single_image(img, st.session_state.ocr_proc, st.session_state.ocr_mod)

                        st.success("Done!")
                        st.text_area("Result:", txt, height=400)
                        st.download_button("📥 Download .txt", txt, "ocr.txt")

# ==========================================
# 7. MAIN CONTROLLER
# ==========================================
if st.session_state.page == 'home':
    show_home_page()
elif st.session_state.page == 'writer':
    show_writer_page()
elif st.session_state.page == 'reader':
    show_reader_page()