# """
# Streamlit Frontend for GitHub Repository Q&A System
# ====================================================
# Production-level interface for querying repository documentation.
# """

# import streamlit as st
# import os
# import sys
# from pathlib import Path

# # Add project root to path
# sys.path.append(str(Path(__file__).parent))

# from nodes.qa_node import qa_node
# from nodes.qa_utils import (
#     list_available_repos, 
#     get_collection_stats, 
#     display_repo_details,
#     get_repo_document_count
# )
# from nodes.create_embeddings import create_embeddings_node
# from config import COLLECTION_NAME


# # ============================================================================
# # PAGE CONFIGURATION
# # ============================================================================

# st.set_page_config(
#     page_title="GitHub Repo Q&A",
#     page_icon="🤖",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )


# # ============================================================================
# # CUSTOM CSS
# # ============================================================================

# def load_custom_css():
#     """Apply custom styling"""
#     st.markdown("""
#         <style>
#         /* Import Google Fonts */
#         @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
#         /* Global Styles */
#         * {
#             font-family: 'Inter', sans-serif;
#         }
        
#         .main {
#             padding: 2rem 3rem;
#             background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
#         }
        
#         /* Header Styles */
#         h1 {
#             color: #1a1a2e;
#             font-weight: 700;
#             padding-bottom: 1.5rem;
#             border-bottom: 4px solid #0f3460;
#             margin-bottom: 2rem;
#             text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
#         }
        
#         h2 {
#             color: #16213e;
#             font-weight: 600;
#             margin-top: 2rem;
#             margin-bottom: 1rem;
#         }
        
#         h3 {
#             color: #0f3460;
#             font-weight: 500;
#         }
        
#         /* Card Styles */
#         .info-card {
#             background: white;
#             padding: 1.5rem;
#             border-radius: 12px;
#             box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#             margin: 1rem 0;
#             transition: transform 0.3s, box-shadow 0.3s;
#         }
        
#         .info-card:hover {
#             transform: translateY(-5px);
#             box-shadow: 0 8px 15px rgba(0,0,0,0.2);
#         }
        
#         /* Sidebar Styles */
#         .css-1d391kg, [data-testid="stSidebar"] {
#             background: linear-gradient(180deg, #0f3460 0%, #16213e 100%);
#             padding: 2rem 1rem;
#         }
        
#         [data-testid="stSidebar"] * {
#             color: white !important;
#         }
        
#         /* Button Styles */
#         .stButton>button {
#             width: 100%;
#             border-radius: 10px;
#             padding: 0.75rem 1.5rem;
#             font-weight: 600;
#             border: none;
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             color: white;
#             transition: all 0.3s;
#             box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#         }
        
#         .stButton>button:hover {
#             transform: translateY(-3px);
#             box-shadow: 0 6px 12px rgba(0,0,0,0.2);
#             background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
#         }
        
#         /* Input Styles */
#         .stTextInput>div>div>input {
#             border-radius: 10px;
#             border: 2px solid #e0e0e0;
#             padding: 0.75rem 1rem;
#             font-size: 1rem;
#             transition: border-color 0.3s;
#         }
        
#         .stTextInput>div>div>input:focus {
#             border-color: #667eea;
#             box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
#         }
        
#         /* Selectbox Styles */
#         .stSelectbox>div>div>select {
#             border-radius: 10px;
#             border: 2px solid #e0e0e0;
#             padding: 0.75rem 1rem;
#         }
        
#         /* Metric Styles */
#         [data-testid="stMetric"] {
#             background: white;
#             padding: 1.5rem;
#             border-radius: 12px;
#             box-shadow: 0 2px 8px rgba(0,0,0,0.1);
#             border-left: 5px solid #667eea;
#         }
        
#         [data-testid="stMetricValue"] {
#             font-size: 2rem;
#             font-weight: 700;
#             color: #0f3460;
#         }
        
#         /* Chat Message Styles */
#         .user-message {
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             color: white;
#             padding: 1.5rem;
#             border-radius: 15px;
#             margin: 1rem 0;
#             box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#             animation: slideInRight 0.3s ease-out;
#         }
        
#         .bot-message {
#             background: white;
#             padding: 1.5rem;
#             border-radius: 15px;
#             margin: 1rem 0;
#             box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#             border-left: 5px solid #4caf50;
#             animation: slideInLeft 0.3s ease-out;
#         }
        
#         @keyframes slideInRight {
#             from {
#                 opacity: 0;
#                 transform: translateX(50px);
#             }
#             to {
#                 opacity: 1;
#                 transform: translateX(0);
#             }
#         }
        
#         @keyframes slideInLeft {
#             from {
#                 opacity: 0;
#                 transform: translateX(-50px);
#             }
#             to {
#                 opacity: 1;
#                 transform: translateX(0);
#             }
#         }
        
#         /* Alert Styles */
#         .stAlert {
#             border-radius: 12px;
#             border: none;
#             box-shadow: 0 2px 8px rgba(0,0,0,0.1);
#         }
        
#         /* Expander Styles */
#         .streamlit-expanderHeader {
#             background-color: #f8f9fa;
#             border-radius: 10px;
#             font-weight: 600;
#         }
        
#         /* Divider */
#         hr {
#             margin: 2rem 0;
#             border: none;
#             height: 2px;
#             background: linear-gradient(90deg, transparent, #667eea, transparent);
#         }
        
#         /* Code blocks */
#         code {
#             background-color: #f5f5f5;
#             padding: 4px 8px;
#             border-radius: 6px;
#             font-family: 'Courier New', monospace;
#             color: #e83e8c;
#         }
        
#         /* Spinner */
#         .stSpinner > div {
#             border-color: #667eea !important;
#         }
        
#         /* Success/Error/Warning */
#         .element-container:has(.stSuccess) {
#             animation: fadeIn 0.5s ease-in;
#         }
        
#         @keyframes fadeIn {
#             from { opacity: 0; }
#             to { opacity: 1; }
#         }
#         </style>
#     """, unsafe_allow_html=True)


# # ============================================================================
# # SESSION STATE INITIALIZATION
# # ============================================================================

# def initialize_session_state():
#     """Initialize session state variables"""
#     defaults = {
#         'initialized': False,
#         'vectorstore': None,
#         'available_repos': [],
#         'chat_history': [],
#         'current_repo': None,
#         'collection_stats': None,
#         'show_stats': False
#     }
    
#     for key, value in defaults.items():
#         if key not in st.session_state:
#             st.session_state[key] = value


# # ============================================================================
# # SYSTEM INITIALIZATION
# # ============================================================================

# @st.cache_resource(show_spinner=False)
# def initialize_system():
#     """Initialize vectorstore connection - cached for performance"""
#     try:
#         state = {}
#         state = create_embeddings_node(state)
#         return state.get("vectorstore"), None
#     except Exception as e:
#         return None, str(e)


# @st.cache_data(ttl=60, show_spinner=False)
# def get_cached_repos():
#     """Get available repositories - cached for 60 seconds"""
#     try:
#         return list_available_repos(), None
#     except Exception as e:
#         return [], str(e)


# @st.cache_data(ttl=60, show_spinner=False)
# def get_cached_stats():
#     """Get collection statistics - cached for 60 seconds"""
#     try:
#         return get_collection_stats(), None
#     except Exception as e:
#         return None, str(e)


# # ============================================================================
# # UI COMPONENTS
# # ============================================================================

# def render_header():
#     """Render application header"""
#     col1, col2 = st.columns([5, 1])
    
#     with col1:
#         st.title("🤖 GitHub Repository Q&A Assistant")
#         st.markdown("**Powered by AI | Ask intelligent questions about your repositories**")
    
#     with col2:
#         if st.button("🔄 Refresh", use_container_width=True, key="header_refresh"):
#             st.cache_data.clear()
#             st.cache_resource.clear()
#             st.rerun()


# def render_sidebar():
#     """Render sidebar with system info and settings"""
#     with st.sidebar:
#         # Logo/Icon
#         st.markdown("""
#             <div style='text-align: center; padding: 1rem 0;'>
#                 <h1 style='color: white; margin: 0;'>📚</h1>
#                 <h3 style='color: white; margin: 0.5rem 0;'>System Dashboard</h3>
#             </div>
#         """, unsafe_allow_html=True)
        
#         st.divider()
        
#         # System Status
#         st.subheader("📊 System Status")
        
#         stats, error = get_cached_stats()
        
#         if error:
#             st.error(f"Error: {error}")
#         elif stats and stats.get("exists"):
#             st.success("✅ System Online")
            
#             # Metrics
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.metric("📦 Collection", COLLECTION_NAME[:15] + "...")
#             with col2:
#                 st.metric("🔢 Vectors", f"{stats.get('vectors_count', 0):,}")
            
#             repos, _ = get_cached_repos()
#             st.metric("📚 Repositories", len(repos))
            
#         else:
#             st.error("❌ Not Connected")
#             st.info("💡 Run: `python main.py`")
        
#         st.divider()
        
#         # Repository List
#         st.subheader("📁 Available Repos")
#         repos, error = get_cached_repos()
        
#         if error:
#             st.error(f"Error: {error}")
#         elif repos:
#             for repo in repos:
#                 doc_count = get_repo_document_count(repo)
#                 with st.expander(f"📂 {repo}", expanded=False):
#                     st.write(f"**Documents:** {doc_count:,}")
#                     if st.button("Select", key=f"sidebar_select_{repo}", use_container_width=True):
#                         st.session_state.current_repo = repo
#                         st.rerun()
#         else:
#             st.warning("No repositories found")
        
#         st.divider()
        
#         # Quick Stats
#         if st.session_state.chat_history:
#             st.subheader("💬 Session Stats")
#             st.metric("Questions Asked", len(st.session_state.chat_history))
        
#         # Footer
#         st.markdown("""
#             <div style='text-align: center; padding-top: 2rem; color: #ccc; font-size: 0.8rem;'>
#                 <p>Version 2.0</p>
#                 <p>© 2024 GitHub Q&A</p>
#             </div>
#         """, unsafe_allow_html=True)


# def render_repository_selector():
#     """Render repository selection"""
#     st.subheader("📂 Select Repository")
    
#     repos, error = get_cached_repos()
    
#     if error:
#         st.error(f"❌ Error loading repositories: {error}")
#         return None
    
#     if not repos:
#         st.warning("⚠️ No repositories available")
#         st.code("python main.py", language="bash")
#         return None
    
#     # Repository selection
#     col1, col2 = st.columns([3, 1])
    
#     with col1:
#         selected_repo = st.selectbox(
#             "Choose a repository:",
#             options=repos,
#             index=repos.index(st.session_state.current_repo) if st.session_state.current_repo in repos else 0,
#             key="repo_selector",
#             label_visibility="collapsed"
#         )
    
#     with col2:
#         if st.button("📊 Details", use_container_width=True, key="repo_details"):
#             st.session_state.show_stats = not st.session_state.get('show_stats', False)
    
#     if selected_repo != st.session_state.current_repo:
#         st.session_state.current_repo = selected_repo
#         st.session_state.chat_history = []
    
#     # Display repository info in cards
#     if selected_repo:
#         col1, col2, col3 = st.columns(3)
        
#         with col1:
#             st.metric("📁 Repository", selected_repo)
        
#         with col2:
#             doc_count = get_repo_document_count(selected_repo)
#             st.metric("📄 Chunks", f"{doc_count:,}")
        
#         with col3:
#             st.metric("🔍 Status", "✅ Ready")
    
#     return selected_repo


# def render_chat_interface(repo_name):
#     """Render chat interface"""
#     st.subheader("💬 Ask Your Questions")
    
#     # Chat History Display
#     if st.session_state.chat_history:
#         st.markdown("### 📜 Conversation")
        
#         for i, chat in enumerate(st.session_state.chat_history):
#             # User Question
#             st.markdown(
#                 f"""<div class="user-message">
#                     <strong>👤 You:</strong><br>
#                     {chat["question"]}
#                 </div>""",
#                 unsafe_allow_html=True
#             )
            
#             # Bot Answer
#             st.markdown(
#                 f"""<div class="bot-message">
#                     <strong>🤖 Assistant:</strong><br>
#                     {chat["answer"]}
#                 </div>""",
#                 unsafe_allow_html=True
#             )
            
#             # Sources
#             if chat.get("sources"):
#                 with st.expander("📚 View Sources", expanded=False):
#                     for j, source in enumerate(chat["sources"][:5], 1):
#                         st.markdown(f"**{j}.** `{source}`")
            
#             if i < len(st.session_state.chat_history) - 1:
#                 st.markdown("<br>", unsafe_allow_html=True)
        
#         st.divider()
    
#     # Question Input Form
#     with st.form(key="question_form", clear_on_submit=True):
#         user_question = st.text_input(
#             "Your question:",
#             placeholder=f"Ask anything about {repo_name}...",
#             key="question_input"
#         )
        
#         col1, col2 = st.columns([4, 1])
#         with col1:
#             submit_button = st.form_submit_button("🚀 Ask Question", use_container_width=True)
#         with col2:
#             clear_button = st.form_submit_button("🗑️ Clear", use_container_width=True)
    
#     # Example Questions (OUTSIDE the form)
#     with st.expander("💡 Example Questions", expanded=False):
#         st.markdown("**Click any example to use it:**")
#         examples = [
#             "What is the main purpose of this repository?",
#             "How do I install and set up this project?",
#             "What are the key features?",
#             "What dependencies does this project use?",
#             "How is the code structured?",
#             "Are there any API endpoints?",
#             "What technologies are used?"
#         ]
        
#         cols = st.columns(2)
#         for idx, example in enumerate(examples):
#             with cols[idx % 2]:
#                 if st.button(f"💬 {example}", key=f"ex_{idx}", use_container_width=True):
#                     st.session_state.pending_question = example
#                     st.rerun()
    
#     # Handle example question
#     if hasattr(st.session_state, 'pending_question'):
#         user_question = st.session_state.pending_question
#         delattr(st.session_state, 'pending_question')
#         submit_button = True
    
#     # Handle clear
#     if clear_button:
#         st.session_state.chat_history = []
#         st.rerun()
    
#     # Process question
#     if submit_button and user_question:
#         with st.spinner("🔍 Analyzing repository..."):
#             answer, sources = process_question(repo_name, user_question)
            
#             if answer:
#                 st.session_state.chat_history.append({
#                     "question": user_question,
#                     "answer": answer,
#                     "sources": sources,
#                     "repo": repo_name
#                 })
#                 st.rerun()
#             else:
#                 st.error("❌ Failed to generate answer. Please try again.")


# def process_question(repo_name, question):
#     """Process user question and get answer"""
#     try:
#         state = {
#             "selected_repo": repo_name,
#             "query": question,
#             "vectorstore": st.session_state.vectorstore
#         }
        
#         result_state = qa_node(state)
#         qa_response = result_state.get("qa", [])
        
#         if not qa_response:
#             return None, []
        
#         # Parse response
#         answer_text = []
#         sources = []
#         in_sources_section = False
        
#         for line in qa_response:
#             if "Sources" in line or "📚" in line:
#                 in_sources_section = True
#                 continue
            
#             if in_sources_section:
#                 if line.strip() and any(line.strip().startswith(f"{i}.") for i in range(1, 10)):
#                     source = line.strip().split(".", 1)[1].strip() if "." in line else line.strip()
#                     sources.append(source)
#             else:
#                 if line.strip() and not line.startswith("📂"):
#                     answer_text.append(line)
        
#         answer = "\n".join(answer_text).strip()
#         return answer, sources
        
#     except Exception as e:
#         st.error(f"Error: {e}")
#         return None, []


# def render_quick_actions():
#     """Render quick action buttons"""
#     st.subheader("⚡ Quick Actions")
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat"):
#             st.session_state.chat_history = []
#             st.success("✅ Chat cleared!")
#             st.rerun()
    
#     with col2:
#         if st.session_state.chat_history:
#             chat_text = "\n\n".join([
#                 f"Q: {chat['question']}\nA: {chat['answer']}\n{'-'*50}"
#                 for chat in st.session_state.chat_history
#             ])
#             st.download_button(
#                 "📥 Export Chat",
#                 data=chat_text,
#                 file_name=f"chat_{st.session_state.current_repo}.txt",
#                 mime="text/plain",
#                 use_container_width=True,
#                 key="export_chat"
#             )
#         else:
#             st.button("📥 Export Chat", disabled=True, use_container_width=True)
    
#     with col3:
#         if st.button("📊 Toggle Stats", use_container_width=True, key="toggle_stats"):
#             st.session_state.show_stats = not st.session_state.get('show_stats', False)
#             st.rerun()


# def render_statistics():
#     """Render detailed statistics"""
#     if st.session_state.get('show_stats', False):
#         st.subheader("📊 Detailed Statistics")
        
#         stats, _ = get_cached_stats()
#         repos, _ = get_cached_repos()
        
#         col1, col2, col3, col4 = st.columns(4)
        
#         with col1:
#             st.metric("📚 Total Repos", len(repos))
        
#         with col2:
#             st.metric("🔢 Total Vectors", f"{stats.get('vectors_count', 0):,}")
        
#         with col3:
#             st.metric("💬 Questions", len(st.session_state.chat_history))
        
#         with col4:
#             status = "🟢 Active" if st.session_state.vectorstore else "🔴 Inactive"
#             st.metric("⚡ Session", status)
        
#         # Repository breakdown
#         if repos:
#             st.markdown("### 📁 Repository Details")
            
#             repo_data = []
#             for repo in repos:
#                 doc_count = get_repo_document_count(repo)
#                 repo_data.append({
#                     "Repository": repo,
#                     "Chunks": doc_count,
#                     "Status": "✅ Ready"
#                 })
            
#             st.dataframe(repo_data, use_container_width=True, hide_index=True)


# # ============================================================================
# # MAIN APPLICATION
# # ============================================================================

# def main():
#     """Main application entry point"""
#     load_custom_css()
#     initialize_session_state()
#     render_header()
#     render_sidebar()
    
#     # Initialize system
#     if not st.session_state.initialized:
#         with st.spinner("🔧 Initializing system..."):
#             vectorstore, error = initialize_system()
            
#             if error:
#                 st.error(f"❌ Initialization failed: {error}")
#                 st.info("💡 Please run the pipeline first:")
#                 st.code("python main.py", language="bash")
#                 st.stop()
            
#             st.session_state.vectorstore = vectorstore
#             st.session_state.initialized = True
#             st.success("✅ System initialized successfully!")
    
#     # Main content
#     if st.session_state.vectorstore:
#         selected_repo = render_repository_selector()
        
#         if selected_repo:
#             st.divider()
#             render_chat_interface(selected_repo)
#             st.divider()
#             render_quick_actions()
#             render_statistics()
#     else:
#         st.error("❌ System not initialized")
#         st.info("Please run: `python main.py`")


# # ============================================================================
# # ENTRY POINT
# # ============================================================================

# if __name__ == "__main__":
#     main()




"""
GitHub Repository Q&A System - Production Frontend
===================================================
Enterprise-grade Streamlit interface with modern design
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from nodes.qa_node import qa_node
from nodes.qa_utils import (
    list_available_repos, 
    get_collection_stats, 
    get_repo_document_count
)
from nodes.create_embeddings import create_embeddings_node
from config import COLLECTION_NAME


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="GitHub Q&A Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Enterprise GitHub Repository Q&A System v3.0"
    }
)


# ============================================================================
# PRODUCTION-GRADE CSS
# ============================================================================

def load_production_css():
    """Load enterprise-grade styling"""
    st.markdown("""
        <style>
        /* ========== IMPORTS ========== */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Roboto+Mono:wght@400;500&display=swap');
        
        /* ========== GLOBAL RESET ========== */
        * {
            font-family: 'Poppins', sans-serif;
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        /* ========== MAIN CONTAINER ========== */
        .main {
            background: linear-gradient(to bottom right, #0f172a, #1e293b, #334155);
            padding: 0;
            min-height: 100vh;
        }
        
        .block-container {
            padding: 2rem 3rem;
            max-width: 1400px;
        }
        
        /* ========== HEADER SECTION ========== */
        .header-container {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 20px 60px rgba(99, 102, 241, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .header-container::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 4s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }
        
        .header-title {
            color: white;
            font-size: 3rem;
            font-weight: 700;
            margin: 0;
            text-shadow: 0 4px 12px rgba(0,0,0,0.3);
            position: relative;
            z-index: 1;
        }
        
        .header-subtitle {
            color: rgba(255,255,255,0.9);
            font-size: 1.2rem;
            font-weight: 400;
            margin-top: 0.5rem;
            position: relative;
            z-index: 1;
        }
        
        /* ========== SIDEBAR ========== */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
            border-right: 1px solid rgba(99, 102, 241, 0.2);
        }
        
        [data-testid="stSidebar"] > div:first-child {
            padding: 2rem 1.5rem;
        }
        
        .sidebar-logo {
            text-align: center;
            padding: 1.5rem 0;
            border-bottom: 2px solid rgba(99, 102, 241, 0.3);
            margin-bottom: 2rem;
        }
        
        .sidebar-logo h1 {
            color: #818cf8;
            font-size: 3rem;
            margin: 0;
            text-shadow: 0 0 20px rgba(129, 140, 248, 0.5);
        }
        
        .sidebar-logo p {
            color: #94a3b8;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }
        
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #e2e8f0;
            font-weight: 600;
            margin-top: 1.5rem;
        }
        
        [data-testid="stSidebar"] .stMarkdown {
            color: #cbd5e1;
        }
        
        /* ========== CARDS ========== */
        .glass-card {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .glass-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 16px 48px rgba(99, 102, 241, 0.4);
            border-color: rgba(99, 102, 241, 0.5);
        }
        
        /* ========== METRICS ========== */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.3s ease;
        }
        
        [data-testid="stMetric"]:hover {
            border-color: rgba(99, 102, 241, 0.6);
            transform: scale(1.05);
        }
        
        [data-testid="stMetricLabel"] {
            color: #94a3b8;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        [data-testid="stMetricValue"] {
            color: #e2e8f0;
            font-size: 2rem;
            font-weight: 700;
            text-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
        }
        
        /* ========== BUTTONS ========== */
        .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.875rem 1.5rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
            cursor: pointer;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.5);
            background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
        }
        
        .stButton > button:active {
            transform: translateY(-1px);
        }
        
        .stButton > button:disabled {
            background: #475569;
            cursor: not-allowed;
            opacity: 0.5;
        }
        
        /* ========== INPUTS ========== */
        .stTextInput input {
            background: rgba(30, 41, 59, 0.6);
            border: 2px solid rgba(99, 102, 241, 0.3);
            border-radius: 12px;
            color: #e2e8f0;
            padding: 1rem 1.5rem;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput input:focus {
            border-color: #6366f1;
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2);
            background: rgba(30, 41, 59, 0.8);
        }
        
        .stTextInput input::placeholder {
            color: #64748b;
        }
        
        .stSelectbox select {
            background: rgba(30, 41, 59, 0.6);
            border: 2px solid rgba(99, 102, 241, 0.3);
            border-radius: 12px;
            color: #e2e8f0;
            padding: 0.875rem 1.5rem;
            font-size: 1rem;
        }
        
        /* ========== CHAT MESSAGES ========== */
        .chat-container {
            max-height: 600px;
            overflow-y: auto;
            padding: 1rem;
            scrollbar-width: thin;
            scrollbar-color: #6366f1 #1e293b;
        }
        
        .chat-container::-webkit-scrollbar {
            width: 8px;
        }
        
        .chat-container::-webkit-scrollbar-track {
            background: #1e293b;
            border-radius: 4px;
        }
        
        .chat-container::-webkit-scrollbar-thumb {
            background: #6366f1;
            border-radius: 4px;
        }
        
        .user-message {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 16px 16px 4px 16px;
            margin: 1rem 0 1rem auto;
            max-width: 80%;
            box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
            animation: slideInRight 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }
        
        .user-message::before {
            content: '👤';
            position: absolute;
            top: -8px;
            right: -8px;
            background: #1e293b;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        
        .bot-message {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #e2e8f0;
            padding: 1.5rem;
            border-radius: 16px 16px 16px 4px;
            margin: 1rem auto 1rem 0;
            max-width: 80%;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            animation: slideInLeft 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }
        
        .bot-message::before {
            content: '🤖';
            position: absolute;
            top: -8px;
            left: -8px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            box-shadow: 0 2px 8px rgba(99, 102, 241, 0.5);
        }
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(100px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-100px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .message-label {
            font-weight: 600;
            margin-bottom: 0.5rem;
            opacity: 0.9;
        }
        
        .message-text {
            line-height: 1.6;
            font-size: 0.95rem;
        }
        
        /* ========== ALERTS ========== */
        .stAlert {
            background: rgba(30, 41, 59, 0.8);
            border-left: 4px solid #6366f1;
            border-radius: 12px;
            color: #e2e8f0;
        }
        
        .stSuccess {
            border-left-color: #10b981;
        }
        
        .stError {
            border-left-color: #ef4444;
        }
        
        .stWarning {
            border-left-color: #f59e0b;
        }
        
        .stInfo {
            border-left-color: #3b82f6;
        }
        
        /* ========== EXPANDER ========== */
        .streamlit-expanderHeader {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 12px;
            color: #e2e8f0;
            font-weight: 600;
            padding: 1rem;
            transition: all 0.3s ease;
        }
        
        .streamlit-expanderHeader:hover {
            background: rgba(30, 41, 59, 0.8);
            border-color: rgba(99, 102, 241, 0.4);
        }
        
        .streamlit-expanderContent {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-top: none;
            border-radius: 0 0 12px 12px;
            padding: 1rem;
        }
        
        /* ========== DIVIDER ========== */
        hr {
            margin: 2.5rem 0;
            border: none;
            height: 2px;
            background: linear-gradient(90deg, 
                transparent 0%, 
                rgba(99, 102, 241, 0.5) 20%, 
                rgba(139, 92, 246, 0.5) 50%,
                rgba(99, 102, 241, 0.5) 80%, 
                transparent 100%);
        }
        
        /* ========== SPINNER ========== */
        .stSpinner > div {
            border-top-color: #6366f1 !important;
            border-right-color: #8b5cf6 !important;
        }
        
        /* ========== CODE BLOCKS ========== */
        code {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #818cf8;
            padding: 0.25rem 0.5rem;
            border-radius: 6px;
            font-family: 'Roboto Mono', monospace;
            font-size: 0.9rem;
        }
        
        /* ========== DATAFRAME ========== */
        [data-testid="stDataFrame"] {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 12px;
        }
        
        /* ========== DOWNLOAD BUTTON ========== */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }
        
        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        }
        
        /* ========== FORM ========== */
        [data-testid="stForm"] {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 16px;
            padding: 2rem;
        }
        
        /* ========== HEADINGS ========== */
        h1, h2, h3, h4, h5, h6 {
            color: #e2e8f0;
            font-weight: 600;
        }
        
        h1 { font-size: 2.5rem; margin-bottom: 1rem; }
        h2 { font-size: 2rem; margin: 2rem 0 1rem 0; }
        h3 { font-size: 1.5rem; margin: 1.5rem 0 0.75rem 0; }
        
        /* ========== PARAGRAPH ========== */
        p {
            color: #cbd5e1;
            line-height: 1.7;
        }
        
        /* ========== BADGE ========== */
        .status-badge {
            display: inline-block;
            padding: 0.375rem 0.875rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
            margin: 0.25rem;
        }
        
        .badge-success {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        
        .badge-warning {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        
        .badge-error {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        
        /* ========== ANIMATIONS ========== */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes scaleIn {
            from { transform: scale(0.9); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        .scale-in {
            animation: scaleIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* ========== RESPONSIVE ========== */
        @media (max-width: 768px) {
            .block-container {
                padding: 1rem;
            }
            
            .header-title {
                font-size: 2rem;
            }
            
            .user-message, .bot-message {
                max-width: 95%;
            }
        }
        </style>
    """, unsafe_allow_html=True)


# ============================================================================
# SESSION STATE
# ============================================================================

def init_session():
    """Initialize session state"""
    defaults = {
        'initialized': False,
        'vectorstore': None,
        'chat_history': [],
        'current_repo': None,
        'show_stats': False,
        'pending_question': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================================
# CACHE FUNCTIONS
# ============================================================================

@st.cache_resource(show_spinner=False)
def init_vectorstore():
    """Initialize vectorstore"""
    try:
        state = create_embeddings_node({})
        return state.get("vectorstore"), None
    except Exception as e:
        return None, str(e)


@st.cache_data(ttl=60, show_spinner=False)
def get_repos():
    """Get available repositories"""
    try:
        return list_available_repos(), None
    except Exception as e:
        return [], str(e)


@st.cache_data(ttl=60, show_spinner=False)
def get_stats():
    """Get collection statistics"""
    try:
        return get_collection_stats(), None
    except Exception as e:
        return None, str(e)


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_header():
    """Render modern header"""
    st.markdown("""
        <div class="header-container scale-in">
            <h1 class="header-title">🚀 GitHub Repository Q&A Assistant</h1>
            <p class="header-subtitle">Enterprise AI-powered documentation search and analysis platform</p>
        </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar"""
    with st.sidebar:
        # Logo
        st.markdown("""
            <div class="sidebar-logo">
                <h1>⚡</h1>
                <p>AI Assistant v3.0</p>
            </div>
        """, unsafe_allow_html=True)
        
        # System Status
        st.markdown("### 📊 System Status")
        
        stats, error = get_stats()
        repos, _ = get_repos()
        
        if stats and stats.get("exists"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🗂️ Repos", len(repos) if repos else 0)
            with col2:
                st.metric("📦 Vectors", f"{stats.get('vectors_count', 0):,}")
            
            st.markdown(f"""
                <div style="text-align: center; margin: 1rem 0;">
                    <span class="status-badge badge-success">✓ Online</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="text-align: center; margin: 1rem 0;">
                    <span class="status-badge badge-error">✗ Offline</span>
                </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Repository List
        st.markdown("### 📚 Repositories")
        
        if repos:
            for repo in repos[:10]:  # Show first 10
                doc_count = get_repo_document_count(repo)
                with st.expander(f"📁 {repo[:25]}...", expanded=False):
                    st.write(f"**Chunks:** {doc_count:,}")
                    if st.button("Select", key=f"sb_{repo}", use_container_width=True):
                        st.session_state.current_repo = repo
                        st.rerun()
        else:
            st.info("No repositories found")
        
        st.divider()
        
        # Session Info
        if st.session_state.chat_history:
            st.markdown("### 💬 Session")
            st.metric("Questions", len(st.session_state.chat_history))
        
        # Refresh
        if st.button("🔄 Refresh System", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()


def render_repo_selector():
    """Render repository selector"""
    repos, error = get_repos()
    
    if error:
        st.error(f"❌ Error: {error}")
        return None
    
    if not repos:
        st.warning("⚠️ No repositories available")
        st.code("python main.py", language="bash")
        return None
    
    st.markdown("### 📂 Select Repository")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        selected = st.selectbox(
            "Choose repository",
            options=repos,
            index=repos.index(st.session_state.current_repo) if st.session_state.current_repo in repos else 0,
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("📊", use_container_width=True, help="Toggle Statistics"):
            st.session_state.show_stats = not st.session_state.get('show_stats', False)
            st.rerun()
    
    if selected != st.session_state.current_repo:
        st.session_state.current_repo = selected
        st.session_state.chat_history = []
    
    # Metrics
    if selected:
        cols = st.columns(3)
        with cols[0]:
            st.metric("📁 Repository", selected[:20] + "...")
        with cols[1]:
            doc_count = get_repo_document_count(selected)
            st.metric("📄 Chunks", f"{doc_count:,}")
        with cols[2]:
            st.metric("🔍 Status", "Ready")
    
    return selected


def render_chat_interface(repo_name):
    """Render chat interface"""
    st.markdown("### 💬 Conversation")
    
    # Chat history
    if st.session_state.chat_history:
        chat_html = '<div class="chat-container">'
        
        for chat in st.session_state.chat_history:
            # User message
            chat_html += f"""
                <div class="user-message">
                    <div class="message-label">You</div>
                    <div class="message-text">{chat['question']}</div>
                </div>
            """
            
            # Bot message
            chat_html += f"""
                <div class="bot-message">
                    <div class="message-label">Assistant</div>
                    <div class="message-text">{chat['answer']}</div>
                </div>
            """
        
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
        
        # Sources in expander
        if st.session_state.chat_history[-1].get('sources'):
            with st.expander("📚 View Sources", expanded=False):
                for i, src in enumerate(st.session_state.chat_history[-1]['sources'][:5], 1):
                    st.markdown(f"**{i}.** `{src}`")
    else:
        st.info("👋 Start by asking a question about the repository!")
    
    st.divider()
    
    # Input form
    with st.form("question_form", clear_on_submit=True):
        question = st.text_input(
            "Ask your question",
            placeholder=f"What would you like to know about {repo_name}?",
            key="q_input"
        )
        
        cols = st.columns([3, 1, 1])
        with cols[0]:
            submit = st.form_submit_button("🚀 Ask", use_container_width=True)
        with cols[1]:
            clear = st.form_submit_button("🗑️ Clear", use_container_width=True)
        with cols[2]:
            export = st.form_submit_button("💾 Export", use_container_width=True)
    
    # Example questions outside form
    with st.expander("💡 Example Questions", expanded=False):
        examples = [
            "What is the main purpose of this repository?",
            "How do I install and set up this project?",
            "What are the key features?",
            "What technologies are used?",
            "How is the code structured?",
            "What are the API endpoints?",
            "What dependencies does it use?"
        ]
        
        cols = st.columns(2)
        for i, ex in enumerate(examples):
            with cols[i % 2]:
                if st.button(f"💬 {ex[:40]}...", key=f"ex_{i}", use_container_width=True):
                    st.session_state.pending_question = ex
                    st.rerun()
    
    # Handle pending question
    if st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None
        submit = True
    
    # Handle actions
    if clear:
        st.session_state.chat_history = []
        st.success("✅ Chat cleared!")
        st.rerun()
    
    if export and st.session_state.chat_history:
        chat_text = "\n\n".join([
            f"Q: {c['question']}\nA: {c['answer']}\n{'-'*80}"
            for c in st.session_state.chat_history
        ])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            "💾 Download Chat",
            data=chat_text,
            file_name=f"chat_{repo_name}_{timestamp}.txt",
            mime="text/plain"
        )
    
    # Process question
    if submit and question:
        with st.spinner("🔍 Analyzing..."):
            answer, sources = process_question(repo_name, question)
            
            if answer:
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": answer,
                    "sources": sources,
                    "timestamp": datetime.now().isoformat()
                })
                st.rerun()
            else:
                st.error("❌ Failed to generate answer")


def process_question(repo_name, question):
    """Process question and get answer"""
    try:
        state = {
            "selected_repo": repo_name,
            "query": question,
            "vectorstore": st.session_state.vectorstore
        }
        
        result = qa_node(state)
        qa_response = result.get("qa", [])
        
        if not qa_response:
            return None, []
        
        # Parse response
        answer_lines = []
        sources = []
        in_sources = False
        
        for line in qa_response:
            if "Sources" in line or "📚" in line:
                in_sources = True
                continue
            
            if in_sources:
                if line.strip() and any(line.strip().startswith(f"{i}.") for i in range(1, 10)):
                    src = line.strip().split(".", 1)[1].strip() if "." in line else line.strip()
                    sources.append(src)
            else:
                if line.strip() and not line.startswith("📂"):
                    answer_lines.append(line)
        
        answer = "\n".join(answer_lines).strip()
        return answer, sources
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None, []


def render_stats():
    """Render statistics dashboard"""
    if not st.session_state.get('show_stats'):
        return
    
    st.markdown("### 📊 Analytics Dashboard")
    
    stats, _ = get_stats()
    repos, _ = get_repos()
    
    # Overview metrics
    cols = st.columns(4)
    with cols[0]:
        st.metric("📚 Total Repos", len(repos) if repos else 0)
    with cols[1]:
        st.metric("🔢 Total Vectors", f"{stats.get('vectors_count', 0):,}" if stats else "0")
    with cols[2]:
        st.metric("💬 Questions", len(st.session_state.chat_history))
    with cols[3]:
        status = "🟢 Active" if st.session_state.vectorstore else "🔴 Inactive"
        st.metric("⚡ Session", status)
    
    # Repository breakdown
    if repos:
        st.markdown("#### 📁 Repository Details")
        
        repo_data = []
        for repo in repos:
            doc_count = get_repo_document_count(repo)
            repo_data.append({
                "Repository": repo,
                "Chunks": doc_count,
                "Status": "✅"
            })
        
        st.dataframe(repo_data, use_container_width=True, hide_index=True)


def render_quick_actions():
    """Render quick action buttons"""
    st.markdown("### ⚡ Quick Actions")
    
    cols = st.columns(4)
    
    with cols[0]:
        if st.button("🗑️ Clear Chat", use_container_width=True, key="qa_clear"):
            st.session_state.chat_history = []
            st.success("✅ Cleared!")
            st.rerun()
    
    with cols[1]:
        if st.button("📊 Toggle Stats", use_container_width=True, key="qa_stats"):
            st.session_state.show_stats = not st.session_state.get('show_stats', False)
            st.rerun()
    
    with cols[2]:
        if st.session_state.chat_history:
            chat_json = json.dumps(st.session_state.chat_history, indent=2)
            st.download_button(
                "📥 Export JSON",
                data=chat_json,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        else:
            st.button("📥 Export JSON", disabled=True, use_container_width=True)
    
    with cols[3]:
        if st.button("🔄 Refresh Data", use_container_width=True, key="qa_refresh"):
            st.cache_data.clear()
            st.rerun()


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application"""
    # Load styling
    load_production_css()
    
    # Initialize
    init_session()
    
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar()
    
    # Initialize vectorstore
    if not st.session_state.initialized:
        with st.spinner("🔧 Initializing AI system..."):
            vectorstore, error = init_vectorstore()
            
            if error:
                st.error(f"❌ Initialization failed: {error}")
                st.info("💡 Please run the pipeline first:")
                st.code("python main.py", language="bash")
                st.stop()
            
            st.session_state.vectorstore = vectorstore
            st.session_state.initialized = True
            st.success("✅ System ready!")
    
    # Main content
    if st.session_state.vectorstore:
        # Repository selector
        selected_repo = render_repo_selector()
        
        if selected_repo:
            st.divider()
            
            # Chat interface
            render_chat_interface(selected_repo)
            
            st.divider()
            
            # Quick actions
            render_quick_actions()
            
            # Statistics
            render_stats()
            
    else:
        st.error("❌ System not initialized")
        st.info("Please run: `python main.py`")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()