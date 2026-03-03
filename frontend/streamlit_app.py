"""
HR Bot - Streamlit UI
Clean, simple chat interface with purple accent theme
"""

import streamlit as st
import requests
import uuid

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HR Bot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Session state ──────────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── API config ─────────────────────────────────────────────────────────────────
API_URL       = "http://localhost:8000"
CHAT_ENDPOINT = f"{API_URL}/chat/"

# ── Minimal CSS polish ─────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
  }

  /* Hide Streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }

  /* Tighten page padding */
  .block-container {
    padding-top: 2rem !important;
    max-width: 720px !important;
  }

  /* Title underline accent */
  .brand-wrap { margin-bottom: 1.6rem; }
  .brand-title {
    font-size: 2.2rem;
    font-weight: 900;
    letter-spacing: -0.5px;
    margin: 0;
    color: inherit;
  }
  .brand-line {
    width: 48px;
    height: 4px;
    background: #7C3AED;
    border-radius: 2px;
    margin: 6px 0 8px 0;
  }
  .brand-sub {
    font-size: 0.88rem;
    opacity: 0.55;
    margin: 0;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    padding-top: 1.5rem;
  }

  /* Sample question buttons - compact */
  .stButton > button {
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    padding: 0.35rem 0.75rem !important;
    text-align: left !important;
    transition: border-color 0.15s;
  }
  .stButton > button:hover {
    border-color: #7C3AED !important;
    color: #7C3AED !important;
  }

  /* Chat messages — tighten spacing */
  [data-testid="stChatMessage"] {
    padding: 0.6rem 0 !important;
  }
</style>
""", unsafe_allow_html=True)

# ── Send helper ────────────────────────────────────────────────────────────────
def send(question: str):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking…"):
            try:
                response = requests.post(
                    CHAT_ENDPOINT,
                    json={
                        "question": question,
                        "session_id": st.session_state.session_id
                    },
                    timeout=120  # Ollama/llama3 can take time on first load
                )
                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer received.")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = f"Error: {response.status_code} - {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except requests.Timeout:
                st.error("⏳ Request timed out. Ollama may still be loading the model — please try again in a moment.")
            except requests.ConnectionError:
                st.error("❌ Cannot connect to API server. Make sure `python run.py` is running.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("#### 🤖 HR Bot")
    st.caption("RAG-powered HR policy assistant")
    st.divider()

    # Server status
    st.markdown("**Server Status**")
    try:
        h = requests.get(f"{API_URL}/health", timeout=3)
        if h.status_code == 200:
            st.success("API Online", icon="✅")
        else:
            st.error("❌ API Server Error")
    except (requests.ConnectionError, requests.Timeout):
        st.error("❌ API Server Offline")
        st.caption("Run `python run.py` to start the server")
    
    st.divider()

    # Sample questions
    st.markdown("**Try asking…**")
    samples = [
        "How many leaves do I get per year?",
        "What is sabbatical leave?",
        "How do I submit a reimbursement claim?",
        "What is Leave Without Pay?",
        "What types of leave are available?",
        "Eligibility for reimbursement?",
    ]
    for q in samples:
        if st.button(q, key=q, use_container_width=True):
            st.session_state.pending_question = q

    st.divider()

    # Policies covered
    st.markdown("**Policies covered**")
    st.markdown("📋 Leave Policy  \n💰 Reimbursement Policy")

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="brand-wrap">
  <p class="brand-title">HR Bot</p>
  <div class="brand-line"></div>
  <p class="brand-sub">Ask questions about your company's Leave &amp; Reimbursement policies.</p>
</div>
""", unsafe_allow_html=True)

# ── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── Handle sidebar sample question clicks ──────────────────────────────────────
if "pending_question" in st.session_state:
    q = st.session_state.pop("pending_question")
    send(q)
    st.rerun()

# ── Chat input ─────────────────────────────────────────────────────────────────
if question := st.chat_input("Ask an HR question…"):
    send(question)
