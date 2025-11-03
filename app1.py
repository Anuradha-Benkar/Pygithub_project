import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path

# Import project modules
from nodes.qa_utils import (
    get_collection_stats,
    list_available_repos,
    display_repo_details,
    health_check,
    get_repo_document_count,
)
from nodes.qa_node import qa_node
from nodes.create_embeddings import create_embeddings_node
from nodes.download_repos import download_repos_node
from nodes.generate_docs import generate_docs_node
from utils.embed_utils import run_embedding_pipeline
from config import COLLECTION_NAME, OUTPUT_LOG_DIR


# ======================================================================
# 🔧 PAGE CONFIGURATION
# ======================================================================
st.set_page_config(
    page_title="GitHub Repo QA System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ======================================================================
# 🎨 GLOBAL STYLES (PROFESSIONAL THEME)
# ======================================================================
st.markdown("""
<style>
    body {
        background-color: #f7f9fc;
        color: #1a1a1a;
        font-family: 'Inter', sans-serif;
    }
    .main-header {
        text-align: center;
        font-size: 2.8rem;
        color: #0d6efd;
        font-weight: 800;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        font-size: 1.1rem;
        color: #495057;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #ffffff;
        padding: 1rem;
        border-radius: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .qa-box {
        background-color: #e7f1ff;
        border-left: 4px solid #0d6efd;
        padding: 1rem;
        border-radius: 0.6rem;
    }
    .source-tag {
        font-size: 0.85rem;
        color: #6c757d;
        background: #f8f9fa;
        border-radius: 0.4rem;
        padding: 0.3rem 0.6rem;
        display: inline-block;
        margin-right: 0.3rem;
    }
    footer {
        text-align: center;
        color: gray;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)


# ======================================================================
# 🧠 SESSION INITIALIZATION
# ======================================================================
def init_session():
    defaults = {
        "vectorstore": None,
        "selected_repo": None,
        "chat_history": [],
        "available_repos": [],
        "system_initialized": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session()


# ======================================================================
# 🧰 SIDEBAR - SYSTEM MANAGEMENT
# ======================================================================
with st.sidebar:
    st.title("⚙️ System Controls")

    st.markdown("#### 📊 System Health")
    with st.spinner("Checking system health..."):
        health = health_check()

    status_color = {
        "healthy": st.success,
        "warning": st.warning,
        "error": st.error,
    }.get(health.get("status", "warning"), st.warning)

    status_color(f"System Status: **{health.get('status', 'Unknown')}**")

    st.metric("Repositories", health.get("repos_available", 0))
    st.metric("Vectors", health.get("total_vectors", 0))

    st.divider()
    st.markdown("#### 🧩 Pipeline Management")

    if st.button("🔄 Refresh Repositories", use_container_width=True):
        st.session_state.available_repos = list_available_repos()
        st.rerun()

    if st.button("🏗️ Run Full Pipeline", use_container_width=True):
        st.session_state.show_pipeline = True

    st.divider()
    st.markdown("#### ⚙️ Pipeline Steps")

    actions = {
        "📥 Download Repos": download_repos_node,
        "📝 Generate Docs": generate_docs_node,
        "🔮 Create Embeddings": lambda _: run_embedding_pipeline(force_recreate=False),
    }

    for label, func in actions.items():
        if st.button(label, use_container_width=True):
            with st.spinner(f"{label}..."):
                try:
                    result = func({})
                    st.success(f"✅ {label} completed successfully!")
                except Exception as e:
                    st.error(f"❌ {label} failed: {e}")

    st.divider()
    st.info(f"🧠 Active Collection: **{COLLECTION_NAME}**")


# ======================================================================
# 🧠 MAIN INTERFACE
# ======================================================================
st.markdown("<div class='main-header'>🤖 GitHub Repository QA System</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Ask intelligent questions about your repositories using AI</div>", unsafe_allow_html=True)

tabs = st.tabs(["💬 Chat Assistant", "📚 Repositories", "📈 Analytics", "🚀 Pipeline"])


# ======================================================================
# 💬 CHAT TAB
# ======================================================================
with tabs[0]:
    stats = get_collection_stats()
    if not stats.get("exists") or stats.get("vectors_count", 0) == 0:
        st.warning("⚠️ System not initialized. Please run the full pipeline.")
        if st.button("🚀 Initialize System"):
            from graph import build_graph
            with st.spinner("Building system graph..."):
                graph = build_graph()
                state = graph.invoke({})
            if state.get("vectorstore"):
                st.session_state.vectorstore = state["vectorstore"]
                st.session_state.system_initialized = True
                st.success("✅ Initialization complete!")
                st.rerun()
    else:
        if not st.session_state.available_repos:
            st.session_state.available_repos = list_available_repos()

        repo = st.selectbox("📦 Select Repository", options=st.session_state.available_repos)
        question = st.text_area("💭 Ask a Question", placeholder="e.g. Explain the purpose of app.py")

        if st.button("🔍 Get Answer"):
            with st.spinner("Thinking..."):
                try:
                    state = {
                        "vectorstore": st.session_state.vectorstore,
                        "selected_repo": repo,
                        "query": question,
                    }
                    result = qa_node(state)
                    answer = "\n".join(result.get("qa", ["No response"]))
                    st.session_state.chat_history.append({
                        "repo": repo,
                        "question": question,
                        "answer": answer,
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                    })
                    st.success("✅ Answer ready below!")
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.chat_history:
            st.divider()
            st.markdown("### 🕒 Recent Conversations")
            for chat in reversed(st.session_state.chat_history):
                st.markdown(f"**[{chat['timestamp']}]** 📂 *{chat['repo']}*")
                st.info(f"**Q:** {chat['question']}")
                st.markdown(f"<div class='qa-box'>{chat['answer']}</div>", unsafe_allow_html=True)


# ======================================================================
# 📚 REPOSITORIES TAB
# ======================================================================
with tabs[1]:
    repos = list_available_repos()
    if not repos:
        st.warning("No repositories found. Run pipeline to fetch.")
    else:
        st.markdown(f"**Available Repositories:** {len(repos)}")
        for repo in repos:
            with st.expander(f"📦 {repo}"):
                doc_count = get_repo_document_count(repo)
                st.metric("Documents", doc_count)
                display_repo_details(repo)


# ======================================================================
# 📈 ANALYTICS TAB
# ======================================================================
with tabs[2]:
    stats = get_collection_stats()
    st.metric("Total Vectors", stats.get("vectors_count", 0))
    st.metric("Repositories Indexed", len(list_available_repos()))
    log_dir = Path(OUTPUT_LOG_DIR)
    if log_dir.exists():
        st.markdown("#### 📝 Recent Logs")
        for log in sorted(log_dir.glob("*.json"), reverse=True)[:5]:
            with open(log, "r", encoding="utf-8") as f:
                data = json.load(f)
            st.markdown(f"🕒 {data['timestamp']} | **{data['repository']}**")
            st.caption(f"Q: {data['query']}")
            st.text_area("Answer", data['answer'], height=100)


# ======================================================================
# 🚀 PIPELINE TAB
# ======================================================================
with tabs[3]:
    st.info("Run the full pipeline (download → docs → embeddings)")
    if st.button("▶️ Execute Full Pipeline", type="primary"):
        try:
            with st.spinner("Executing pipeline..."):
                s1 = download_repos_node({})
                s2 = generate_docs_node(s1)
                res = run_embedding_pipeline()
            st.success(f"✅ Pipeline complete! {res.get('total_chunks', 0)} chunks created.")
        except Exception as e:
            st.error(f"Pipeline failed: {e}")


# ======================================================================
# 🧾 FOOTER
# ======================================================================
st.markdown("""
<footer>
    🤖 <strong>GitHub Repository QA System</strong> | Built with ❤️ using Streamlit, LangChain & Qdrant
</footer>
""", unsafe_allow_html=True)
