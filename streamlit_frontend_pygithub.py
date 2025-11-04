import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path

# Import modules from your project
from nodes.qa_utils import (
    get_collection_stats, 
    list_available_repos,
    display_repo_details,
    health_check
)
from nodes.qa_node import qa_node
from nodes.create_embeddings import create_embeddings_node
from nodes.download_repos import download_repos_node
from nodes.generate_docs import generate_docs_node
from utils.embed_utils import run_embedding_pipeline
from config import COLLECTION_NAME, OUTPUT_LOG_DIR


# ----------------------------------------------------------------------------
# CHAT HISTORY FILE HANDLER (threaded saving)
# ----------------------------------------------------------------------------
import threading

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
    if 'vectorstore' not in st.session_state:
        st.session_state.vectorstore = None
    if 'selected_repo' not in st.session_state:
        st.session_state.selected_repo = None
    # if 'chat_history' not in st.session_state:
    #     st.session_state.chat_history = []

    if 'chat_history' not in st.session_state:
        if CHAT_HISTORY_FILE.exists():
            with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                st.session_state.chat_history = json.load(f)
        else:
            st.session_state.chat_history = []

    if 'available_repos' not in st.session_state:
        st.session_state.available_repos = []
    if 'system_initialized' not in st.session_state:
        st.session_state.system_initialized = False


# ----------------------------------------------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="PyGitHub Project Dashboard",
    # page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ✅ Initialize session state early
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
.source-item {
    background-color: #f8f9fa;
    padding: 0.4rem;
    margin: 0.2rem 0;
    border-radius: 4px;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)






# init_session_state()


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

    st.metric("Repos", health.get('repos_available', 0))
    # st.metric("Vectors", health.get('total_vectors', 0))

    # st.divider()
    # # st.subheader("🧠 Quick Actions")

    # if st.button("📥 Download Repositories"):
    #     with st.spinner("Downloading..."):
    #         state = download_repos_node({})
    #         st.success(state.get("status", "Done"))

    # if st.button("📝 Generate Docs"):
    #     with st.spinner("Generating docs..."):
    #         state = generate_docs_node({})
    #         st.success(state.get("status", "Done"))

    # if st.button("🔮 Create Embeddings"):
    #     with st.spinner("Creating embeddings..."):
    #         result = run_embedding_pipeline(force_recreate=False)
    #         st.success(f"✅ {result.get('total_chunks', 0)} chunks created!")

    # st.divider()
    # st.info(f"Active Collection: **{COLLECTION_NAME}**")


# ----------------------------------------------------------------------------
# MAIN INTERFACE
# ----------------------------------------------------------------------------
st.markdown('<div class="main-header">PyGitHub Repository QA System</div>', unsafe_allow_html=True)
st.caption("Ask questions about your GitHub repositories using AI-powered search.")


tab1, = st.tabs(["💬 Q&A Chat"])


# ----------------------------------------------------------------------------
# TAB 1 — Q&A CHAT
# ----------------------------------------------------------------------------
with tab1:
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

        selected_repo = st.selectbox(
            "Select Repository", 
            options=st.session_state.available_repos
        )
        st.session_state.selected_repo = selected_repo

        st.divider()
        question = st.text_area("Ask a Question about the repository:")

        # if st.button("🔍 Ask"):
        #     with st.spinner("Generating answer..."):
        #         state = {
        #             "vectorstore": st.session_state.vectorstore,
        #             "selected_repo": selected_repo,
        #             "query": question
        #         }
        #         result = qa_node(state)
        #         st.session_state.chat_history.append({
        #             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        #             "repo": selected_repo,
        #             "question": question,
        #             "answer": result.get("qa", ["No answer"])
        #         })

        if st.button("🔍 Ask"):
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
                    "answer": answer
                }

                print(f"{'='*50} \nnew_entry:{new_entry} \n{'='*50}")

                st.session_state.chat_history.append(new_entry)
                save_chat_history_async(st.session_state.chat_history)

        # 🗑️ Clear history button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            save_chat_history_async([])
            st.success("Chat history cleared!")

        # 💬 Display chat history
        if st.session_state.chat_history:
            st.divider()
            st.markdown("### 💬 Chat History")
            for chat in reversed(st.session_state.chat_history):
                print(f"{'='*50} \nchat:{chat} \n{'='*50}")
                st.markdown(f"**🕒 {chat['timestamp']}** | **📦 {chat['repo']}**")
                st.info(f"**❓ Question:** {chat['question']}")
                st.markdown('<div class="qa-answer">', unsafe_allow_html=True)
                
                for line in (chat["answer"] or ["No answer available"]):
                    if not line.strip():
                        continue
                    # Skip any chunk/source/log information
                    if (
                        line.startswith("📚 SOURCES")
                        or line.startswith("💾 Interaction logged")
                        or line.strip().startswith(tuple(str(i) + "." for i in range(1, 21)))  # removes numbered chunks
                        or line.endswith(".md")  # removes any markdown source filenames
                    ):
                        continue

                    st.markdown(line)
                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()


# ----------------------------------------------------------------------------
# TAB 2 — REPOSITORIES
# ----------------------------------------------------------------------------
# with tab2:
#     st.subheader("📦 Repository Overview")

#     repos = list_available_repos()
#     if not repos:
#         st.warning("No repositories found. Please run the pipeline.")
#     else:
#         cols = st.columns(3)
#         for idx, repo in enumerate(repos):
#             with cols[idx % 3]:
#                 st.markdown(f"#### {repo}")
#                 from nodes.qa_utils import get_repo_document_count
#                 doc_count = get_repo_document_count(repo)
#                 st.metric("Documents", doc_count)
#                 if st.button(f"ℹ️ Details", key=f"repo_{idx}"):
#                     with st.expander(f"Repository: {repo}", expanded=True):
#                         display_repo_details(repo)


# # ----------------------------------------------------------------------------
# # TAB 3 — PIPELINE
# # ----------------------------------------------------------------------------
# with tab3:
#     st.subheader("🔧 Run Full Pipeline")

#     if st.button("🚀 Start Full Pipeline"):
#         progress = st.progress(0)
#         with st.spinner("Running full pipeline..."):
#             state = download_repos_node({})
#             progress.progress(33)
#             state = generate_docs_node(state)
#             progress.progress(66)
#             result = run_embedding_pipeline(force_recreate=False)
#             progress.progress(100)
#             st.success(f"✅ Completed — {result.get('total_chunks', 0)} embeddings created.")


# ----------------------------------------------------------------------------
# FOOTER
# ----------------------------------------------------------------------------
st.divider()
st.markdown("""
<div style='text-align:center; color:gray'>
    <p> <b>PyGitHub QA System</b> | Powered by LangChain + Qdrant + Streamlit</p>
</div>
""", unsafe_allow_html=True)
