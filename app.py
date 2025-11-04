import streamlit as st
import os
import json
import threading
from datetime import datetime
from pathlib import Path

# Import project modules
from nodes.qa_utils import (
    get_collection_stats, 
    list_available_repos,
    health_check
)
from nodes.qa_node import qa_node
from nodes.create_embeddings import create_embeddings_node
from utils.embed_utils import run_embedding_pipeline
from config import COLLECTION_NAME


# ----------------------------------------------------------------------------
# CHAT HISTORY FILE HANDLER
# ----------------------------------------------------------------------------
CHAT_HISTORY_FILE = Path("data/qa_logs/chat_history.json")

def save_chat_history_async(chat_data: list):
    """Save chat history asynchronously (non-blocking)."""
    def _save_to_file():
        CHAT_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(chat_data, f, indent=4, ensure_ascii=False)
    threading.Thread(target=_save_to_file, daemon=True).start()


# ----------------------------------------------------------------------------
# SESSION INITIALIZATION
# ----------------------------------------------------------------------------
def init_session_state():
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "selected_repo" not in st.session_state:
        st.session_state.selected_repo = None
    if "chat_history" not in st.session_state:
        if CHAT_HISTORY_FILE.exists():
            with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                st.session_state.chat_history = json.load(f)
        else:
            st.session_state.chat_history = []
    if "available_repos" not in st.session_state:
        st.session_state.available_repos = []
    if "system_initialized" not in st.session_state:
        st.session_state.system_initialized = False


# ----------------------------------------------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="PyGitHub Project Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_session_state()

st.markdown("""
<style>
.main-header {
    font-size: 2.3rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 1.5rem;
}
.qa-answer {
    background-color: #e8f4f8;
    padding: 1rem;
    border-left: 4px solid #1f77b4;
    border-radius: 6px;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# SIDEBAR CONTROLS
# ----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ System Controls")

    with st.spinner("Checking system health..."):
        health = health_check()

    if health.get('status') == 'healthy':
        st.success("✅ System Healthy")
    elif health.get('status') == 'warning':
        st.warning("⚠️ Warning")
    else:
        st.error("❌ Error in system")

    st.metric("Repos", health.get("repos_available", 0))
    st.info(f"Active Collection: **{COLLECTION_NAME}**")


# ----------------------------------------------------------------------------
# MAIN INTERFACE
# ----------------------------------------------------------------------------
st.markdown('<div class="main-header">PyGitHub Repository QA System</div>', unsafe_allow_html=True)
st.caption("Ask questions about your GitHub repositories using AI-powered search.")


# ----------------------------------------------------------------------------
# REPO SELECTION
# ----------------------------------------------------------------------------
stats = get_collection_stats()
if not stats.get("exists") or stats.get("vectors_count", 0) == 0:
    st.warning("⚠️ No embeddings found. Please run pipeline first.")
else:
    if not st.session_state.vectorstore:
        with st.spinner("Initializing vectorstore..."):
            state = create_embeddings_node({})
            st.session_state.vectorstore = state.get("vectorstore")

    if not st.session_state.available_repos:
        st.session_state.available_repos = list_available_repos()

    st.subheader("📦 Select Repository")
    selected_repo = st.selectbox(
        "Choose a repository",
        options=st.session_state.available_repos,
    )
    st.session_state.selected_repo = selected_repo
    st.divider()

    # Tabs for Chat Functions
    tab1, tab2, tab3 = st.tabs(["💬 New Chat", "🕒 Chat History", "🔍 Search Chat"])

    # ------------------------------------------------------------------------
    # TAB 1 — NEW CHAT
    # ------------------------------------------------------------------------
    with tab1:
        st.markdown("### 💬 Ask a New Question")
        question = st.text_area("Enter your question about the repository:")

        if st.button("🔍 Ask", use_container_width=True):
            if not question.strip():
                st.warning("Please enter a question before submitting.")
            else:
                with st.spinner("Generating answer..."):
                    state = {
                        "vectorstore": st.session_state.vectorstore,
                        "selected_repo": selected_repo,
                        "query": question
                    }
                    result = qa_node(state)
                    answer = result.get("qa", "No answer")

                    if isinstance(answer, str):
                        answer = [answer]

                    new_entry = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "repo": selected_repo,
                        "question": question,
                        "answer": answer,
                    }

                    st.session_state.chat_history.append(new_entry)
                    save_chat_history_async(st.session_state.chat_history)

                    st.success("✅ Answer Generated Successfully!")
                    st.markdown('<div class="qa-answer">', unsafe_allow_html=True)
                    for line in answer:
                        if line.strip() and not line.endswith(".md") and not line.startswith("📚"):
                            st.markdown(line)
                    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------------------
    # TAB 2 — CHAT HISTORY
    # ------------------------------------------------------------------------
    with tab2:
        st.markdown("### 🕒 Previous Chats")

        if st.button("🗑️ Clear All Chat History", use_container_width=True):
            st.session_state.chat_history = []
            save_chat_history_async([])
            st.success("Chat history cleared successfully!")

        if not st.session_state.chat_history:
            st.info("No previous chats available.")
        else:
            for chat in reversed(st.session_state.chat_history):
                if chat["repo"] != selected_repo:
                    continue
                st.markdown(f"**🕒 {chat['timestamp']}** | **📦 {chat['repo']}**")
                st.info(f"**❓ Question:** {chat['question']}")
                st.markdown('<div class="qa-answer">', unsafe_allow_html=True)
                for line in (chat["answer"] or ["No answer available"]):
                    if line.strip() and not line.endswith(".md") and not line.startswith("📚"):
                        st.markdown(line)
                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()

    # ------------------------------------------------------------------------
    # TAB 3 — SEARCH CHAT
    # ------------------------------------------------------------------------
    with tab3:
        st.markdown("### 🔍 Search in Chat History")
        search_query = st.text_input("Enter keyword to search:")

        if search_query.strip():
            results = [
                chat for chat in st.session_state.chat_history
                if search_query.lower() in chat["question"].lower()
                or any(search_query.lower() in ans.lower() for ans in chat["answer"])
            ]

            if results:
                st.success(f"Found {len(results)} matching results.")
                for chat in reversed(results):
                    st.markdown(f"**🕒 {chat['timestamp']}** | **📦 {chat['repo']}**")
                    st.info(f"**❓ Question:** {chat['question']}")
                    st.markdown('<div class="qa-answer">', unsafe_allow_html=True)
                    for line in chat["answer"]:
                        if line.strip() and not line.endswith(".md") and not line.startswith("📚"):
                            st.markdown(line)
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.divider()
            else:
                st.warning("No results found for your search query.")
        else:
            st.info("Type a keyword above to search through chat history.")
