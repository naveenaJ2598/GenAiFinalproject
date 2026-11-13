
import sys
from pathlib import Path

import streamlit as st

# --------------------------------------------------
# PROJECT ROOT AND BACKEND IMPORTS
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.logic import ask_lingua_mate
from backend.rag import extract_text_from_pdf, answer_document_question


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="LinguaMate AI",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 5%, #172b4d 0%, transparent 35%),
        linear-gradient(135deg, #080e1c, #101a2e 60%, #0b1220);
    color: #edf3ff;
}

/* Main page spacing - FIX */

.block-container {
    max-width: 1250px;
    padding-top: 3.5rem !important;
    padding-bottom: 3rem !important;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: #0c1527;
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] p {
    color: #c5d0e5;
}

/* Headings and text */

h1, h2, h3 {
    color: #f4f7ff !important;
    letter-spacing: -0.5px;
}

p {
    color: #b9c6dc;
    line-height: 1.7;
}

/* Hero container */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(20, 35, 59, 0.75);
    border: 1px solid rgba(150,180,255,0.2);
    border-radius: 20px;
}

/* Hero title */

.hero-title {
    color: #ffffff !important;
    font-size: clamp(32px, 5vw, 52px);
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 16px;
}

.hero-description {
    color: #d1dbee !important;
    font-size: 16px;
    line-height: 1.8;
    max-width: 750px;
}

/* Section label */
/* Section label visibility - FIX */

.section-label {
    display: block;
    color: #7ee7dc !important;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1.8px;
    line-height: 1.8;
    margin-top: 0.5rem;
    margin-bottom: 12px;
    padding-top: 4px;
    overflow: visible;
}

/* Feature cards */

.feature-heading {
    color: #ffffff !important;
    font-size: 20px;
    font-weight: 700;
}

.feature-description {
    color: #b9c6dc !important;
    font-size: 14px;
}

/* Buttons */

.stButton > button {
    background: linear-gradient(100deg, #20b8ad, #6475e8);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.65rem 1.4rem;
    font-weight: 700;
    min-height: 44px;
}

.stButton > button:hover {
    border: 1px solid #7ee7dc;
    color: white;
}

/* Inputs */

.stTextInput input,
.stTextArea textarea {
    background: #111d32 !important;
    color: white !important;
    border: 1px solid #344664 !important;
    border-radius: 10px !important;
}

.stTextInput label,
.stTextArea label,
.stFileUploader label {
    color: #dce6f7 !important;
    font-weight: 600;
}

/* File uploader */

[data-testid="stFileUploader"] {
    background: #111d32;
    border: 1px dashed #536c91;
    border-radius: 14px;
    padding: 14px;
}

/* Chat messages */

[data-testid="stChatMessage"] {
    background: #142239;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 12px;
}

/* Divider */

hr {
    border-color: rgba(255,255,255,0.10);
}

/* Footer */

.footer-text {
    color: #8494ad !important;
    font-size: 12px;
    text-align: center;
}

/* Mobile */

@media (max-width: 768px) {
    .hero-title {
        font-size: 32px;
    }

    .hero-description {
        font-size: 14px;
    }

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

defaults = {
    "page": "Home",
    "pdf_text": "",
    "pdf_name": "",
    "chat_history": [],
    "english_result": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def change_page(page_name):
    st.session_state.page = page_name


def display_english_result(result):

    if isinstance(result, dict):

        for key, value in result.items():

            with st.container(border=True):
                st.markdown(
                    f"#### {str(key).replace('_', ' ').title()}"
                )
                st.write(str(value))

    else:

        with st.container(border=True):
            st.write(str(result))


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("# 🌐 LinguaMate AI")

    st.caption("Your Personal AI Learning Space")

    st.divider()

    st.markdown("### NAVIGATION")

    if st.button("🏠 Home", use_container_width=True):
        change_page("Home")
        st.rerun()

    if st.button("💬 English Coach", use_container_width=True):
        change_page("English Coach")
        st.rerun()

    if st.button("📄 PDF Assistant", use_container_width=True):
        change_page("PDF Assistant")
        st.rerun()

    st.divider()

    st.markdown("### ✨ Learning with AI")

    st.caption(
        "Improve your English and understand your documents "
        "with your AI companion."
    )


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

if st.session_state.page == "Home":

    with st.container(border=True):

        st.markdown(
            '<p class="section-label">YOUR PERSONAL LEARNING SPACE</p>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="hero-title">Learn. Understand.<br>Improve.</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <p class="hero-description">
            Welcome to LinguaMate AI — your friendly AI learning
            companion. Practise English with Tamil explanations
            or understand your PDF documents with AI assistance.
            </p>
            """,
            unsafe_allow_html=True
        )

        st.write("🌐 English Learning     🤖 AI Powered     📚 PDF Understanding")

    st.write("")

    st.markdown(
        '<p class="section-label">EXPLORE YOUR TOOLS</p>',
        unsafe_allow_html=True
    )

    st.header("What would you like to do today?")

    col1, col2 = st.columns(2, gap="large")

    with col1:

        with st.container(border=True):

            st.markdown("## 💬")

            st.markdown(
                '<p class="feature-heading">English Coach</p>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<p class="feature-description">'
                'Improve your English sentences with AI correction, '
                'simple Tamil explanations and vocabulary support.'
                '</p>',
                unsafe_allow_html=True
            )

        if st.button(
            "Start English Practice →",
            key="home_english",
            use_container_width=True
        ):
            change_page("English Coach")
            st.rerun()

    with col2:

        with st.container(border=True):

            st.markdown("## 📄")

            st.markdown(
                '<p class="feature-heading">PDF Assistant</p>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<p class="feature-description">'
                'Upload your PDF document and ask questions. '
                'Understand important information easily.'
                '</p>',
                unsafe_allow_html=True
            )

        if st.button(
            "Explore PDF Assistant →",
            key="home_pdf",
            use_container_width=True
        ):
            change_page("PDF Assistant")
            st.rerun()

    st.divider()

    st.subheader("Your AI Learning Companion")

    st.write(
        "One place to practise English, understand documents "
        "and learn with the help of AI."
    )


# --------------------------------------------------
# ENGLISH COACH
# --------------------------------------------------

elif st.session_state.page == "English Coach":

    st.markdown(
        '<p class="section-label">AI ENGLISH LEARNING</p>',
        unsafe_allow_html=True
    )

    st.title("💬 English Coach")

    st.write(
        "Write an English sentence. Your AI coach will help you "
        "correct it and understand it in Tamil."
    )

    st.divider()

    sentence = st.text_area(
        "Enter your English sentence",
        placeholder="Example: I am go to school yesterday.",
        height=130,
        key="english_sentence"
    )

    if st.button("✨ Correct My English", key="correct_english"):

        if sentence.strip():

            with st.spinner("Your AI coach is thinking..."):

                try:
                    result = ask_lingua_mate(sentence.strip())
                    st.session_state.english_result = result

                except Exception as error:
                    st.error(f"Unable to process your sentence: {error}")

        else:
            st.warning("Please enter a sentence first.")

    if st.session_state.english_result is not None:

        st.divider()
        st.subheader("Your Learning Result")

        display_english_result(st.session_state.english_result)


# --------------------------------------------------
# PDF ASSISTANT
# --------------------------------------------------

elif st.session_state.page == "PDF Assistant":

    st.markdown(
        '<p class="section-label">DOCUMENT AI ASSISTANT</p>',
        unsafe_allow_html=True
    )

    st.title("📄 PDF Assistant")

    st.write(
        "Upload your PDF document and ask questions about "
        "its contents. Your AI assistant will help you."
    )

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload your PDF document",
        type=["pdf"],
        help="Choose a PDF file from your computer."
    )

    if uploaded_file is not None:

        if uploaded_file.name != st.session_state.pdf_name:

            with st.spinner("Reading your PDF document..."):

                try:
                    pdf_text = extract_text_from_pdf(uploaded_file)

                    st.session_state.pdf_text = pdf_text
                    st.session_state.pdf_name = uploaded_file.name
                    st.session_state.chat_history = []

                except Exception as error:
                    st.error(f"Unable to read PDF: {error}")

        if st.session_state.pdf_text:

            st.success(
                f"Document ready: {st.session_state.pdf_name}"
            )

            st.divider()
            st.subheader("Ask Your Document")

            for message in st.session_state.chat_history:

                with st.chat_message(message["role"]):
                    st.write(message["content"])

            question = st.chat_input(
                "Ask a question about your PDF..."
            )

            if question:

                st.session_state.chat_history.append(
                    {"role": "user", "content": question}
                )

                with st.chat_message("user"):
                    st.write(question)

                with st.chat_message("assistant"):

                    with st.spinner("Finding your answer..."):

                        try:
                            answer = answer_document_question(
                                question,
                                st.session_state.pdf_text
                            )

                            st.write(answer)

                            st.session_state.chat_history.append(
                                {
                                    "role": "assistant",
                                    "content": str(answer)
                                }
                            )

                        except Exception as error:

                            error_message = (
                                f"Unable to answer your question: {error}"
                            )

                            st.error(error_message)

                            st.session_state.chat_history.append(
                                {
                                    "role": "assistant",
                                    "content": error_message
                                }
                            )

        else:
            st.warning(
                "No readable text was found in this PDF. "
                "Please try another PDF document."
            )

    else:

        with st.container(border=True):

            st.markdown("## 📚 Start with your document")

            st.write(
                "Upload a PDF to begin asking questions. "
                "Your document content will be used to find answers."
            )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    '<p class="footer-text">'
    '🌐 LinguaMate AI | Powered by Generative AI | '
    'Learn. Understand. Improve.'
    '</p>',
    unsafe_allow_html=True
)
