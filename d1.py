# """
# GitHub Repository Q&A System - Simple Frontend
# Clean and easy-to-use interface
# """

# import streamlit as st
# import sys
# from pathlib import Path
# from datetime import datetime

# # Add project root to path
# sys.path.append(str(Path(__file__).parent))

# from nodes.qa_node import qa_node
# from nodes.qa_utils import list_available_repos, get_repo_document_count
# from nodes.create_embeddings import create_embeddings_node


# # Page configuration
# st.set_page_config(
#     page_title="GitHub Q&A",
#     page_icon="🤖",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Simple CSS
# st.markdown("""
#     <style>
#     .main { background-color: #f8f9fa; }
#     .sidebar .sidebar-content { background-color: #ffffff; }
#     .chat-user { background-color: #e3f2fd; padding: 12px; border-radius: 10px; margin: 5px 0; }
#     .chat-bot { background-color: #f5f5f5; padding: 12px; border-radius: 10px; margin: 5px 0; }
#     </style>
# """, unsafe_allow_html=True)

# # Initialize session state
# if 'chat_history' not in st.session_state:
#     st.session_state.chat_history = []
# if 'vectorstore' not in st.session_state:
#     st.session_state.vectorstore = None
# if 'selected_repo' not in st.session_state:
#     st.session_state.selected_repo = None

# def init_system():
#     """Initialize the Q&A system"""
#     if st.session_state.vectorstore is None:
#         with st.spinner("Loading AI system..."):
#             try:
#                 state = create_embeddings_node({})
#                 st.session_state.vectorstore = state.get("vectorstore")
#                 return True
#             except Exception as e:
#                 st.error(f"Failed to initialize: {str(e)}")
#                 return False
#     return True

# def get_answer(question, repo_name):
#     """Get answer for a question"""
#     try:
#         state = {
#             "selected_repo": repo_name,
#             "query": question,
#             "vectorstore": st.session_state.vectorstore
#         }
        
#         result = qa_node(state)
#         qa_response = result.get("qa", [])
        
#         if qa_response:
#             # Extract answer (skip sources for simplicity)
#             answer_lines = []
#             for line in qa_response:
#                 if line.strip() and not any(x in line for x in ["Sources:", "📚", "📂"]):
#                     answer_lines.append(line)
#             return "\n".join(answer_lines)
#         return "Sorry, I couldn't find an answer."
        
#     except Exception as e:
#         return f"Error: {str(e)}"

# # Sidebar
# with st.sidebar:
#     st.title("🤖 GitHub Q&A")
#     st.markdown("---")
    
#     # System status
#     if st.session_state.vectorstore:
#         st.success("✅ System Ready")
#     else:
#         st.warning("⚠️ System Not Loaded")
    
#     # Initialize button
#     if st.button("🔄 Initialize System", use_container_width=True):
#         init_system()
#         st.rerun()
    
#     st.markdown("---")
    
#     # Repository selection
#     st.subheader("📚 Repositories")
    
#     repos = list_available_repos()
#     if repos:
#         selected = st.selectbox(
#             "Choose a repository:",
#             options=repos,
#             index=repos.index(st.session_state.selected_repo) if st.session_state.selected_repo in repos else 0
#         )
        
#         if selected != st.session_state.selected_repo:
#             st.session_state.selected_repo = selected
#             st.session_state.chat_history = []
#             st.rerun()
        
#         if st.session_state.selected_repo:
#             doc_count = get_repo_document_count(st.session_state.selected_repo)
#             st.info(f"📄 {doc_count} chunks loaded")
#     else:
#         st.error("No repositories found")
#         st.info("Run: python main.py")

# # Main content
# st.title("GitHub Repository Q&A Assistant")

# if not st.session_state.vectorstore:
#     st.warning("Please initialize the system first using the sidebar button.")
#     st.info("""
#     **How to use:**
#     1. Click 'Initialize System' in sidebar
#     2. Select a repository
#     3. Start asking questions!
#     """)
    
# elif not st.session_state.selected_repo:
#     st.info("Please select a repository from the sidebar to start chatting.")
    
# else:
#     st.success(f"💬 Chatting with: **{st.session_state.selected_repo}**")
    
#     # Display chat history
#     for chat in st.session_state.chat_history:
#         st.markdown(f'<div class="chat-user"><strong>You:</strong> {chat["question"]}</div>', unsafe_allow_html=True)
#         st.markdown(f'<div class="chat-bot"><strong>Assistant:</strong> {chat["answer"]}</div>', unsafe_allow_html=True)
    
#     # Question input
#     st.markdown("---")
#     question = st.text_input("Ask a question about the repository:", placeholder="e.g., What is the main purpose of this project?")
    
#     col1, col2, col3 = st.columns([1, 1, 1])
    
#     with col1:
#         if st.button("🚀 Ask", use_container_width=True) and question:
#             with st.spinner("Thinking..."):
#                 answer = get_answer(question, st.session_state.selected_repo)
#                 st.session_state.chat_history.append({
#                     "question": question,
#                     "answer": answer
#                 })
#                 st.rerun()
    
#     with col2:
#         if st.button("🗑️ Clear Chat", use_container_width=True):
#             st.session_state.chat_history = []
#             st.rerun()
    
#     with col3:
#         if st.button("🔄 Change Repo", use_container_width=True):
#             st.session_state.selected_repo = None
#             st.rerun()

# # Footer
# st.markdown("---")
# st.markdown("*Simple GitHub Q&A System - Ask questions about your repositories*")


import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path

# Import your existing project modules
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


# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="🐍 PyGitHub Project Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.4rem;
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


# ============================================================================
# SESSION INITIALIZATION
# ============================================================================
def init_session_state():
    if 'vectorstore' not in st.session_state:
        st.session_state.vectorstore = None
    if 'selected_repo' not in st.session_state:
        st.session_state.selected_repo = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'available_repos' not in st.session_state:
        st.session_state.available_repos = []
    if 'system_initialized' not in st.session_state:
        st.session_state.system_initialized = False

init_session_state()


# ============================================================================
# SIDEBAR - CONTROLS
# ============================================================================
with st.sidebar:
    st.header("⚙️ System Controls")

    with st.spinner("Checking system health..."):
        health = health_check()

    # Display health status
    if health.get('status') == 'healthy':
        st.success("✅ System Healthy")
    elif health.get('status') == 'warning':
        st.warning("⚠️ System Warning")
    else:
        st.error("❌ System Error")

    st.metric("Repos", health.get('repos_available', 0))
    st.metric("Vectors", health.get('total_vectors', 0))

    st.divider()
    st.subheader("⚡ Quick Actions")

    if st.button("📥 Download Repositories"):
        with st.spinner("Downloading repositories..."):
            state = download_repos_node({})
            st.success(state.get("status", "Completed!"))

    if st.button("📝 Generate Docs"):
        with st.spinner("Generating documentation..."):
            state = generate_docs_node({})
            st.success(state.get("status", "Completed!"))

    if st.button("🔮 Create Embeddings"):
        with st.spinner("Creating embeddings..."):
            result = run_embedding_pipeline(force_recreate=False)
            st.success(f"✅ {result.get('total_chunks', 0)} chunks created!")

    st.divider()
    st.info(f"Active Collection: **{COLLECTION_NAME}**")


# ============================================================================
# MAIN CONTENT AREA
# ============================================================================
st.markdown('<div class="main-header">🐍 PyGitHub Repository QA System</div>', unsafe_allow_html=True)
st.caption("Ask questions about your GitHub repositories using AI-powered search and embeddings.")


tab1, tab2, tab3 = st.tabs(["💬 Q&A Chat", "📚 Repositories", "🚀 Pipeline"])


# ============================================================================
# TAB 1 — Q&A CHAT
# ============================================================================
with tab1:
    stats = get_collection_stats()

    if not stats.get("exists") or stats.get("vectors_count", 0) == 0:
        st.warning("⚠️ No embeddings found. Please run the pipeline first.")
    else:
        # Initialize vectorstore if not already done
        if not st.session_state.vectorstore:
            with st.spinner("Initializing vectorstore..."):
                state = create_embeddings_node({})
                st.session_state.vectorstore = state.get("vectorstore")

        # Load repositories
        if not st.session_state.available_repos:
            st.session_state.available_repos = list_available_repos()

        # Repo selection
        selected_repo = st.selectbox("Select Repository", st.session_state.available_repos)
        st.session_state.selected_repo = selected_repo

        st.divider()
        question = st.text_area("Ask a Question about this repository:")

        if st.button("🔍 Ask Question"):
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Thinking..."):
                    state = {
                        "vectorstore": st.session_state.vectorstore,
                        "selected_repo": selected_repo,
                        "query": question
                    }
                    result = qa_node(state)
                    st.session_state.chat_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "repo": selected_repo,
                        "question": question,
                        "answer": result.get("qa", ["No answer generated"])
                    })
                    st.success("✅ Answer generated!")

        # Display chat history
        if st.session_state.chat_history:
            st.divider()
            st.markdown("### 💬 Chat History")
            for chat in reversed(st.session_state.chat_history):
                st.markdown(f"**🕒 {chat['timestamp']}** | **📦 {chat['repo']}**")
                st.info(f"**❓ Question:** {chat['question']}")
                st.markdown('<div class="qa-answer">', unsafe_allow_html=True)
                for line in chat["answer"]:
                    st.markdown(line)
                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()


# ============================================================================
# TAB 2 — REPOSITORIES
# ============================================================================
with tab2:
    st.subheader("📚 Repository Overview")

    repos = list_available_repos()
    if not repos:
        st.warning("⚠️ No repositories found. Please run the pipeline.")
    else:
        cols = st.columns(3)
        for idx, repo in enumerate(repos):
            with cols[idx % 3]:
                st.markdown(f"#### 📦 {repo}")
                from nodes.qa_utils import get_repo_document_count
                doc_count = get_repo_document_count(repo)
                st.metric("Documents", doc_count)
                if st.button(f"ℹ️ Details", key=f"repo_{idx}"):
                    with st.expander(f"Repository Details: {repo}", expanded=True):
                        display_repo_details(repo)


# ============================================================================
# TAB 3 — PIPELINE MANAGEMENT
# ============================================================================
with tab3:
    st.subheader("🚀 Full Pipeline Execution")

    st.markdown("""
    This will:
    1️⃣ Download repositories  
    2️⃣ Generate documentation  
    3️⃣ Create embeddings
    """)

    if st.button("▶️ Start Full Pipeline", type="primary"):
        progress = st.progress(0)
        status_text = st.empty()

        try:
            # Step 1: Download
            status_text.text("📥 Step 1/3: Downloading repositories...")
            progress.progress(20)
            state = download_repos_node({})

            # Step 2: Docs
            status_text.text("📝 Step 2/3: Generating documentation...")
            progress.progress(50)
            state = generate_docs_node(state)

            # Step 3: Embeddings
            status_text.text("🔮 Step 3/3: Creating embeddings...")
            progress.progress(80)
            result = run_embedding_pipeline(force_recreate=False)

            progress.progress(100)
            st.success(f"✅ Completed — {result.get('total_chunks', 0)} embeddings created!")
            st.session_state.system_initialized = True
            st.session_state.available_repos = list_available_repos()

        except Exception as e:
            st.error(f"❌ Pipeline failed: {str(e)}")


# ============================================================================
# FOOTER
# ============================================================================
st.divider()
st.markdown("""
<div style='text-align:center; color:gray;'>
    <p>🐍 <b>PyGitHub QA System</b> | Powered by LangChain + Qdrant + Streamlit</p>
    <p style='font-size:0.85rem;'>Built with ❤️ for intelligent code search</p>
</div>
""", unsafe_allow_html=True)

