import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path

# Import your existing modules
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
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="GitHub Repo QA System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .qa-answer {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .source-item {
        background-color: #f8f9fa;
        padding: 0.5rem;
        margin: 0.3rem 0;
        border-radius: 0.3rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize session state variables"""
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
# SIDEBAR - SYSTEM CONTROLS
# ============================================================================

with st.sidebar:
    st.markdown("### 🎛️ System Controls")
    
    # System Status
    st.markdown("#### 📊 System Status")
    
    with st.spinner("Checking system health..."):
        health = health_check()
    
    if health['status'] == 'healthy':
        st.success("✅ System Healthy")
    elif health['status'] == 'warning':
        st.warning("⚠️ System Warning")
    else:
        st.error("❌ System Error")
    
    # Display metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Repos", health.get('repos_available', 0))
    with col2:
        st.metric("Vectors", health.get('total_vectors', 0))
    
    st.divider()
    
    # Pipeline Controls
    st.markdown("#### 🔧 Pipeline Management")
    
    if st.button("🔄 Refresh Repositories", use_container_width=True):
        with st.spinner("Fetching repositories..."):
            st.session_state.available_repos = list_available_repos()
            st.rerun()
    
    if st.button("🏗️ Run Full Pipeline", use_container_width=True):
        st.session_state.show_pipeline = True
    
    st.divider()
    
    # Quick Actions
    st.markdown("#### ⚡ Quick Actions")
    
    if st.button("📥 Download Repos", use_container_width=True):
        with st.spinner("Downloading repositories..."):
            state = {}
            state = download_repos_node(state)
            if "Success" in state.get("status", ""):
                st.success("✅ Repositories downloaded!")
            else:
                st.error(f"❌ {state.get('status', 'Failed')}")
    
    if st.button("📝 Generate Docs", use_container_width=True):
        with st.spinner("Generating documentation..."):
            state = {}
            state = generate_docs_node(state)
            if "Success" in state.get("status", ""):
                st.success("✅ Documentation generated!")
            else:
                st.error(f"❌ {state.get('status', 'Failed')}")
    
    if st.button("🔮 Create Embeddings", use_container_width=True):
        with st.spinner("Creating embeddings (this may take a while)..."):
            result = run_embedding_pipeline(force_recreate=False)
            if "Success" in result.get("status", ""):
                st.success(f"✅ Created {result.get('total_chunks', 0)} chunks!")
                st.session_state.system_initialized = True
            else:
                st.error(f"❌ {result.get('status', 'Failed')}")
    
    st.divider()
    
    # Settings
    st.markdown("#### ⚙️ Settings")
    st.info(f"**Collection:** {COLLECTION_NAME}")

# ============================================================================
# MAIN CONTENT AREA
# ============================================================================

# Header
st.markdown('<div class="main-header">🤖 GitHub Repository QA System</div>', unsafe_allow_html=True)
st.markdown("**Ask questions about your GitHub repositories using AI-powered search**")

# ============================================================================
# TAB NAVIGATION
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs(["💬 Q&A Chat", "📚 Repositories", "🔧 Pipeline", "📊 Analytics"])

# ============================================================================
# TAB 1: Q&A CHAT
# ============================================================================

with tab1:
    # Check if system is initialized
    stats = get_collection_stats()
    
    if not stats.get("exists") or stats.get("vectors_count", 0) == 0:
        st.warning("⚠️ System not initialized. Please run the pipeline first.")
        
        if st.button("🚀 Initialize System Now"):
            with st.spinner("Running full pipeline..."):
                from graph import build_graph
                graph = build_graph()
                state = {}
                state = graph.invoke(state)
                
                if state.get("vectorstore"):
                    st.session_state.vectorstore = state["vectorstore"]
                    st.session_state.system_initialized = True
                    st.success("✅ System initialized successfully!")
                    st.rerun()
                else:
                    st.error("❌ Initialization failed. Check logs.")
    else:
        # Initialize vectorstore if needed
        if not st.session_state.vectorstore:
            with st.spinner("Connecting to vector store..."):
                state = {}
                state = create_embeddings_node(state)
                st.session_state.vectorstore = state.get("vectorstore")
        
        # Get available repos
        if not st.session_state.available_repos:
            st.session_state.available_repos = list_available_repos()
        
        if not st.session_state.available_repos:
            st.error("❌ No repositories found. Please run the pipeline.")
        else:
            # Repository Selection
            st.markdown("### 📂 Select Repository")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                selected_repo = st.selectbox(
                    "Choose a repository to ask questions about:",
                    options=st.session_state.available_repos,
                    index=0 if st.session_state.available_repos else None,
                    key="repo_selector"
                )
                st.session_state.selected_repo = selected_repo
            
            with col2:
                if st.button("ℹ️ Repo Details", use_container_width=True):
                    with st.expander("Repository Details", expanded=True):
                        display_repo_details(selected_repo)
            
            st.divider()
            
            # Question Input
            st.markdown("### ❓ Ask a Question")
            
            question = st.text_area(
                "Enter your question:",
                placeholder="e.g., What does this repository do? How do I install it? Explain the main.py file.",
                height=100,
                key="question_input"
            )
            
            col1, col2, col3 = st.columns([2, 2, 6])
            
            with col1:
                ask_button = st.button("🔍 Ask Question", type="primary", use_container_width=True)
            
            with col2:
                clear_button = st.button("🗑️ Clear History", use_container_width=True)
            
            if clear_button:
                st.session_state.chat_history = []
                st.rerun()
            
            # Process Question
            if ask_button and question.strip():
                with st.spinner("🤔 Thinking..."):
                    # Prepare state
                    state = {
                        "vectorstore": st.session_state.vectorstore,
                        "selected_repo": selected_repo,
                        "query": question
                    }
                    
                    # Get answer
                    state = qa_node(state)
                    
                    # Add to history
                    st.session_state.chat_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "repo": selected_repo,
                        "question": question,
                        "answer": state.get("qa", ["No answer generated"])
                    })
            
            # Display Chat History
            if st.session_state.chat_history:
                st.markdown("### 💬 Conversation History")
                
                # Display in reverse order (newest first)
                for idx, chat in enumerate(reversed(st.session_state.chat_history)):
                    with st.container():
                        st.markdown(f"**🕒 {chat['timestamp']}** | **📂 {chat['repo']}**")
                        
                        # Question
                        st.markdown(f"**❓ Question:**")
                        st.info(chat['question'])
                        
                        # Answer
                        st.markdown(f"**💡 Answer:**")
                        answer_lines = chat['answer']
                        
                        # Extract answer and sources
                        answer_text = []
                        sources = []
                        in_sources = False
                        
                        for line in answer_lines:
                            if "SOURCES" in line.upper() or "📚" in line:
                                in_sources = True
                                continue
                            if in_sources:
                                sources.append(line)
                            else:
                                answer_text.append(line)
                        
                        # Display answer
                        st.markdown('<div class="qa-answer">', unsafe_allow_html=True)
                        for line in answer_text:
                            if line.strip() and not line.startswith("="):
                                st.markdown(line)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Display sources
                        if sources:
                            with st.expander("📚 View Sources"):
                                for source in sources:
                                    if source.strip():
                                        st.markdown(f'<div class="source-item">{source}</div>', unsafe_allow_html=True)
                        
                        st.divider()

# ============================================================================
# TAB 2: REPOSITORIES
# ============================================================================

with tab2:
    st.markdown("### 📚 Repository Overview")
    
    if not st.session_state.available_repos:
        repos = list_available_repos()
        st.session_state.available_repos = repos
    else:
        repos = st.session_state.available_repos
    
    if not repos:
        st.warning("⚠️ No repositories found. Please run the pipeline to index repositories.")
    else:
        st.success(f"✅ Found {len(repos)} repositories")
        
        # Display in grid
        cols = st.columns(3)
        
        for idx, repo in enumerate(repos):
            with cols[idx % 3]:
                with st.container():
                    st.markdown(f"#### 📦 {repo}")
                    
                    # Get repo stats
                    from nodes.qa_utils import get_repo_document_count
                    doc_count = get_repo_document_count(repo)
                    
                    st.metric("Documents", doc_count)
                    
                    if st.button(f"View Details", key=f"details_{idx}"):
                        with st.expander(f"Details: {repo}", expanded=True):
                            display_repo_details(repo)

# ============================================================================
# TAB 3: PIPELINE
# ============================================================================

with tab3:
    st.markdown("### 🔧 Pipeline Management")
    
    st.info("**Pipeline Steps:** Download Repos → Generate Docs → Create Embeddings")
    
    # Pipeline Status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 1️⃣ Download Repos")
        repos_dir = Path("data/github_repos")
        if repos_dir.exists():
            repo_count = len([d for d in repos_dir.iterdir() if d.is_dir()])
            st.success(f"✅ {repo_count} repos downloaded")
        else:
            st.warning("⚠️ No repos directory")
    
    with col2:
        st.markdown("#### 2️⃣ Generate Docs")
        docs_dir = Path("repos_docs2")
        if docs_dir.exists():
            doc_count = len(list(docs_dir.glob("*.md")))
            st.success(f"✅ {doc_count} docs generated")
        else:
            st.warning("⚠️ No docs directory")
    
    with col3:
        st.markdown("#### 3️⃣ Embeddings")
        stats = get_collection_stats()
        if stats.get("exists") and stats.get("vectors_count", 0) > 0:
            st.success(f"✅ {stats['vectors_count']} vectors")
        else:
            st.warning("⚠️ No embeddings")
    
    st.divider()
    
    # Run Full Pipeline
    st.markdown("### 🚀 Run Complete Pipeline")
    
    st.warning("⚠️ This will run all pipeline steps. It may take several minutes.")
    
    if st.button("▶️ Start Full Pipeline", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Download
            status_text.text("📥 Step 1/3: Downloading repositories...")
            progress_bar.progress(10)
            
            state = {}
            state = download_repos_node(state)
            
            progress_bar.progress(33)
            st.success(f"✅ {state.get('status', 'Completed')}")
            
            # Step 2: Generate Docs
            status_text.text("📝 Step 2/3: Generating documentation...")
            state = generate_docs_node(state)
            
            progress_bar.progress(66)
            st.success(f"✅ {state.get('status', 'Completed')}")
            
            # Step 3: Embeddings
            status_text.text("🔮 Step 3/3: Creating embeddings...")
            result = run_embedding_pipeline(force_recreate=False)
            
            progress_bar.progress(100)
            st.success(f"✅ Pipeline completed! Created {result.get('total_chunks', 0)} chunks")
            
            status_text.text("✅ Pipeline completed successfully!")
            
            # Update session state
            st.session_state.system_initialized = True
            st.session_state.available_repos = list_available_repos()
            
        except Exception as e:
            st.error(f"❌ Pipeline failed: {str(e)}")

# ============================================================================
# TAB 4: ANALYTICS
# ============================================================================

with tab4:
    st.markdown("### 📊 System Analytics")
    
    # System Metrics
    st.markdown("#### System Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    stats = get_collection_stats()
    
    with col1:
        st.metric(
            "Total Vectors",
            stats.get("vectors_count", 0)
        )
    
    with col2:
        repos = list_available_repos()
        st.metric(
            "Repositories",
            len(repos)
        )
    
    with col3:
        docs_dir = Path("repos_docs2")
        doc_count = len(list(docs_dir.glob("*.md"))) if docs_dir.exists() else 0
        st.metric(
            "Documentation Files",
            doc_count
        )
    
    with col4:
        log_dir = Path(OUTPUT_LOG_DIR)
        log_count = len(list(log_dir.glob("*.json"))) if log_dir.exists() else 0
        st.metric(
            "QA Logs",
            log_count
        )
    
    st.divider()
    
    # Recent Activity
    st.markdown("#### 📝 Recent QA Activity")
    
    log_dir = Path(OUTPUT_LOG_DIR)
    if log_dir.exists():
        log_files = sorted(log_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:10]
        
        if log_files:
            for log_file in log_files:
                try:
                    # ✅ FIX: Specify UTF-8 encoding
                    with open(log_file, 'r', encoding='utf-8') as f:
                        log_data = json.load(f)
                    
                    with st.expander(f"🕒 {log_data['timestamp']} - {log_data['repository']}"):
                        st.markdown(f"**Question:** {log_data['query']}")
                        st.markdown(f"**Answer:** {log_data['answer'][:200]}...")
                        st.markdown(f"**Chunks Retrieved:** {len(log_data.get('retrieved_chunks', []))}")
                except Exception as e:
                    # Skip corrupted or problematic log files
                    st.warning(f"⚠️ Could not read log file: {log_file.name}")
                    continue
        else:
            st.info("No activity logs yet")
    else:
        st.info("No logs directory found")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 1rem;'>
    <p>🤖 <strong>GitHub Repository QA System</strong> | Powered by LangChain + Qdrant + Groq</p>
    <p style='font-size: 0.8rem;'>Built with Streamlit | AI-Powered Documentation Search</p>
</div>
""", unsafe_allow_html=True)