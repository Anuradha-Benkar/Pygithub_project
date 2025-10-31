import sys
import os

# from github_repo_processor import GROQ_API_KEY
from config import GROQ_API_KEY
sys.path.append('.')
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

import subprocess
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, TypedDict
from datetime import datetime

# LangGraph and LangChain imports
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate

# dotenv import for environment variables
from dotenv import load_dotenv

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ Missing GITHUB_TOKEN or GROQ_API_KEY in .env file")

# ------------------------------
# STATE
# ------------------------------
class DocumentationState(TypedDict):
    repo_path: str
    repo_name: str
    file_contents: Dict[str, str]
    initial_documentation: str
    reviewed_documentation: str
    final_documentation: str
    current_step: str
    error_message: str


# ------------------------------
# DOC GENERATOR CLASS 
# ------------------------------
# class DocumentationGenerator:
#     def __init__(self, GROQ_API_K: str):
#         self.analyzer_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.7)
#         self.documenter_llm = ChatGroq(model="llama-3.1-70b-versatile", temperature=0.7)
#         self.reviewer_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)

#     def read_repository_files(self, repo_path: str) -> Dict[str, str]:
#         """Read all relevant files"""
#         file_contents = {}
#         supported_extensions = {
#             '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h',
#             '.md', '.txt', '.yml', '.yaml', '.json', '.xml', 
#             '.html', '.css', '.jsx', '.tsx'
#         }
#         repo_path = Path(repo_path)
#         all_files = [f for f in repo_path.rglob("*") if f.is_file() and f.suffix in supported_extensions]

#         total_chars = 0
#         for file_path in all_files:
#             try:
#                 if file_path.stat().st_size > 512*1024: 
#                     continue
#                 with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
#                     content = f.read()
#                 if len(content) > 20000:
#                     continue
#                 if total_chars + len(content) > 200000:
#                     break
#                 file_contents[str(file_path.relative_to(repo_path))] = content
#                 total_chars += len(content)
#             except Exception as e:
#                 print(f"⚠️ Could not read {file_path}: {e}")
#         return file_contents

class DocumentationGenerator:
    def __init__(self, GROQ_API_K: str):
        self.analyzer_llm = ChatGroq(
            model="llama-3.3-70b-versatile", 
            api_key=GROQ_API_K,
            temperature=0.7
        )
        self.documenter_llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=GROQ_API_K,
            temperature=0.7
        )
        self.reviewer_llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=GROQ_API_K,
            temperature=0.7
        )


        # ✅ NEW FUNCTION - ADD THIS ONE
    def read_repository_files(self, repo_path: str) -> Dict[str, str]:
        """Read all relevant files"""
        file_contents = {}
        supported_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h',
            '.md', '.txt', '.yml', '.yaml', '.json', '.xml', 
            '.html', '.css', '.jsx', '.tsx', '.go', '.rs', '.rb'
        }
        repo_path = Path(repo_path)
        
        # Skip common directories
        skip_dirs = {'.git', '__pycache__', 'node_modules', 'venv', 'env', '.venv', 'dist', 'build'}
        
        all_files = []
        for f in repo_path.rglob("*"):
            if f.is_file() and f.suffix in supported_extensions:
                # Check if file is in skip directory
                if any(skip_dir in f.parts for skip_dir in skip_dirs):
                    continue
                all_files.append(f)

        total_chars = 0
        for file_path in all_files:
            try:
                # Skip large files
                if file_path.stat().st_size > 512*1024: 
                    continue
                    
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                # Skip very long files
                if len(content) > 20000:
                    continue
                    
                # Stop if we've read too much
                if total_chars + len(content) > 200000:
                    break
                    
                file_contents[str(file_path.relative_to(repo_path))] = content
                total_chars += len(content)
                
            except Exception as e:
                print(f"⚠️ Could not read {file_path}: {e}")
                
        return file_contents



    def analyze_repository_structure(self, state: DocumentationState):#-> DocumentationState
        """Analyze repo structure"""
        prompt = f"Analyze repo {state['repo_name']} with files: {list(state['file_contents'].keys())[:10]}"
        try:
            response = self.analyzer_llm.invoke([HumanMessage(content=prompt)])
            state["initial_documentation"] = response.content
            state["current_step"] = "analysis_complete"
        except Exception as e:
            state["initial_documentation"] = f"Basic analysis for {state['repo_name']}"
            state["current_step"] = "analysis_complete"
        return state

    def generate_documentation(self, state: DocumentationState) -> DocumentationState:
        """Generate docs"""
        doc_prompt = f"Generate documentation for {state['repo_name']}:\n{state['initial_documentation']}"
        try:
            response = self.documenter_llm.invoke([HumanMessage(content=doc_prompt)])
            state["reviewed_documentation"] = response.content
            state["current_step"] = "documentation_complete"
        except Exception as e:
            state["error_message"] = str(e)
            state["current_step"] = "error"
        return state

    def review_documentation(self, state: DocumentationState) -> DocumentationState:
        """Refine docs"""
        review_prompt = f"Improve documentation:\n{state['reviewed_documentation'][:8000]}"
        try:
            response = self.reviewer_llm.invoke([HumanMessage(content=review_prompt)])
            state["final_documentation"] = response.content
            state["current_step"] = "review_complete"
        except Exception:
            state["final_documentation"] = state["reviewed_documentation"]
            state["current_step"] = "review_complete"
        return state

    def save_documentation(self, state: DocumentationState) -> DocumentationState:
        """Save docs"""
        docs_dir = Path("repos_docs2")
        docs_dir.mkdir(exist_ok=True)
        file_path = docs_dir / f"{state['repo_name']}_documentation.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# Generated on {datetime.now()}\n\n")
            f.write(state["final_documentation"])
        state["current_step"] = "complete"
        return state


# ------------------------------
# HELPER: HASH
# ------------------------------
def calculate_repo_hash(file_contents: Dict[str, str]) -> str:
    """Create hash for repo contents"""
    md5 = hashlib.md5()
    for path, content in sorted(file_contents.items()):
        md5.update(path.encode("utf-8"))
        md5.update(content.encode("utf-8"))
    return md5.hexdigest()


# ------------------------------
# WORKFLOW
# ------------------------------
def create_documentation_workflow():
    gen = DocumentationGenerator(GROQ_API_KEY)
    workflow = StateGraph(DocumentationState)
    workflow.add_node("analyze", gen.analyze_repository_structure)
    workflow.add_node("document", gen.generate_documentation)
    workflow.add_node("review", gen.review_documentation)
    workflow.add_node("save", gen.save_documentation)

    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "document")
    workflow.add_edge("document", "review")
    workflow.add_edge("review", "save")
    workflow.add_edge("save", END)
    return workflow.compile()


# ------------------------------
# PROCESS REPO
# ------------------------------
def process_repository(repo_path: str, repo_name: str = None, metadata_file="repo_doc_metadata.json"):
    """Process a single repo"""
    print(f"🔹 Processing repository at -> {repo_path}")

    if repo_name is None:
        repo_name = Path(repo_path).name

    # Load metadata
    metadata = {}
    if os.path.exists(metadata_file):
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    gen = DocumentationGenerator(GROQ_API_KEY)
    file_contents = gen.read_repository_files(repo_path)
    if not file_contents:
        return f"Failed: no files in {repo_name}"

    current_hash = calculate_repo_hash(file_contents)

    # Skip if unchanged
    if repo_name in metadata and metadata[repo_name]["hash"] == current_hash:
        print(f"⏩ Skipping {repo_name}: no changes detected")
        return f"Skipped: no changes in {repo_name}"

    # Run workflow
    workflow = create_documentation_workflow()
    state = DocumentationState(
        repo_path=repo_path,
        repo_name=repo_name,
        file_contents=file_contents,
        initial_documentation="",
        reviewed_documentation="",
        final_documentation="",
        current_step="initialized",
        error_message=""
    )
    final_state = workflow.invoke(state)
    if final_state["current_step"] == "complete":
        metadata[repo_name] = {
            "hash": current_hash,
            "last_updated": datetime.now().isoformat()
        }
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        return f"Success: docs generated for {repo_name}"
    return f"Failed: {final_state.get('error_message','unknown error')}"


# ------------------------------
# PROCESS ALL REPOS
# ------------------------------
def process_all_repositories(base_path="data/github_repos"):
    print("🚀 Starting documentation generation pipeline...")
    base = Path(base_path)
    if not base.exists():
        print(f"⚠️ {base} does not exist. Creating it now...")
        base.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created folder '{base}'")
        print("⚠️ Currently, no repositories to process. Add repos inside this folder and rerun the script.")
        return
    repos = [d for d in base.iterdir() if d.is_dir()]
    for repo in repos:
        print(f"\n--- Processing {repo.name} ---")
        result = process_repository(str(repo), repo.name)
        print(result)  




# # utils/doc_utils.py
# import sys
# import os
# sys.path.append('.')

# import hashlib
# import json
# import time
# from pathlib import Path
# from typing import Dict, TypedDict
# from datetime import datetime

# # LangGraph and LangChain imports
# from langgraph.graph import StateGraph, END
# from langchain_groq import ChatGroq
# from langchain.schema import HumanMessage

# # Import from config instead of non-existent module
# from config import GROQ_API_KEY

# if not GROQ_API_KEY:
#     raise ValueError("❌ Missing GROQ_API_KEY in .env file")

# # ------------------------------
# # STATE
# # ------------------------------
# class DocumentationState(TypedDict):
#     repo_path: str
#     repo_name: str
#     file_contents: Dict[str, str]
#     initial_documentation: str
#     reviewed_documentation: str
#     final_documentation: str
#     current_step: str
#     error_message: str


# # ------------------------------
# # DOC GENERATOR CLASS 
# # ------------------------------
# class DocumentationGenerator:
#     def __init__(self, groq_api_key: str):
#         self.analyzer_llm = ChatGroq(
#             model="llama-3.1-70b-versatile", 
#             api_key=groq_api_key,
#             temperature=0.7
#         )
#         self.documenter_llm = ChatGroq(
#             model="llama-3.1-70b-versatile",
#             api_key=groq_api_key,
#             temperature=0.7
#         )
#         self.reviewer_llm = ChatGroq(
#             model="llama-3.1-8b-instant",
#             api_key=groq_api_key,
#             temperature=0.7
#         )

#     def read_repository_files(self, repo_path: str) -> Dict[str, str]:
#         """Read all relevant files"""
#         file_contents = {}
#         supported_extensions = {
#             '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h',
#             '.md', '.txt', '.yml', '.yaml', '.json', '.xml', 
#             '.html', '.css', '.jsx', '.tsx', '.go', '.rs', '.rb'
#         }
#         repo_path = Path(repo_path)
        
#         # Skip common directories
#         skip_dirs = {'.git', '__pycache__', 'node_modules', 'venv', 'env', '.venv', 'dist', 'build'}
        
#         all_files = []
#         for f in repo_path.rglob("*"):
#             if f.is_file() and f.suffix in supported_extensions:
#                 # Check if file is in skip directory
#                 if any(skip_dir in f.parts for skip_dir in skip_dirs):
#                     continue
#                 all_files.append(f)

#         total_chars = 0
#         for file_path in all_files:
#             try:
#                 # Skip large files
#                 if file_path.stat().st_size > 512*1024: 
#                     continue
                    
#                 with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
#                     content = f.read()
                    
#                 # Skip very long files
#                 if len(content) > 20000:
#                     continue
                    
#                 # Stop if we've read too much
#                 if total_chars + len(content) > 200000:
#                     break
                    
#                 file_contents[str(file_path.relative_to(repo_path))] = content
#                 total_chars += len(content)
                
#             except Exception as e:
#                 print(f"⚠️ Could not read {file_path}: {e}")
                
#         return file_contents

#     def analyze_repository_structure(self, state: DocumentationState) -> DocumentationState:
#         """Analyze repo structure"""
#         file_list = list(state['file_contents'].keys())[:20]  # First 20 files
        
#         prompt = f"""Analyze the following repository: {state['repo_name']}

# Files found:
# {chr(10).join(file_list)}

# Provide a brief analysis of:
# 1. What type of project this is
# 2. Main programming languages used
# 3. Key components or modules
# 4. Overall purpose

# Keep it concise (under 500 words)."""

#         try:
#             response = self.analyzer_llm.invoke([HumanMessage(content=prompt)])
#             state["initial_documentation"] = response.content
#             state["current_step"] = "analysis_complete"
#             print(f"✅ Analysis complete for {state['repo_name']}")
#         except Exception as e:
#             print(f"⚠️ Analysis failed: {e}")
#             state["initial_documentation"] = f"Basic analysis for {state['repo_name']}"
#             state["current_step"] = "analysis_complete"
#         return state

#     def generate_documentation(self, state: DocumentationState) -> DocumentationState:
#         """Generate comprehensive documentation"""
        
#         # Get some sample code
#         sample_files = list(state['file_contents'].items())[:3]
#         sample_code = "\n\n---\n\n".join([
#             f"File: {name}\n```\n{content[:1000]}...\n```" 
#             for name, content in sample_files
#         ])
        
#         doc_prompt = f"""Generate comprehensive documentation for the repository: {state['repo_name']}

# Initial Analysis:
# {state['initial_documentation']}

# Sample Code:
# {sample_code}

# Create documentation with these sections:
# # {state['repo_name']} Documentation

# ## Overview
# (What the project does)

# ## Features
# (Key features and capabilities)

# ## Installation
# (How to install/setup)

# ## Usage
# (Basic usage examples)

# ## Project Structure
# (Main files and directories)

# ## Technical Details
# (Technologies, dependencies, architecture)

# Keep it clear and user-friendly."""

#         try:
#             response = self.documenter_llm.invoke([HumanMessage(content=doc_prompt)])
#             state["reviewed_documentation"] = response.content
#             state["current_step"] = "documentation_complete"
#             print(f"✅ Documentation generated for {state['repo_name']}")
#         except Exception as e:
#             print(f"❌ Documentation generation failed: {e}")
#             state["error_message"] = str(e)
#             state["current_step"] = "error"
#         return state

#     def review_documentation(self, state: DocumentationState) -> DocumentationState:
#         """Review and refine documentation"""
#         review_prompt = f"""Review and improve the following documentation. 
# Fix any errors, improve clarity, and ensure completeness.

# Documentation:
# {state['reviewed_documentation'][:8000]}

# Provide the improved version."""

#         try:
#             response = self.reviewer_llm.invoke([HumanMessage(content=review_prompt)])
#             state["final_documentation"] = response.content
#             state["current_step"] = "review_complete"
#             print(f"✅ Documentation reviewed for {state['repo_name']}")
#         except Exception as e:
#             print(f"⚠️ Review failed, using original: {e}")
#             state["final_documentation"] = state["reviewed_documentation"]
#             state["current_step"] = "review_complete"
#         return state

#     def save_documentation(self, state: DocumentationState) -> DocumentationState:
#         """Save documentation to file"""
#         docs_dir = Path("repos_docs2")
#         docs_dir.mkdir(exist_ok=True)
#         file_path = docs_dir / f"{state['repo_name']}_documentation.md"
        
#         try:
#             with open(file_path, "w", encoding="utf-8") as f:
#                 f.write(f"# Documentation for {state['repo_name']}\n")
#                 f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
#                 f.write("---\n\n")
#                 f.write(state["final_documentation"])
            
#             state["current_step"] = "complete"
#             print(f"✅ Documentation saved to {file_path}")
#         except Exception as e:
#             print(f"❌ Failed to save documentation: {e}")
#             state["error_message"] = str(e)
            
#         return state


# # ------------------------------
# # HELPER: HASH
# # ------------------------------
# def calculate_repo_hash(file_contents: Dict[str, str]) -> str:
#     """Create hash for repo contents"""
#     md5 = hashlib.md5()
#     for path, content in sorted(file_contents.items()):
#         md5.update(path.encode("utf-8"))
#         md5.update(content.encode("utf-8"))
#     return md5.hexdigest()


# # ------------------------------
# # WORKFLOW
# # ------------------------------
# def create_documentation_workflow():
#     gen = DocumentationGenerator(GROQ_API_KEY)
#     workflow = StateGraph(DocumentationState)
    
#     workflow.add_node("analyze", gen.analyze_repository_structure)
#     workflow.add_node("document", gen.generate_documentation)
#     workflow.add_node("review", gen.review_documentation)
#     workflow.add_node("save", gen.save_documentation)

#     workflow.set_entry_point("analyze")
#     workflow.add_edge("analyze", "document")
#     workflow.add_edge("document", "review")
#     workflow.add_edge("review", "save")
#     workflow.add_edge("save", END)
    
#     return workflow.compile()


# # ------------------------------
# # PROCESS REPO
# # ------------------------------
# def process_repository(repo_path: str, repo_name: str = None, metadata_file="repo_doc_metadata.json"):
#     """Process a single repository"""
#     print(f"\n{'='*60}")
#     print(f"🔹 Processing repository: {repo_path}")
#     print(f"{'='*60}")

#     if repo_name is None:
#         repo_name = Path(repo_path).name

#     # Load metadata
#     metadata = {}
#     if os.path.exists(metadata_file):
#         try:
#             with open(metadata_file, "r", encoding="utf-8") as f:
#                 metadata = json.load(f)
#         except:
#             metadata = {}

#     gen = DocumentationGenerator(GROQ_API_KEY)
    
#     print(f"📂 Reading files from {repo_path}...")
#     file_contents = gen.read_repository_files(repo_path)
    
#     if not file_contents:
#         print(f"⚠️ No supported files found in {repo_name}")
#         return f"Failed: no files in {repo_name}"

#     print(f"✅ Read {len(file_contents)} files")
    
#     current_hash = calculate_repo_hash(file_contents)

#     # Skip if unchanged
#     if repo_name in metadata and metadata[repo_name].get("hash") == current_hash:
#         print(f"⏩ Skipping {repo_name}: no changes detected")
#         return f"Skipped: no changes in {repo_name}"

#     # Run workflow
#     print(f"🚀 Starting documentation workflow for {repo_name}...")
#     workflow = create_documentation_workflow()
    
#     state = DocumentationState(
#         repo_path=repo_path,
#         repo_name=repo_name,
#         file_contents=file_contents,
#         initial_documentation="",
#         reviewed_documentation="",
#         final_documentation="",
#         current_step="initialized",
#         error_message=""
#     )
    
#     final_state = workflow.invoke(state)
    
#     if final_state["current_step"] == "complete":
#         # Update metadata
#         metadata[repo_name] = {
#             "hash": current_hash,
#             "last_updated": datetime.now().isoformat()
#         }
#         with open(metadata_file, "w", encoding="utf-8") as f:
#             json.dump(metadata, f, indent=2)
        
#         print(f"✅ Successfully generated docs for {repo_name}")
#         return f"Success: docs generated for {repo_name}"
#     else:
#         error_msg = final_state.get('error_message', 'unknown error')
#         print(f"❌ Failed to generate docs for {repo_name}: {error_msg}")
#         return f"Failed: {error_msg}"


# # ------------------------------
# # PROCESS ALL REPOS
# # ------------------------------
# def process_all_repositories(base_path="data/github_repos"):
#     """Process all repositories in the base path"""
#     print("\n" + "="*60)
#     print("🚀 Starting documentation generation pipeline...")
#     print("="*60 + "\n")
    
#     base = Path(base_path)
    
#     if not base.exists():
#         print(f"⚠️ Directory {base} does not exist. Creating it now...")
#         base.mkdir(parents=True, exist_ok=True)
#         print(f"✅ Created folder '{base}'")
#         print("⚠️ No repositories to process yet.")
#         print(f"   Please ensure repositories are cloned to {base_path}")
#         return
    
#     repos = [d for d in base.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
#     if not repos:
#         print(f"⚠️ No repositories found in {base_path}")
#         print("   Make sure the download_repos step completed successfully.")
#         return
    
#     print(f"📦 Found {len(repos)} repositories to process:\n")
#     for i, repo in enumerate(repos, 1):
#         print(f"   {i}. {repo.name}")
#     print()
    
#     results = []
#     for repo in repos:
#         result = process_repository(str(repo), repo.name)
#         results.append(result)
#         time.sleep(1)  # Small delay between repos
    
#     # Summary
#     print("\n" + "="*60)
#     print("📊 Documentation Generation Summary")
#     print("="*60)
#     for result in results:
#         status = "✅" if "Success" in result else ("⏩" if "Skipped" in result else "❌")
#         print(f"{status} {result}")
#     print("="*60 + "\n")