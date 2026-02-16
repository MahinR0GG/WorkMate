"""
Streamlit UI for HR Bot - Testing Interface
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import requests
import json

# ============================================
# Configuration
# ============================================
API_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{API_URL}/chat/"

# ============================================
# Page Config
# ============================================
st.set_page_config(
    page_title="HR Bot",
    page_icon="🤖",
    layout="centered"
)

# ============================================
# Custom CSS
# ============================================
st.markdown("""
<style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
    }
    .bot-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4CAF50;
    }
    .error-message {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# Header
# ============================================
st.title("🤖 HR Bot Assistant")
st.caption("Ask questions about Leave Policy & Reimbursement Policy")

# ============================================
# Sidebar
# ============================================
with st.sidebar:
    st.header("About")
    st.markdown("""
    **HR Bot** uses RAG (Retrieval-Augmented Generation) to answer 
    your HR policy questions.
    
    **Policies covered:**
    - 📋 Leave Policy
    - 💰 Reimbursement Policy
    
    **How it works:**
    1. Your question is converted to an embedding
    2. Similar policy chunks are retrieved via FAISS
    3. Ollama generates an answer using the context
    """)
    
    st.divider()
    
    # Health check
    st.subheader("Server Status")
    try:
        health = requests.get(f"{API_URL}/health", timeout=3)
        if health.status_code == 200:
            st.success("✅ API Server Online")
        else:
            st.error("❌ API Server Error")
    except requests.ConnectionError:
        st.error("❌ API Server Offline")
        st.caption("Run `python main.py` to start the server")
    
    st.divider()
    
    # Sample questions
    st.subheader("Sample Questions")
    sample_questions = [
        "How much leave do I get per year?",
        "What is sabbatical leave?",
        "How do I submit a reimbursement claim?",
        "What is Leave Without Pay?",
        "What types of leave are available?",
        "What are the eligibility criteria for reimbursement?",
    ]
    
    for q in sample_questions:
        if st.button(q, key=q, use_container_width=True):
            st.session_state.sample_question = q

# ============================================
# Chat History
# ============================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    
    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(content)
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(content)

# ============================================
# Handle sample question from sidebar
# ============================================
if "sample_question" in st.session_state:
    question = st.session_state.sample_question
    del st.session_state.sample_question
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)
    
    # Get bot response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    CHAT_ENDPOINT,
                    json={"question": question},
                    timeout=30
                )
                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer received")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = f"Error: {response.status_code} - {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except requests.ConnectionError:
                st.error("Cannot connect to API server. Make sure `python main.py` is running.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ============================================
# Chat Input
# ============================================
if question := st.chat_input("Ask an HR question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)
    
    # Get bot response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    CHAT_ENDPOINT,
                    json={"question": question},
                    timeout=30
                )
                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer received")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = f"Error: {response.status_code} - {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except requests.ConnectionError:
                st.error("Cannot connect to API server. Make sure `python main.py` is running.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ============================================
# Footer
# ============================================
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.caption("Powered by Ollama + FAISS")
with col2:
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
