# import sys
# import os

# # from github_repo_processor import GROQ_API_KEY
# from config import GROQ_API_KEY
# sys.path.append('.')
# from IPython.core.interactiveshell import InteractiveShell
# InteractiveShell.ast_node_interactivity = "all"

# import subprocess
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
# from langchain.prompts import PromptTemplate

# # dotenv import for environment variables
# from dotenv import load_dotenv

# # GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# if not GROQ_API_KEY:
#     raise ValueError("❌ Missing GITHUB_TOKEN or GROQ_API_KEY in .env file")

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
# # class DocumentationGenerator:
# #     def __init__(self, GROQ_API_K: str):
# #         self.analyzer_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.7)
# #         self.documenter_llm = ChatGroq(model="llama-3.1-70b-versatile", temperature=0.7)
# #         self.reviewer_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)

# #     def read_repository_files(self, repo_path: str) -> Dict[str, str]:
# #         """Read all relevant files"""
# #         file_contents = {}
# #         supported_extensions = {
# #             '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h',
# #             '.md', '.txt', '.yml', '.yaml', '.json', '.xml', 
# #             '.html', '.css', '.jsx', '.tsx'
# #         }
# #         repo_path = Path(repo_path)
# #         all_files = [f for f in repo_path.rglob("*") if f.is_file() and f.suffix in supported_extensions]

# #         total_chars = 0
# #         for file_path in all_files:
# #             try:
# #                 if file_path.stat().st_size > 512*1024: 
# #                     continue
# #                 with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
# #                     content = f.read()
# #                 if len(content) > 20000:
# #                     continue
# #                 if total_chars + len(content) > 200000:
# #                     break
# #                 file_contents[str(file_path.relative_to(repo_path))] = content
# #                 total_chars += len(content)
# #             except Exception as e:
# #                 print(f"⚠️ Could not read {file_path}: {e}")
# #         return file_contents

# class DocumentationGenerator:
#     def __init__(self, GROQ_API_K: str):
#         self.analyzer_llm = ChatGroq(
#             model="llama-3.3-70b-versatile", 
#             api_key=GROQ_API_K,
#             temperature=0.7
#         )
#         self.documenter_llm = ChatGroq(
#             model="llama-3.3-70b-versatile",
#             api_key=GROQ_API_K,
#             temperature=0.7
#         )
#         self.reviewer_llm = ChatGroq(
#             model="llama-3.3-70b-versatile",
#             api_key=GROQ_API_K,
#             temperature=0.7
#         )


#         # ✅ NEW FUNCTION - ADD THIS ONE
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



#     def analyze_repository_structure(self, state: DocumentationState):#-> DocumentationState
#         """Analyze repo structure"""
#         prompt = f"Analyze repo {state['repo_name']} with files: {list(state['file_contents'].keys())[:10]}"
#         try:
#             response = self.analyzer_llm.invoke([HumanMessage(content=prompt)])
#             state["initial_documentation"] = response.content
#             state["current_step"] = "analysis_complete"
#         except Exception as e:
#             state["initial_documentation"] = f"Basic analysis for {state['repo_name']}"
#             state["current_step"] = "analysis_complete"
#         return state

#     def generate_documentation(self, state: DocumentationState) -> DocumentationState:
#         """Generate docs"""
#         doc_prompt = f"Generate documentation for {state['repo_name']}:\n{state['initial_documentation']}"
#         try:
#             response = self.documenter_llm.invoke([HumanMessage(content=doc_prompt)])
#             state["reviewed_documentation"] = response.content
#             state["current_step"] = "documentation_complete"
#         except Exception as e:
#             state["error_message"] = str(e)
#             state["current_step"] = "error"
#         return state

#     def review_documentation(self, state: DocumentationState) -> DocumentationState:
#         """Refine docs"""
#         review_prompt = f"Improve documentation:\n{state['reviewed_documentation'][:8000]}"
#         try:
#             response = self.reviewer_llm.invoke([HumanMessage(content=review_prompt)])
#             state["final_documentation"] = response.content
#             state["current_step"] = "review_complete"
#         except Exception:
#             state["final_documentation"] = state["reviewed_documentation"]
#             state["current_step"] = "review_complete"
#         return state

#     def save_documentation(self, state: DocumentationState) -> DocumentationState:
#         """Save docs"""
#         docs_dir = Path("repos_docs2")
#         docs_dir.mkdir(exist_ok=True)
#         file_path = docs_dir / f"{state['repo_name']}_documentation.md"
#         with open(file_path, "w", encoding="utf-8") as f:
#             f.write(f"# Generated on {datetime.now()}\n\n")
#             f.write(state["final_documentation"])
#         state["current_step"] = "complete"
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
#     """Process a single repo"""
#     print(f"🔹 Processing repository at -> {repo_path}")

#     if repo_name is None:
#         repo_name = Path(repo_path).name

#     # Load metadata
#     metadata = {}
#     if os.path.exists(metadata_file):
#         with open(metadata_file, "r", encoding="utf-8") as f:
#             metadata = json.load(f)

#     gen = DocumentationGenerator(GROQ_API_KEY)
#     file_contents = gen.read_repository_files(repo_path)
#     if not file_contents:
#         return f"Failed: no files in {repo_name}"

#     current_hash = calculate_repo_hash(file_contents)

#     # Skip if unchanged
#     if repo_name in metadata and metadata[repo_name]["hash"] == current_hash:
#         print(f"⏩ Skipping {repo_name}: no changes detected")
#         return f"Skipped: no changes in {repo_name}"

#     # Run workflow
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
#         metadata[repo_name] = {
#             "hash": current_hash,
#             "last_updated": datetime.now().isoformat()
#         }
#         with open(metadata_file, "w", encoding="utf-8") as f:
#             json.dump(metadata, f, indent=2)
#         return f"Success: docs generated for {repo_name}"
#     return f"Failed: {final_state.get('error_message','unknown error')}"


# # ------------------------------
# # PROCESS ALL REPOS
# # ------------------------------
# def process_all_repositories(base_path="data/github_repos"):
#     print("🚀 Starting documentation generation pipeline...")
#     base = Path(base_path)
#     if not base.exists():
#         print(f"⚠️ {base} does not exist. Creating it now...")
#         base.mkdir(parents=True, exist_ok=True)
#         print(f"✅ Created folder '{base}'")
#         print("⚠️ Currently, no repositories to process. Add repos inside this folder and rerun the script.")
#         return
#     repos = [d for d in base.iterdir() if d.is_dir()]
#     for repo in repos:
#         print(f"\n--- Processing {repo.name} ---")
#         result = process_repository(str(repo), repo.name)
#         print(result)  




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



import sys
import os
sys.path.append('.')

# from config import GROQ_API_KEY
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

import hashlib
import json
import time
import re
import ast
from pathlib import Path
from typing import Dict, TypedDict, List, Set, Tuple
from datetime import datetime
from collections import defaultdict

# LangGraph and LangChain imports
from langgraph.graph import StateGraph, END
# from langchain_groq import ChatGroq
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage

# if not GROQ_API_KEY:
#     raise ValueError("❌ Missing GROQ_API_KEY in .env file")


# ============================================================================
# STATE DEFINITION
# ============================================================================
class DocumentationState(TypedDict):
    repo_path: str
    repo_name: str
    file_contents: Dict[str, str]
    file_structure: Dict[str, any]
    code_analysis: Dict[str, any]
    project_type: str
    initial_documentation: str
    reviewed_documentation: str
    final_documentation: str
    current_step: str
    error_message: str


# ============================================================================
# CODE ANALYZER - Extract functions, classes, imports
# ============================================================================
class CodeAnalyzer:
    """Advanced code analysis for Python files"""
    
    @staticmethod
    def analyze_python_file(content: str, file_path: str) -> Dict:
        """Extract functions, classes, imports from Python file"""
        analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'constants': [],
            'file_docstring': '',
            'complexity_score': 0,
            'decorators_used': set()
        }
        
        try:
            tree = ast.parse(content)
            
            # Get file docstring
            if ast.get_docstring(tree):
                analysis['file_docstring'] = ast.get_docstring(tree)
            
            for node in ast.walk(tree):
                # Extract functions
                if isinstance(node, ast.FunctionDef):
                    decorators = []
                    for d in node.decorator_list:
                        if isinstance(d, ast.Name):
                            decorators.append(d.id)
                            analysis['decorators_used'].add(d.id)
                        elif isinstance(d, ast.Attribute):
                            decorators.append(f"{d.value.id if isinstance(d.value, ast.Name) else ''}.{d.attr}")
                            analysis['decorators_used'].add(d.attr)
                    
                    func_info = {
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node) or 'No description',
                        'line_number': node.lineno,
                        'is_async': isinstance(node, ast.AsyncFunctionDef),
                        'decorators': decorators,
                        'returns': CodeAnalyzer._get_return_type(node)
                    }
                    analysis['functions'].append(func_info)
                    analysis['complexity_score'] += len(node.body)
                
                # Extract classes
                elif isinstance(node, ast.ClassDef):
                    methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                    bases = []
                    for b in node.bases:
                        if isinstance(b, ast.Name):
                            bases.append(b.id)
                        elif isinstance(b, ast.Attribute):
                            bases.append(f"{b.value.id if isinstance(b.value, ast.Name) else ''}.{b.attr}")
                    
                    class_info = {
                        'name': node.name,
                        'methods': methods,
                        'docstring': ast.get_docstring(node) or 'No description',
                        'line_number': node.lineno,
                        'bases': bases
                    }
                    analysis['classes'].append(class_info)
                
                # Extract imports
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis['imports'].append(alias.name)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        analysis['imports'].append(f"{node.module}")
                
                # Extract constants (uppercase variables)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            analysis['constants'].append(target.id)
            
            analysis['decorators_used'] = list(analysis['decorators_used'])
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    @staticmethod
    def _get_return_type(node):
        """Extract return type if annotated"""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
        return None
    
    @staticmethod
    def analyze_javascript_file(content: str) -> Dict:
        """Basic analysis for JavaScript/TypeScript files"""
        analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'exports': [],
            'react_components': []
        }
        
        # Extract function declarations
        func_pattern = r'(?:function|const|let|var)\s+(\w+)\s*=?\s*(?:function|\([^)]*\)\s*=>)'
        analysis['functions'] = re.findall(func_pattern, content)
        
        # Extract class declarations
        class_pattern = r'class\s+(\w+)'
        analysis['classes'] = re.findall(class_pattern, content)
        
        # Extract imports
        import_pattern = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
        analysis['imports'] = re.findall(import_pattern, content)
        
        # Extract exports
        export_pattern = r'export\s+(?:default\s+)?(?:class|function|const)?\s*(\w+)?'
        analysis['exports'] = [e for e in re.findall(export_pattern, content) if e]
        
        # React component detection
        if 'react' in content.lower():
            component_pattern = r'(?:function|const)\s+([A-Z]\w+)\s*(?:=|\()'
            analysis['react_components'] = re.findall(component_pattern, content)
        
        return analysis


# ============================================================================
# PROJECT TYPE DETECTOR
# ============================================================================
class ProjectTypeDetector:
    """Intelligent project type detection"""
    
    @staticmethod
    def detect_project_type(file_contents: Dict[str, str], code_analysis: Dict) -> str:
        """Detect project type from code analysis with high accuracy"""
        
        imports = set(str(imp).lower() for imp in code_analysis.get('all_imports', set()))
        all_code = ' '.join(file_contents.values()).lower()
        file_names = set(Path(f).name.lower() for f in file_contents.keys())
        
        # Machine Learning Project
        ml_libs = {'sklearn', 'tensorflow', 'keras', 'torch', 'pytorch', 'xgboost', 'lightgbm', 'catboost'}
        ml_keywords = ['model.fit', 'train_test_split', 'cross_val_score', 'fit(', 'predict(']
        if any(lib in str(imports) for lib in ml_libs) and any(kw in all_code for kw in ml_keywords):
            return "Machine Learning / Data Science"
        
        # Deep Learning
        dl_libs = {'tensorflow', 'keras', 'torch', 'pytorch'}
        if any(lib in str(imports) for lib in dl_libs) and ('neural' in all_code or 'layer' in all_code):
            return "Deep Learning / Neural Networks"
        
        # Web Framework - Flask
        if 'flask' in str(imports) and ('@app.route' in all_code or '@route' in all_code):
            return "Flask Web Application (Backend API)"
        
        # Web Framework - FastAPI
        if 'fastapi' in str(imports) and ('@app.' in all_code or 'apirouter' in str(imports)):
            return "FastAPI Web Application (Backend API)"
        
        # Web Framework - Django
        if 'django' in str(imports) and ('models.model' in all_code or 'settings.py' in file_names):
            return "Django Web Application"
        
        # React/Frontend
        if any(fw in str(imports) for fw in ['react', 'vue', 'angular']):
            return "Frontend Web Application (React/Vue/Angular)"
        
        # Data Analysis
        if 'pandas' in str(imports) and ('matplotlib' in str(imports) or 'seaborn' in str(imports)):
            if 'jupyter' in all_code or '.ipynb' in str(file_names):
                return "Jupyter Notebook Data Analysis"
            return "Data Analysis / Visualization"
        
        # ETL / Data Pipeline
        if 'airflow' in str(imports) or 'luigi' in str(imports):
            return "Data Pipeline / ETL"
        
        # CLI Tool
        if 'argparse' in str(imports) or 'click' in str(imports) or 'typer' in str(imports):
            return "Command-Line Tool (CLI)"
        
        # Web Scraping
        scraping_libs = {'selenium', 'beautifulsoup', 'bs4', 'scrapy', 'requests'}
        if any(lib in str(imports) for lib in scraping_libs) and ('soup' in all_code or 'driver' in all_code):
            return "Web Scraping / Automation"
        
        # Bot/Automation
        if 'telegram' in str(imports) or 'discord' in str(imports) or 'slack' in str(imports):
            return "Bot / Messaging Automation"
        
        # Game Development
        if 'pygame' in str(imports) or 'unity' in str(imports):
            return "Game Development"
        
        # DevOps/Infrastructure
        if 'ansible' in str(imports) or 'terraform' in all_code or 'kubernetes' in str(imports):
            return "DevOps / Infrastructure Automation"
        
        # Desktop GUI
        if any(lib in str(imports) for lib in ['tkinter', 'pyqt', 'kivy', 'wxpython']):
            return "Desktop GUI Application"
        
        # Library/Package
        if 'setup.py' in file_names or 'pyproject.toml' in file_names:
            return "Python Library / Package"
        
        # API Client
        if 'requests' in str(imports) and 'api' in all_code:
            return "API Client / Integration"
        
        # Testing Framework
        if 'pytest' in str(imports) or 'unittest' in str(imports):
            return "Testing Framework / Test Suite"
        
        return "General Python Application"


# ============================================================================
# CODE EXTRACTION UTILITIES
# ============================================================================
class CodeExtractor:
    """Extract actual code snippets from files"""
    
    @staticmethod
    def extract_function_code(file_content: str, func_name: str, line_number: int, lines_to_get: int = 20) -> str:
        """Extract function code from file"""
        lines = file_content.split('\n')
        start = max(0, line_number - 1)
        
        # Try to find the end of the function
        indent_level = None
        end = start
        for i in range(start, min(len(lines), start + 50)):
            line = lines[i]
            if line.strip() and indent_level is None:
                indent_level = len(line) - len(line.lstrip())
            elif line.strip() and indent_level is not None:
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent_level and i > start:
                    end = i
                    break
            end = i + 1
        
        return '\n'.join(lines[start:min(end, start + lines_to_get)])
    
    @staticmethod
    def extract_class_code(file_content: str, class_name: str, line_number: int, lines_to_get: int = 30) -> str:
        """Extract class code from file"""
        lines = file_content.split('\n')
        start = max(0, line_number - 1)
        end = min(len(lines), start + lines_to_get)
        return '\n'.join(lines[start:end])
    
    @staticmethod
    def get_key_functions_with_code(code_analysis: Dict, file_contents: Dict, limit: int = 5) -> str:
        """Extract key functions with actual code"""
        functions_info = []
        
        for file_path, analysis in list(code_analysis.get('python_files', {}).items())[:5]:
            for func in analysis.get('functions', [])[:limit]:
                code = file_contents.get(file_path, '')
                func_code = CodeExtractor.extract_function_code(code, func['name'], func['line_number'])
                
                decorators_str = f"@{', @'.join(func['decorators'])}" if func['decorators'] else ""
                
                functions_info.append(f"""
**Function: `{func['name']}()`** in `{file_path}` (Line {func['line_number']})
{decorators_str}
- Arguments: `{', '.join(func['args'])}`
- Description: {func['docstring'][:200]}
- Code:
```python
{func_code[:600]}
{'... [truncated]' if len(func_code) > 600 else ''}
```
""")
        
        return '\n'.join(functions_info[:limit])
    
    @staticmethod
    def get_key_classes_with_code(code_analysis: Dict, file_contents: Dict, limit: int = 3) -> str:
        """Extract key classes with actual code"""
        classes_info = []
        
        for file_path, analysis in list(code_analysis.get('python_files', {}).items())[:5]:
            for cls in analysis.get('classes', [])[:limit]:
                code = file_contents.get(file_path, '')
                class_code = CodeExtractor.extract_class_code(code, cls['name'], cls['line_number'])
                
                bases_str = f"({', '.join(cls['bases'])})" if cls['bases'] else ""
                
                classes_info.append(f"""
**Class: `{cls['name']}{bases_str}`** in `{file_path}` (Line {cls['line_number']})
- Methods: `{', '.join(cls['methods'][:8])}`
- Description: {cls['docstring'][:200]}
- Code:
```python
{class_code[:600]}
{'... [truncated]' if len(class_code) > 600 else ''}
```
""")
        
        return '\n'.join(classes_info[:limit])


# ============================================================================
# FILE STRUCTURE UTILITIES
# ============================================================================
class FileStructureHelper:
    """Helper for file structure visualization"""
    
    @staticmethod
    def create_file_tree(file_contents: Dict, max_depth: int = 3) -> str:
        """Create visual file tree"""
        tree = {}
        for file_path in sorted(file_contents.keys()):
            parts = Path(file_path).parts
            current = tree
            for i, part in enumerate(parts):
                if i >= max_depth:
                    break
                if part not in current:
                    current[part] = {}
                current = current[part]
        
        def format_tree(d, indent=0):
            lines = []
            items = sorted(d.keys())
            for idx, key in enumerate(items):
                is_last = idx == len(items) - 1
                prefix = "    " * indent + ("└── " if is_last else "├── ")
                lines.append(prefix + key)
                if d[key]:
                    lines.extend(format_tree(d[key], indent + 1))
            return lines
        
        return '\n'.join(format_tree(tree))
    
    @staticmethod
    def detect_primary_language(structure: Dict) -> str:
        """Detect primary programming language"""
        extensions = structure.get('by_extension', {})
        
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JavaScript (React)',
            '.tsx': 'TypeScript (React)',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin'
        }
        
        if extensions:
            main_ext = max(extensions, key=extensions.get)
            return language_map.get(main_ext, f'Unknown ({main_ext})')
        
        return 'Unknown'


# ============================================================================
# ENHANCED DOCUMENTATION GENERATOR
# ============================================================================
# class DocumentationGenerator:
#     def __init__(self, groq_api_key: str):
#         """Initialize with enhanced LLM models"""
#         self.analyzer_llm = ChatGroq(
#             model="llama-3.3-70b-versatile", 
#             api_key=groq_api_key,
#             temperature=0.2
#         )
#         self.documenter_llm = ChatGroq(
#             model="llama-3.3-70b-versatile",
#             api_key=groq_api_key,
#             temperature=0.3
#         )
#         self.reviewer_llm = ChatGroq(
#             model="llama-3.3-70b-versatile",
#             api_key=groq_api_key,
#             temperature=0.2
#         )
#         self.code_analyzer = CodeAnalyzer()
#         self.project_detector = ProjectTypeDetector()
#         self.code_extractor = CodeExtractor()
#         self.file_helper = FileStructureHelper()

class DocumentationGenerator:
    def __init__(self):
        """Initialize with local Ollama LLM models"""
        model_name = "gpt-oss:20b"  # or "mistral", "llama2", etc.
        self.analyzer_llm = ChatOllama(model=model_name, temperature=0.2)
        self.documenter_llm = ChatOllama(model=model_name, temperature=0.3)
        self.reviewer_llm = ChatOllama(model=model_name, temperature=0.2)

        # Other helper classes
        self.code_analyzer = CodeAnalyzer()
        self.project_detector = ProjectTypeDetector()
        self.code_extractor = CodeExtractor()
        self.file_helper = FileStructureHelper()

    def generate_summary(self, prompt: str) -> str:
        """Generate summary or documentation text using Ollama"""
        response = self.documenter_llm.invoke([HumanMessage(content=prompt)])
        text = response.content.strip()
        return text


    # ========================================================================
    # FILE READING & STRUCTURE ANALYSIS
    # ========================================================================
    
    def read_repository_files(self, repo_path: str) -> Dict[str, str]:
        """Read all relevant files with improved filtering"""
        file_contents = {}
        supported_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp',
            '.md', '.txt', '.yml', '.yaml', '.json', '.xml', 
            '.html', '.css', '.jsx', '.tsx', '.go', '.rs', '.rb',
            '.php', '.swift', '.kt', '.scala', '.sh', '.bash',
            '.sql', '.r', '.R', '.m', '.mat', '.ipynb'
        }
        
        repo_path = Path(repo_path)
        skip_dirs = {
            '.git', '__pycache__', 'node_modules', 'venv', 'env', 
            '.venv', 'dist', 'build', 'target', '.idea', '.vscode',
            'coverage', '.pytest_cache', '.mypy_cache', 'site-packages',
            'bower_components', '.next', '.nuxt'
        }
        
        all_files = []
        for f in repo_path.rglob("*"):
            if f.is_file() and f.suffix in supported_extensions:
                if any(skip_dir in f.parts for skip_dir in skip_dirs):
                    continue
                all_files.append(f)

        total_chars = 0
        print(f"📂 Found {len(all_files)} relevant files")
        
        for file_path in all_files:
            try:
                if file_path.stat().st_size > 512*1024: 
                    continue
                    
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                if len(content) > 50000:
                    content = content[:50000] + "\n... [File truncated]"
                    
                if total_chars + len(content) > 500000:  # Increased limit
                    break
                    
                file_contents[str(file_path.relative_to(repo_path))] = content
                total_chars += len(content)
                
            except Exception as e:
                print(f"⚠️ Could not read {file_path}: {e}")
        
        print(f"✅ Successfully read {len(file_contents)} files ({total_chars:,} characters)")
        return file_contents

    def analyze_file_structure(self, file_contents: Dict[str, str]) -> Dict:
        """Analyze repository structure in detail"""
        structure = {
            "total_files": len(file_contents),
            "by_extension": {},
            "by_directory": {},
            "main_files": [],
            "config_files": [],
            "source_files": [],
            "test_files": [],
            "doc_files": [],
            "frontend_files": [],
            "backend_files": [],
            "database_files": [],
            "notebook_files": []
        }
        
        for file_path in file_contents.keys():
            ext = Path(file_path).suffix or "no_extension"
            structure["by_extension"][ext] = structure["by_extension"].get(ext, 0) + 1
            
            directory = str(Path(file_path).parent)
            structure["by_directory"][directory] = structure["by_directory"].get(directory, 0) + 1
            
            file_lower = file_path.lower()
            
            # Categorize files
            if any(name in file_lower for name in ['readme', 'license', 'changelog', 'contributing']):
                structure["doc_files"].append(file_path)
            elif any(name in file_lower for name in ['test_', '_test', 'test.', 'spec.', 'tests/']):
                structure["test_files"].append(file_path)
            elif any(name in file_lower for name in ['config', 'setup', 'requirements', 'package', '.env', 'dockerfile']):
                structure["config_files"].append(file_path)
            elif any(name in file_lower for name in ['main', 'app', 'index', '__init__', 'server', 'run', 'manage']):
                structure["main_files"].append(file_path)
            elif ext == '.ipynb':
                structure["notebook_files"].append(file_path)
            elif ext in ['.html', '.css', '.jsx', '.tsx', '.vue']:
                structure["frontend_files"].append(file_path)
            elif ext in ['.sql', '.db', '.sqlite']:
                structure["database_files"].append(file_path)
            elif ext in ['.py', '.js', '.ts', '.java', '.go', '.rb']:
                structure["backend_files"].append(file_path)
            else:
                structure["source_files"].append(file_path)
        
        return structure

    def perform_code_analysis(self, file_contents: Dict[str, str]) -> Dict:
        """Perform deep code analysis on all files"""
        print("🔬 Performing deep code analysis...")
        
        code_analysis = {
            'python_files': {},
            'javascript_files': {},
            'all_imports': set(),
            'all_functions': [],
            'all_classes': [],
            'entry_points': [],
            'api_endpoints': [],
            'database_models': [],
            'decorators_used': set(),
            'test_files': []
        }
        
        for file_path, content in file_contents.items():
            ext = Path(file_path).suffix
            file_lower = file_path.lower()
            
            # Analyze Python files
            if ext == '.py':
                analysis = self.code_analyzer.analyze_python_file(content, file_path)
                code_analysis['python_files'][file_path] = analysis
                code_analysis['all_imports'].update(analysis['imports'])
                code_analysis['all_functions'].extend([f['name'] for f in analysis['functions']])
                code_analysis['all_classes'].extend([c['name'] for c in analysis['classes']])
                code_analysis['decorators_used'].update(analysis.get('decorators_used', []))
                
                # Detect entry points
                if 'if __name__' in content or 'def main()' in content:
                    code_analysis['entry_points'].append(file_path)
                
                # Detect test files
                if 'test' in file_lower or any(f['name'].startswith('test_') for f in analysis['functions']):
                    code_analysis['test_files'].append(file_path)
                
                # Detect API endpoints (Flask, FastAPI, Django)
                if '@app.route' in content or '@router.' in content:
                    routes = re.findall(r'@(?:app|router)\.(?:route|get|post|put|delete|patch)\([\'"]([^\'"]+)', content)
                    code_analysis['api_endpoints'].extend(routes)
                
                # Detect database models
                if 'class' in content:
                    for cls in analysis['classes']:
                        if any(term in cls['name'].lower() for term in ['model', 'schema', 'entity']) or \
                           any('Model' in base or 'Base' in base for base in cls.get('bases', [])):
                            code_analysis['database_models'].append(cls['name'])
            
            # Analyze JavaScript/TypeScript files
            elif ext in ['.js', '.ts', '.jsx', '.tsx']:
                analysis = self.code_analyzer.analyze_javascript_file(content)
                code_analysis['javascript_files'][file_path] = analysis
                code_analysis['all_imports'].update(analysis['imports'])
        
        print(f"✅ Analysis complete: {len(code_analysis['python_files'])} Python, {len(code_analysis['javascript_files'])} JS/TS")
        print(f"   Found: {len(code_analysis['all_functions'])} functions, {len(code_analysis['all_classes'])} classes")
        
        return code_analysis

    # ========================================================================
    # ENHANCED ANALYSIS PHASE WITH IMPROVED PROMPTS
    # ========================================================================
    
    def analyze_repository_structure(self, state: DocumentationState) -> DocumentationState:
        """Comprehensive repository analysis with project-specific prompts"""
        print(f"\n{'='*70}")
        print(f"🔍 ANALYZING REPOSITORY: {state['repo_name']}")
        print(f"{'='*70}")
        
        structure = self.analyze_file_structure(state['file_contents'])
        state['file_structure'] = structure
        
        code_analysis = self.perform_code_analysis(state['file_contents'])
        state['code_analysis'] = code_analysis
        
        # Detect project type
        project_type = self.project_detector.detect_project_type(state['file_contents'], code_analysis)
        state['project_type'] = project_type
        print(f"🎯 Detected Project Type: {project_type}")
        
        # Get real code examples
        key_functions = self.code_extractor.get_key_functions_with_code(code_analysis, state['file_contents'], limit=5)
        key_classes = self.code_extractor.get_key_classes_with_code(code_analysis, state['file_contents'], limit=3)
        
        # Get primary language
        primary_lang = self.file_helper.detect_primary_language(structure)
        
        # Create file tree
        file_tree = self.file_helper.create_file_tree(state['file_contents'])
        
        # Build enhanced analysis prompt
        prompt = self._create_enhanced_analysis_prompt(
            state, structure, code_analysis, project_type, 
            key_functions, key_classes, primary_lang, file_tree
        )

        try:
            print("🤖 Running AI analysis with enhanced prompts...")
            response = self.analyzer_llm.invoke([HumanMessage(content=prompt)])
            state["initial_documentation"] = response.content
            state["current_step"] = "analysis_complete"
            print(f"✅ Analysis complete for {state['repo_name']}")
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            state["initial_documentation"] = self._generate_comprehensive_fallback_analysis(state, structure, code_analysis)
            state["current_step"] = "analysis_complete"
            state["error_message"] = f"Analysis AI failed: {str(e)}"
        
        return state

    def _create_enhanced_analysis_prompt(self, state, structure, code_analysis, project_type, 
                                         key_functions, key_classes, primary_lang, file_tree):
        """Create project-type-specific analysis prompt"""
        
        main_libraries = sorted(list(code_analysis.get('all_imports', set())))[:20]
        
        # Project-specific questions
        specific_questions = self._get_project_specific_questions(project_type)
        
        # FIXED: Create libraries list outside f-string
        libraries_list = '\n'.join(f"- {lib}" for lib in main_libraries[:15])
        
        prompt = f"""You are analyzing a **{project_type}** project: **{state['repo_name']}**

🔍 PROJECT DETECTION: {project_type}

📊 REPOSITORY STATISTICS:
- Total Files: {structure['total_files']}
- Primary Language: {primary_lang}
- Python Files: {len(code_analysis.get('python_files', {}))}
- JavaScript/TS Files: {len(code_analysis.get('javascript_files', {}))}
- Entry Points: {', '.join(code_analysis.get('entry_points', ['Not detected'])[:3])}
- Functions: {len(code_analysis.get('all_functions', []))}
- Classes: {len(code_analysis.get('all_classes', []))}
- API Endpoints: {len(code_analysis.get('api_endpoints', []))}
- Database Models: {len(code_analysis.get('database_models', []))}

🔬 KEY LIBRARIES/FRAMEWORKS DETECTED:
{libraries_list}

📂 PROJECT STRUCTURE:
```
{file_tree[:2000]}
```

💻 ACTUAL CODE COMPONENTS:

{key_functions[:4000]}

{key_classes[:3000]}

**API Endpoints Detected:**
{self._format_list(code_analysis.get('api_endpoints', [])[:15])}

**Database Models:**
{', '.join(code_analysis.get('database_models', [])[:10])}

**Decorators Used:**
{', '.join(sorted(code_analysis.get('decorators_used', []))[:10])}

🎯 ANALYSIS REQUIREMENTS:

You MUST provide a DETAILED, SPECIFIC analysis based on the ACTUAL code shown above.

## 1. Project Overview (Be SPECIFIC)
- **Exact Purpose**: What SPECIFIC problem does this solve? (Look at function names, classes, API endpoints)
- **Project Type Confirmation**: Is this truly a {project_type}? Verify from code.
- **Target Users**: WHO uses this? (End users, developers, data scientists, etc.)
- **Key Value**: What makes this useful? What's the main benefit?
- **Input/Output**: What goes IN and what comes OUT?

## 2. Technology Stack (FROM ACTUAL IMPORTS)
- **Primary Language**: {primary_lang}
- **Frameworks**: Identify ALL frameworks (Flask={('@app.route' in str(code_analysis))}, FastAPI, React, etc.)
- **Key Libraries & Their PURPOSE**:
- For EACH library in imports, explain WHY it's used in THIS project
- Example: "pandas - used in load_data() function for CSV processing"
- **Database Technology**: {('SQLAlchemy' if 'sqlalchemy' in str(main_libraries) else 'None detected')}
- **External Services/APIs**: Any third-party integrations?

## 3. Architecture & Design
- **Architecture Pattern**: {self._suggest_architecture(project_type)}
- **Entry Point**: How does the app start? (Check: {', '.join(code_analysis.get('entry_points', [])[:2])})
- **Data Flow**: Trace how data moves through the system
- **Component Breakdown**: Identify major components from files and classes
- **Design Patterns**: Observer, Factory, Singleton, etc. (if applicable)

## 4. Core Functionality Analysis
{specific_questions}

## 5. Code Organization
- **Module Structure**: How is code organized? (by feature, by layer, etc.)
- **Key Files & Their Roles**:
- Entry Points: {', '.join(structure.get('main_files', [])[:3])}
- Core Logic: {', '.join(structure.get('backend_files', [])[:5])}
- Configuration: {', '.join(structure.get('config_files', [])[:3])}
- **File Relationships**: Which files depend on which?

## 6. Feature Inventory (FROM ACTUAL CODE)
List EVERY feature you can identify:
- Feature 1: [What it does] → Implemented in `file.py::function_name()`
- Feature 2: [What it does] → Implemented in `file.py::class_name`
(Continue for ALL major features found in code)

## 7. Configuration & Dependencies
- **Environment Variables**: What's needed? (Check for os.getenv, config files)
- **Required Files**: Data files, config files, credentials
- **External Dependencies**: Services that must be running
- **Installation Requirements**: What needs to be installed?

## 8. Technical Insights
- **Complexity Level**: Beginner/Intermediate/Advanced
- **Code Quality Indicators**: Error handling, logging, type hints, docstrings
- **Performance Considerations**: Caching, optimization, async operations
- **Security Measures**: Authentication, validation, encryption
- **Scalability**: Can it handle growth? Bottlenecks?
- **Testing**: Test coverage, testing frameworks used

## 9. Data Models (If Applicable)
- **Models Found**: {', '.join(code_analysis.get('database_models', [])[:10])}
- **Relationships**: How models relate to each other
- **Data Validation**: How is data validated?

## 10. API Documentation (If Applicable)
- **Endpoints**: {len(code_analysis.get('api_endpoints', []))} detected
- **Request/Response Formats**: JSON, XML, etc.
- **Authentication**: How are requests authenticated?

---

🚨 CRITICAL REQUIREMENTS:

1. **Use ACTUAL code evidence** - Reference specific functions, classes, files
2. **Be PRECISE** - "The RandomForestClassifier in model.py line 45" NOT "uses ML"
3. **Explain HOW** - Don't just say "processes data", explain the process
4. **Real examples** - Use actual function names, not placeholders
5. **Verify claims** - Only state what you can prove from the code
6. **Technical depth** - Go deep into implementation details

Example of GOOD analysis:
✅ "The application uses Flask (app.py:15) with 5 REST endpoints (/api/predict, /api/train, /api/status, /api/health, /api/metrics). The predict() function (model.py:78) loads a pre-trained RandomForestClassifier and makes predictions on 7 features extracted from user input via extract_features() (utils.py:34)."

Example of BAD analysis:
❌ "The application is a machine learning system that makes predictions."

Analyze NOW based on ACTUAL code."""

        return prompt
    
    def _format_list(self, items):
        """Helper method to format lists safely"""
        if not items:
            return "None detected"
        return '\n'.join(f"- {item}" for item in items)

    def _get_project_specific_questions(self, project_type: str) -> str:
        """Return project-type-specific analysis questions"""
        
        questions = {
            "Machine Learning / Data Science": """
**ML-Specific Analysis:**
- What is being PREDICTED/CLASSIFIED? (Target variable)
- What FEATURES are used? (List actual feature names from code)
- What ML ALGORITHM? (RandomForest, LogisticRegression, etc. - cite line number)
- DATA PREPROCESSING: How is data cleaned/transformed? (Show actual functions)
- TRAINING PROCESS: How is model trained? (Show train code)
- EVALUATION METRICS: Accuracy, precision, recall, RMSE? (What's actually measured?)
- MODEL PERSISTENCE: How is model saved/loaded?
- PREDICTION INTERFACE: How do you input data and get predictions?
""",
            "Deep Learning / Neural Networks": """
**Deep Learning Analysis:**
- NETWORK ARCHITECTURE: Layers, neurons, activation functions
- FRAMEWORK: TensorFlow, PyTorch, Keras?
- TRAINING: Loss function, optimizer, epochs, batch size
- DATA PIPELINE: How is training data loaded and preprocessed?
- MODEL: Show actual model definition code
- INFERENCE: How are predictions made?
""",
            "Flask Web Application (Backend API)": """
**Flask API Analysis:**
- ALL ENDPOINTS: List every @app.route with method (GET/POST/etc.)
- What does EACH endpoint do? Be specific.
- DATABASE: What database? Show model classes.
- AUTHENTICATION: How are requests authenticated?
- REQUEST/RESPONSE: What's the expected input/output format for each endpoint?
- ERROR HANDLING: How are errors handled?
- MIDDLEWARE: Any middleware used?
""",
            "FastAPI Web Application (Backend API)": """
**FastAPI Analysis:**
- ALL ENDPOINTS: List every @app.get, @app.post, etc.
- REQUEST MODELS: What Pydantic models are used?
- RESPONSE MODELS: What's returned?
- ASYNC: Which endpoints are async?
- VALIDATION: How is input validated?
- DOCUMENTATION: Is OpenAPI/Swagger auto-generated?
""",
            "Data Analysis / Visualization": """
**Data Analysis:**
- DATA SOURCES: What files/databases are analyzed?
- VISUALIZATIONS: What charts/plots are created? (bar, line, scatter, etc.)
- ANALYSIS STEPS: What transformations/calculations?
- INSIGHTS: What questions does this answer?
- OUTPUT: What's the final deliverable?
""",
            "Command-Line Tool (CLI)": """
**CLI Tool Analysis:**
- COMMANDS: What commands are available?
- ARGUMENTS: What arguments/flags does it accept?
- USAGE EXAMPLES: Show actual command examples
- INPUT: What does it operate on?
- OUTPUT: What does it produce?
""",
            "Web Scraping / Automation": """
**Scraping Analysis:**
- TARGET SITES: What websites are scraped?
- DATA EXTRACTED: What specific data is collected?
- SCRAPING METHOD: BeautifulSoup, Selenium, API?
- STORAGE: Where is data saved?
- RATE LIMITING: Any delays/throttling?
"""
        }
        
        return questions.get(project_type, """
**General Analysis:**
- MAIN FUNCTIONALITY: What does this application do?
- KEY OPERATIONS: What are the main operations/processes?
- USER INTERACTION: How do users interact with it?
- DATA HANDLING: How is data processed?
""")

    def _suggest_architecture(self, project_type: str) -> str:
        """Suggest likely architecture based on project type"""
        architectures = {
            "Machine Learning / Data Science": "Pipeline (Data → Preprocessing → Training → Evaluation)",
            "Flask Web Application (Backend API)": "MVC or REST API",
            "FastAPI Web Application (Backend API)": "REST API with async support",
            "Django Web Application": "MVT (Model-View-Template)",
            "Frontend Web Application (React/Vue/Angular)": "Component-based",
            "Command-Line Tool (CLI)": "Procedural or Command pattern",
            "Data Analysis / Visualization": "Notebook-based or Pipeline"
        }
        return architectures.get(project_type, "Unknown - analyze from code")

    # ========================================================================
    # ENHANCED DOCUMENTATION GENERATION
    # ========================================================================
    
    def generate_documentation(self, state: DocumentationState) -> DocumentationState:
        """Generate project-type-specific documentation"""
        print(f"\n{'='*70}")
        print(f"📝 GENERATING DOCUMENTATION: {state['repo_name']}")
        print(f"{'='*70}")
        
        project_type = state.get('project_type', 'General Python Application')
        structure = state['file_structure']
        code_analysis = state['code_analysis']
        
        # Create project-specific documentation prompt
        doc_prompt = self._create_enhanced_documentation_prompt(
            state, project_type, structure, code_analysis
        )

        try:
            print(f"🤖 Generating {project_type} documentation...")
            print("⏳ This may take 30-60 seconds...")
            response = self.documenter_llm.invoke([HumanMessage(content=doc_prompt)])
            state["reviewed_documentation"] = response.content
            state["current_step"] = "documentation_complete"
            print(f"✅ Documentation generated for {state['repo_name']}")
        except Exception as e:
            print(f"❌ Documentation generation failed: {e}")
            state["error_message"] = f"Documentation AI failed: {str(e)}"
            state["reviewed_documentation"] = self._generate_comprehensive_fallback_docs(state)
            state["current_step"] = "documentation_complete"
        
        return state

    def _create_enhanced_documentation_prompt(self, state, project_type, structure, code_analysis):
        """Create project-type-specific documentation prompt"""
        
        # Get actual code samples
        main_file = structure.get('main_files', [''])[0] if structure.get('main_files') else ''
        main_code = state['file_contents'].get(main_file, '')[:3000] if main_file else ''
        
        template = self._get_documentation_template_for_type(project_type, state['repo_name'], code_analysis)
        
        prompt = f"""Generate PRODUCTION-QUALITY, PROJECT-SPECIFIC documentation for: **{state['repo_name']}**

📋 PROJECT TYPE: {project_type}

🔬 TECHNICAL ANALYSIS COMPLETED:
{state['initial_documentation'][:15000]}

💻 MAIN FILE CODE:
```python
{main_code}
```

📊 CODE METRICS:
- Functions: {len(code_analysis.get('all_functions', []))}
- Classes: {len(code_analysis.get('all_classes', []))}
- API Endpoints: {len(code_analysis.get('api_endpoints', []))}
- Entry Points: {', '.join(code_analysis.get('entry_points', [])[:3])}

🎯 DOCUMENTATION TEMPLATE:

{template}

---

🚨 CRITICAL REQUIREMENTS:

1. **REAL CODE ONLY** - Use ACTUAL function/class names, file paths, code snippets from the repository
2. **NO PLACEHOLDERS** - Never write "your_function()", "example.py", or "sample_data"
3. **WORKING EXAMPLES** - Every code example must be runnable
4. **SPECIFIC COMMANDS** - Show exact commands with real file names
5. **ACTUAL ENDPOINTS** - Use real API routes from code_analysis
6. **REAL CONFIGURATION** - Show actual config variables from code
7. **PRECISE EXPLANATIONS** - Explain HOW and WHY, not just WHAT
8. **ADD ARCHITECTURE DIAGRAMS** - Include Mermaid diagrams for flow and architecture
9. **ADD CODE STRUCTURE SECTION** - Detailed explanation of project organization

VALIDATION CHECKLIST (verify before submitting):
✅ Every code block contains real code from the repo
✅ Every file path mentioned actually exists
✅ Every function/class name is from actual code
✅ All installation commands will actually work
✅ All examples can be copy-pasted and run
✅ Mermaid diagrams are syntactically correct
✅ No generic placeholders anywhere
✅ Architecture diagram included
✅ Data flow diagram included (if applicable)
✅ Code structure section is detailed

Generate COMPLETE, DETAILED, PRODUCTION-READY documentation NOW."""

        return prompt

    def _get_documentation_template_for_type(self, project_type, repo_name, code_analysis):
        """Return project-type-specific documentation template"""
        
        if "Machine Learning" in project_type or "Deep Learning" in project_type:
            return self._ml_documentation_template(repo_name, code_analysis)
        elif "Flask" in project_type or "FastAPI" in project_type:
            return self._api_documentation_template(repo_name, code_analysis, project_type)
        elif "CLI" in project_type:
            return self._cli_documentation_template(repo_name, code_analysis)
        elif "Data Analysis" in project_type:
            return self._data_analysis_template(repo_name, code_analysis)
        else:
            return self._general_documentation_template(repo_name, code_analysis)

    def _ml_documentation_template(self, repo_name, code_analysis):
        """ML/DS project documentation template"""
        # Create endpoint lists safely
        endpoints_list = '\n'.join(f"- `{endpoint}`" for endpoint in code_analysis.get('api_endpoints', [])[:20])
        models_list = '\n'.join(f"- {model}" for model in code_analysis.get('database_models', [])[:10])
        
        return f"""
# {repo_name} - Machine Learning Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Problem Statement](#problem-statement)
3. [Dataset](#dataset)
4. [Methodology](#methodology)
5. [Installation](#installation)
6. [Usage](#usage)
7. [Model Details](#model-details)
8. [Results](#results)
9. [Architecture](#architecture)
10. [Code Structure](#code-structure)
11. [Data Flow](#data-flow)

---

## 🎯 Overview

### Project Goal
[What is being predicted/classified? Be SPECIFIC from actual code]

### Problem Type
- [ ] Classification
- [ ] Regression
- [ ] Clustering
- [ ] Other: ___

### Target Variable
**Target:** `[actual target column name from code]`

### Performance
- **Accuracy/Score:** [if mentioned in code]
- **Evaluation Metric:** [actual metric used]

---

## 📊 Dataset

### Data Source
[Where does the data come from? Show actual file paths or URLs from code]

### Features Used
Show ACTUAL features from the code:

| Feature Name | Description | Type | Example Value |
|--------------|-------------|------|---------------|
| [real_feature_1] | [purpose] | numeric/categorical | [value] |
| [real_feature_2] | [purpose] | numeric/categorical | [value] |

### Data Loading
```python
# ACTUAL data loading code from repository
[paste real code here from actual file]
```

---

## 🔬 Methodology

### 1. Data Preprocessing

Show ACTUAL preprocessing steps from code:

```python
# Real preprocessing code
[actual code from repo with real function names]
```

**Steps:**
1. [Actual step 1 - cite function and file]
2. [Actual step 2 - cite function and file]
3. [Actual step 3 - cite function and file]

### 2. Feature Engineering

```python
# Actual feature engineering code
[real code with actual function names]
```

### 3. Model Training

**Algorithm Used:** [RandomForestClassifier/LogisticRegression/etc. - from actual code with line number]

```python
# ACTUAL model training code with real hyperparameters
[real training code from repository]
```

**Hyperparameters:**
- `parameter1`: [actual value from code]
- `parameter2`: [actual value from code]

### 4. Model Evaluation

```python
# Real evaluation code
[actual metrics calculation from code]
```

---

## 🏗️ Architecture

### System Architecture

```mermaid
graph TD
    A[Data Input] --> B[Data Preprocessing]
    B --> C[Feature Engineering]
    C --> D[Model Training]
    D --> E[Model Evaluation]
    E --> F[Model Deployment]
    F --> G[Prediction API]
    
    style A fill:#e1f5ff
    style D fill:#fff3e0
    style G fill:#f3e5f5
```

### Component Architecture

```mermaid
graph LR
    subgraph Data Layer
        D1[Raw Data]
        D2[Processed Data]
    end
    
    subgraph Model Layer
        M1[Preprocessing Pipeline]
        M2[ML Model]
        M3[Prediction Engine]
    end
    
    subgraph API Layer
        A1[REST API]
        A2[Response Handler]
    end
    
    D1 --> M1
    M1 --> D2
    D2 --> M2
    M2 --> M3
    M3 --> A1
    A1 --> A2
```

---

## 🔄 Data Flow

### Training Flow

```mermaid
sequenceDiagram
    participant U as User
    participant D as Data Loader
    participant P as Preprocessor
    participant M as Model
    participant E as Evaluator
    
    U->>D: Load training data
    D->>P: Raw data
    P->>P: Clean & transform
    P->>M: Processed features
    M->>M: Train model
    M->>E: Trained model
    E->>E: Calculate metrics
    E->>U: Performance report
```

### Prediction Flow

```mermaid
sequenceDiagram
    participant U as User/API
    participant V as Validator
    participant P as Preprocessor
    participant M as Model
    participant R as Response
    
    U->>V: Input data
    V->>V: Validate format
    V->>P: Valid data
    P->>P: Apply transformations
    P->>M: Processed features
    M->>M: Make prediction
    M->>R: Prediction result
    R->>U: JSON response
```

---

## 🚀 Installation

### Prerequisites
```bash
Python 3.x
[list actual requirements from requirements.txt]
```

### Setup
```bash
# Clone repository
git clone [actual url if available]
cd {repo_name}

# Install dependencies (use ACTUAL requirements file name)
pip install -r requirements.txt

# [Any other setup steps from actual code]
```

---

## 📘 Usage

### Training the Model

```bash
# Show ACTUAL command to train from code
python [actual_training_file.py] [actual_arguments]
```

### Making Predictions

```python
# REAL prediction code with actual function/class names
from [actual_module] import [actual_class]

# Use REAL feature names from code
[actual prediction code from repository]
```

### Example

```python
# Complete working example from repository
[full example code with real function names and parameters]
```

---

## 🤖 Model Details

### Architecture
[Describe actual model architecture from code - layers, parameters, etc.]

### Training Process
1. [Step 1 from actual training code with file reference]
2. [Step 2 from actual training code with file reference]
3. [Step 3 from actual training code with file reference]

### Model Persistence
```python
# How model is saved/loaded (actual code)
[real save/load code from repository]
```

---

## 📈 Results

[Include any results/metrics from code, comments, or documentation]

**Performance Metrics:**
- Metric 1: [value if available]
- Metric 2: [value if available]

---

## 📂 Code Structure

```
{repo_name}/
├── [actual_file_1.py]     # [Purpose from analysis - be specific]
│   ├── [actual_function_1]()  # [What it does]
│   └── [actual_class_1]       # [What it does]
├── [actual_file_2.py]     # [Purpose from analysis]
│   ├── [actual_function_2]()  # [What it does]
│   └── [actual_function_3]()  # [What it does]
└── [actual_file_3.py]     # [Purpose from analysis]
    └── [actual_class_2]       # [What it does]
```

### Key Files Explained

#### `[actual_main_file.py]`
**Purpose:** [Detailed explanation of what this file does]

**Key Components:**
- `actual_function_1()`: [What it does, parameters, returns]
- `actual_function_2()`: [What it does, parameters, returns]
- `ActualClass`: [What it does, key methods]

**Dependencies:**
- [List actual imported modules]

#### `[actual_data_file.py]`
**Purpose:** [Detailed explanation]

**Key Components:**
- [List actual functions/classes with purposes]

---

## 🔧 Configuration

### Environment Variables
```bash
# Actual environment variables from code
[REAL_ENV_VAR_1]=[description]
[REAL_ENV_VAR_2]=[description]
```

### Configuration Files
- `[actual_config_file]`: [What it configures]

---

## 🧪 Testing

[If test files exist]
```bash
# Run tests (actual command)
python -m pytest [actual_test_directory]
```

---

## 📝 API Reference (If Applicable)

### Endpoints

{endpoints_list}

---

## 🤝 Contributing

[Standard contributing guidelines]

---

## 📄 License

[License information if available in repo]

---

*Documentation generated with enhanced AI analysis including architecture diagrams and detailed code structure*
"""

    def _api_documentation_template(self, repo_name, code_analysis, project_type):
        """API documentation template"""
        endpoints = code_analysis.get('api_endpoints', [])
        models = code_analysis.get('database_models', [])
        
        # Create lists safely
        endpoints_list = '\n'.join(f"- `{endpoint}`" for endpoint in endpoints[:20])
        models_list = '\n'.join(f"#### `{model}`\n[Description from code]\n" for model in models[:5])
        
        return f"""
# {repo_name} - API Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [API Endpoints](#api-endpoints)
3. [Installation](#installation)
4. [Running the API](#running-the-api)
5. [Authentication](#authentication)
6. [Database Schema](#database-schema)
7. [Architecture](#architecture)
8. [Code Structure](#code-structure)
9. [API Flow](#api-flow)

---

## 🎯 Overview

**Framework:** {project_type}
**Base URL:** `http://localhost:[port from code]`
**Endpoints:** {len(endpoints)} routes

### Quick Start
```bash
# Start the API
python [actual_main_file.py]
```

---

## 🏗️ Architecture

### System Architecture

```mermaid
graph TD
    A[Client Request] --> B[API Gateway]
    B --> C{{Route Handler}}
    C --> D[Business Logic]
    C --> E[Authentication]
    D --> F[(Database)]
    E --> D
    D --> G[Response]
    G --> A
    
    style A fill:#e1f5ff
    style C fill:#fff3e0
    style F fill:#f3e5f5
```

### API Architecture

```mermaid
graph LR
    subgraph Client Layer
        C1[Web Client]
        C2[Mobile App]
        C3[API Consumer]
    end
    
    subgraph API Layer
        A1[Routes]
        A2[Controllers]
        A3[Middleware]
    end
    
    subgraph Business Layer
        B1[Services]
        B2[Validators]
    end
    
    subgraph Data Layer
        D1[(Database)]
        D2[Models]
    end
    
    C1 --> A1
    C2 --> A1
    C3 --> A1
    A1 --> A3
    A3 --> A2
    A2 --> B1
    B1 --> B2
    B2 --> D2
    D2 --> D1
```

---

## 🔄 API Flow

### Request Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant M as Middleware
    participant R as Route Handler
    participant S as Service
    participant D as Database
    
    C->>M: HTTP Request
    M->>M: Authenticate
    M->>R: Validated Request
    R->>R: Parse & Validate
    R->>S: Business Logic
    S->>D: Query Data
    D->>S: Return Data
    S->>R: Processed Data
    R->>C: JSON Response
```

---

## 🔌 API Endpoints

### Complete Endpoint List

{endpoints_list}

### Detailed Documentation

[For each endpoint, provide:]

#### `POST /api/example`

**Description:** [What this endpoint does - from actual code]

**Request:**
```bash
curl -X POST http://localhost:5000/api/example \\
  -H "Content-Type: application/json" \\
  -d '[actual request body structure from code]'
```

**Request Body:**
```json
{{
  "field1": "value",
  "field2": "value"
}}
```

**Response:**
```json
{{
  "status": "success",
  "data": {{}}
}}
```

**Code Implementation:**
```python
# Actual route handler code from repository
[paste real code]
```

---

## 🚀 Installation

```bash
# Clone
git clone [url]
cd {repo_name}

# Install (use ACTUAL requirements file)
pip install -r requirements.txt

# Setup database (if applicable - actual commands from code)
[actual setup commands]

# Set environment variables
export API_KEY=[value]
export DATABASE_URL=[value]
```

---

## ▶️ Running the API

```bash
# ACTUAL command to start server from code
python [actual_main_file.py]

# Or if using Flask
flask run

# Or if using uvicorn (FastAPI)
uvicorn [actual_module]:app --reload
```

Server will start on: `http://localhost:[actual_port from code]`

---

## 🔐 Authentication

[Describe actual authentication method from code]

```python
# Actual authentication code
[real auth code from repository]
```

---

## 🗄️ Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    USER ||--o{{ ORDER : places
    USER {{
        int id PK
        string email
        string password_hash
        datetime created_at
    }}
    ORDER {{
        int id PK
        int user_id FK
        decimal total
        datetime created_at
    }}
    ORDER ||--|{{ ORDER_ITEM : contains
    ORDER_ITEM {{
        int id PK
        int order_id FK
        int product_id FK
        int quantity
    }}
```

### Models

{models_list}

---

## 📂 Code Structure

```
{repo_name}/
├── [actual_api_file.py]       # API routes and endpoints
│   ├── @app.route('/endpoint1')  # [Purpose]
│   └── @app.route('/endpoint2')  # [Purpose]
├── [actual_models_file.py]    # Database models
│   ├── class Model1          # [Purpose]
│   └── class Model2          # [Purpose]
├── [actual_services_file.py]  # Business logic
│   ├── service_function_1()  # [Purpose]
│   └── service_function_2()  # [Purpose]
└── [actual_config_file.py]    # Configuration
```

### Key Components

#### Routes (`[actual_routes_file.py]`)
**Purpose:** [Detailed explanation]

**Endpoints:**
- `[actual_endpoint]`: [What it does]

#### Models (`[actual_models_file.py]`)
**Purpose:** [Detailed explanation]

**Models:**
- `[ActualModel]`: [What it represents]

---

## 🧪 Testing

```bash
# Run tests (actual command from code)
pytest [actual_test_directory]
```

---

## 📊 Monitoring

[If logging/monitoring code exists]

```python
# Actual logging code
[real monitoring/logging code]
```

---

*API Documentation with architecture diagrams and complete code structure*
"""

    def _cli_documentation_template(self, repo_name, code_analysis):
        """CLI tool documentation template"""
        return f"""
# {repo_name} - Command-Line Tool Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Commands](#commands)
5. [Examples](#examples)
6. [Architecture](#architecture)
7. [Code Structure](#code-structure)

---

## 🎯 Overview

[Description of what the CLI tool does - from actual code analysis]

**Main Features:**
- [Feature 1 from code]
- [Feature 2 from code]
- [Feature 3 from code]

---

## 🏗️ Architecture

### CLI Flow

```mermaid
graph TD
    A[User Command] --> B[Argument Parser]
    B --> C{{Command Router}}
    C --> D[Command Handler 1]
    C --> E[Command Handler 2]
    C --> F[Command Handler 3]
    D --> G[Execute Logic]
    E --> G
    F --> G
    G --> H[Output Result]
    
    style A fill:#e1f5ff
    style C fill:#fff3e0
    style H fill:#f3e5f5
```

---

## 🚀 Installation

```bash
# Clone repository
git clone [url]
cd {repo_name}

# Install dependencies
pip install -r requirements.txt

# Install CLI tool
pip install -e .
```

---

## 📘 Usage

### Basic Command Structure

```bash
python [actual_main_file.py] [command] [options] [arguments]
```

---

## 🔧 Commands

[List ACTUAL commands from argparse/click in code]

### Command 1: `[actual_command_name]`

**Description:** [What it does from code]

**Usage:**
```bash
python [actual_file] [actual_command] [actual_flags]
```

**Options:**
- `--flag1`: [Description from code]
- `--flag2`: [Description from code]

**Examples:**
```bash
# Example 1 (REAL command from code)
python [actual_file] [actual_command] --flag value

# Example 2
python [actual_file] [actual_command] input.txt
```

---

## 📂 Code Structure

```
{repo_name}/
├── [actual_cli_file.py]      # Main CLI entry point
│   ├── main()                # Entry function
│   └── [command_function]()  # Command handler
└── [actual_utils_file.py]    # Helper functions
```

---

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/
```

---

*CLI Documentation with flow diagrams*
"""

    def _data_analysis_template(self, repo_name, code_analysis):
        """Data analysis documentation template"""
        return f"""
# {repo_name} - Data Analysis Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Dataset](#dataset)
3. [Analysis Steps](#analysis-steps)
4. [Visualizations](#visualizations)
5. [Results](#results)
6. [Architecture](#architecture)
7. [Code Structure](#code-structure)

---

## 🎯 Overview

[What data is being analyzed and why - from actual code]

---

## 🏗️ Architecture

### Analysis Pipeline

```mermaid
graph LR
    A[Raw Data] --> B[Data Loading]
    B --> C[Data Cleaning]
    C --> D[Data Transformation]
    D --> E[Analysis]
    E --> F[Visualization]
    F --> G[Insights/Report]
    
    style A fill:#e1f5ff
    style E fill:#fff3e0
    style G fill:#f3e5f5
```

---

## 📊 Dataset

**Data Sources:**
- [Actual data file 1 from code]
- [Actual data file 2 from code]

**Data Structure:**
[Show actual column names and types from code]

---

## 🔬 Analysis Steps

### 1. Data Loading
```python
# Actual data loading code
[real code from repository]
```

### 2. Data Cleaning
```python
# Actual cleaning code
[real code from repository]
```

### 3. Analysis
```python
# Actual analysis code
[real code from repository]
```

---

## 📈 Visualizations

[List actual plots/charts created in code]

1. **[Chart Type]**: [What it shows]
   ```python
   # Actual plotting code
   [real code]
   ```

---

## 📂 Code Structure

```
{repo_name}/
├── [actual_analysis_file.py]   # Main analysis
├── [actual_data_file.csv]      # Dataset
└── [actual_output_dir]/         # Results
```

---

*Data Analysis Documentation with pipeline diagrams*
"""

    def _general_documentation_template(self, repo_name, code_analysis):
        """General project documentation template"""
        funcs_list = '\n'.join(f"- `{func}()` - [Purpose]" for func in code_analysis.get('all_functions', [])[:10])
        
        return f"""
# {repo_name} - Project Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Architecture](#architecture)
6. [Code Structure](#code-structure)
7. [Configuration](#configuration)

---

## 🎯 Overview

[Specific description from analysis - what this project does]

**Key Capabilities:**
- [Capability 1 from code]
- [Capability 2 from code]
- [Capability 3 from code]

---

## 🏗️ Architecture

### System Overview

```mermaid
graph TD
    A[Input] --> B[Processing Module]
    B --> C[Core Logic]
    C --> D[Output Handler]
    D --> E[Result]
    
    style A fill:#e1f5ff
    style C fill:#fff3e0
    style E fill:#f3e5f5
```

### Component Interaction

```mermaid
graph LR
    subgraph Input Layer
        I1[User Input]
        I2[File Input]
    end
    
    subgraph Processing Layer
        P1[Validator]
        P2[Processor]
    end
    
    subgraph Output Layer
        O1[Formatter]
        O2[Output Handler]
    end
    
    I1 --> P1
    I2 --> P1
    P1 --> P2
    P2 --> O1
    O1 --> O2
```

---

## ✨ Features

{funcs_list}

---

## 🚀 Installation

```bash
# Clone repository
git clone [url]
cd {repo_name}

# Install dependencies (actual requirements file)
pip install -r requirements.txt
```

---

## 📘 Usage

### Basic Usage

```python
# ACTUAL usage from repository
from [actual_module] import [actual_class]

# Real example with actual function names
[actual code example]
```

### Advanced Usage

```python
# More complex example from actual code
[real advanced example]
```

---

## 🔄 Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant I as Input Handler
    participant P as Processor
    participant O as Output
    
    U->>I: Provide input
    I->>I: Validate
    I->>P: Process data
    P->>P: Execute logic
    P->>O: Generate output
    O->>U: Return result
```

---

## 📂 Code Structure

```
{repo_name}/
├── [actual_file_1.py]     # [Purpose from analysis]
│   ├── [actual_function_1]()  # [What it does]
│   ├── [actual_function_2]()  # [What it does]
│   └── [ActualClass]          # [What it does]
├── [actual_file_2.py]     # [Purpose from analysis]
│   └── [actual_function_3]()  # [What it does]
└── [actual_file_3.py]     # [Purpose from analysis]
```

### File Descriptions

#### `[actual_main_file.py]`
**Purpose:** [Detailed explanation]

**Key Components:**
- `[actual_function]()`: [Detailed description with parameters and return values]
- `[ActualClass]`: [What it does, key methods]

**Code Example:**
```python
# Real code from this file
[actual code snippet]
```

---

## ⚙️ Configuration

### Environment Variables
```bash
# Actual environment variables from code
[REAL_VAR_1]=[description]
[REAL_VAR_2]=[description]
```

### Configuration Files
- `[actual_config_file]`: [What it configures]

---

## 🧪 Testing

```bash
# Run tests (actual command)
python -m pytest [actual_test_dir]
```

---

## 🤝 Contributing

[Standard contributing guidelines]

---

## 📄 License

[License information if available]

---

*Comprehensive documentation with architecture and flow diagrams*
"""

    # ========================================================================
    # REVIEW & ENHANCEMENT
    # ========================================================================
    
    def review_documentation(self, state: DocumentationState) -> DocumentationState:
        """Review with focus on accuracy and completeness"""
        print(f"\n{'='*70}")
        print(f"🔍 REVIEWING DOCUMENTATION: {state['repo_name']}")
        print(f"{'='*70}")
        
        review_prompt = f"""Review and ENHANCE this documentation to PRODUCTION quality.

PROJECT: {state['repo_name']}
TYPE: {state.get('project_type', 'Unknown')}

CURRENT DOCUMENTATION:
{state['reviewed_documentation'][:20000]}

🔍 REVIEW CHECKLIST:

1. **Accuracy Verification**
   ✅ All file names are real (not "example.py" or "your_file.py")
   ✅ All function names exist in the codebase
   ✅ All commands are runnable
   ✅ All code snippets are from actual repository
   ✅ All paths are correct

2. **Completeness Check**
   ✅ Installation steps are complete and testable
   ✅ Usage examples are comprehensive
   ✅ All major features are documented
   ✅ Configuration is explained
   ✅ API endpoints (if any) are all listed
   ✅ Architecture diagrams are included
   ✅ Data flow diagrams are included
   ✅ Code structure section is detailed

3. **Quality Standards**
   ✅ Explanations are clear and detailed
   ✅ Code examples include comments
   ✅ Mermaid diagrams are syntactically correct
   ✅ No placeholder text remains
   ✅ Technical depth is appropriate

4. **Practical Usability**
   ✅ A new developer can immediately use this
   ✅ Setup instructions will actually work
   ✅ Examples can be copy-pasted and run
   ✅ Troubleshooting guidance (if needed)

🎯 ENHANCEMENT TASKS:

1. Replace ANY remaining placeholders with specifics
2. Add more detail to thin sections
3. Include more code examples where helpful
4. Ensure all diagrams render correctly
5. Add "Quick Start" if missing
6. Verify technical accuracy of all claims
7. Ensure architecture diagrams show actual components
8. Verify data flow matches actual code flow
9. Ensure code structure section lists real files

Return ENHANCED, PRODUCTION-READY documentation with proper diagrams."""

        try:
            print("🤖 Reviewing and enhancing...")
            response = self.reviewer_llm.invoke([HumanMessage(content=review_prompt)])
            state["final_documentation"] = response.content
            state["current_step"] = "review_complete"
            print(f"✅ Documentation reviewed for {state['repo_name']}")
        except Exception as e:
            print(f"⚠️ Review failed, using generated version: {e}")
            state["final_documentation"] = state["reviewed_documentation"]
            state["current_step"] = "review_complete"
        
        return state

    # ========================================================================
    # SAVE DOCUMENTATION
    # ========================================================================
    
    def save_documentation(self, state: DocumentationState) -> DocumentationState:
        """Save comprehensive documentation with metadata"""
        print(f"\n{'='*70}")
        print(f"💾 SAVING DOCUMENTATION: {state['repo_name']}")
        print(f"{'='*70}")
        
        docs_dir = Path("repos_docs2")
        docs_dir.mkdir(exist_ok=True)
        file_path = docs_dir / f"{state['repo_name']}_documentation.md"
        
        try:
            structure = state.get('file_structure', {})
            code_analysis = state.get('code_analysis', {})
            project_type = state.get('project_type', 'Unknown')
            
            # Create language distribution list safely
            lang_dist = '\n'.join(
                f"- `{ext}`: {count} file(s)" 
                for ext, count in sorted(structure.get('by_extension', {}).items(), key=lambda x: x[1], reverse=True)[:10]
            )
            
            # Create comprehensive documentation
            full_doc = f"""{state['final_documentation']}

---

## 📊 Project Metrics

**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}

**Project Type:** {project_type}

**Repository Statistics:**
- Total Files: {structure.get('total_files', 0)}
- Python Files: {len(code_analysis.get('python_files', {}))}
- JavaScript/TypeScript Files: {len(code_analysis.get('javascript_files', {}))}
- Total Functions: {len(code_analysis.get('all_functions', []))}
- Total Classes: {len(code_analysis.get('all_classes', []))}
- Entry Points: {len(code_analysis.get('entry_points', []))}
- API Endpoints: {len(code_analysis.get('api_endpoints', []))}
- Database Models: {len(code_analysis.get('database_models', []))}
- Test Files: {len(code_analysis.get('test_files', []))}

**Language Distribution:**
{lang_dist}
"""
            
            if code_analysis.get('decorators_used'):
                decorators = ', '.join(sorted(code_analysis['decorators_used'])[:10])
                full_doc += f"\n\n**Decorators Used:** {decorators}"
            
            full_doc += f"""

---

## 🔗 Quick Navigation

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Code Structure](#code-structure)
- [API Reference](#api-endpoints) (if applicable)

---

*📅 Documentation Version: 3.0*  
*🤖 AI-Powered Documentation Generator with Enhanced Analysis*  
*⭐ Production-Ready with Architecture & Flow Diagrams*  
*🎯 Project Type: {project_type}*
"""
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(full_doc)
            
            state["current_step"] = "complete"
            file_size = file_path.stat().st_size
            print(f"✅ Documentation saved to {file_path}")
            print(f"📄 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            print(f"🎯 Project Type: {project_type}")
            
        except Exception as e:
            print(f"❌ Failed to save documentation: {e}")
            state["error_message"] = str(e)
        
        return state

    # ========================================================================
    # FALLBACK METHODS
    # ========================================================================
    
    def _generate_comprehensive_fallback_analysis(self, state: DocumentationState, structure: Dict, code_analysis: Dict) -> str:
        """Generate comprehensive fallback analysis"""
        project_type = state.get('project_type', 'Unknown')
        return f"""# Technical Analysis: {state['repo_name']}

## Project Type
{project_type}

## Project Overview
This repository contains {structure['total_files']} files implementing a {project_type} solution.

## Technology Stack
- **Primary Language:** {self.file_helper.detect_primary_language(structure)}
- **Files:** {structure['total_files']} total
- **Entry Points:** {', '.join(code_analysis.get('entry_points', ['Not detected']))}

## Code Structure
- Functions: {len(code_analysis.get('all_functions', []))}
- Classes: {len(code_analysis.get('all_classes', []))}
- API Endpoints: {len(code_analysis.get('api_endpoints', []))}
- Database Models: {len(code_analysis.get('database_models', []))}

## File Organization
- Backend Files: {len(structure['backend_files'])}
- Frontend Files: {len(structure['frontend_files'])}
- Configuration: {len(structure['config_files'])}
- Tests: {len(code_analysis.get('test_files', []))}

## Key Components
{self._format_list(code_analysis.get('all_functions', [])[:20])}
"""
    
    def _generate_comprehensive_fallback_docs(self, state: DocumentationState) -> str:
        """Generate comprehensive fallback documentation"""
        structure = state.get('file_structure', {})
        code_analysis = state.get('code_analysis', {})
        project_type = state.get('project_type', 'Unknown')
        
        funcs_list = '\n'.join(f"- `{func}()`" for func in code_analysis.get('all_functions', [])[:15])
        
        return f"""# {state['repo_name']} - Documentation

**Project Type:** {project_type}

## 📋 Overview

{state.get('initial_documentation', 'A software project with multiple components.')}

### Quick Stats
- **Project Type:** {project_type}
- **Total Files:** {structure.get('total_files', 0)}
- **Primary Language:** {self.file_helper.detect_primary_language(structure)}
- **Functions:** {len(code_analysis.get('all_functions', []))}
- **Classes:** {len(code_analysis.get('all_classes', []))}

## ✨ Features

Based on code analysis:
{funcs_list}

## 🚀 Installation

```bash
git clone [repository-url]
cd {state['repo_name']}
pip install -r requirements.txt
```

## 📘 Usage

Entry points detected: {', '.join(code_analysis.get('entry_points', ['app.py']))}

```bash
python {code_analysis.get('entry_points', ['app.py'])[0]}
```

## 📂 Code Structure

```
{state['repo_name']}/
{self.file_helper.create_file_tree(state['file_contents'], max_depth=2)}
```

## ⚙️ Configuration

Configuration files: {', '.join(structure.get('config_files', [])[:5])}

---

*Note: This is an auto-generated fallback documentation.*
"""


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_repo_hash(file_contents: Dict[str, str]) -> str:
    """Calculate MD5 hash of repository contents"""
    md5 = hashlib.md5()
    for path, content in sorted(file_contents.items()):
        md5.update(path.encode("utf-8"))
        md5.update(content.encode("utf-8"))
    return md5.hexdigest()


# ============================================================================
# WORKFLOW CREATION
# ============================================================================

def create_documentation_workflow():
    """Create and configure documentation workflow"""
    # gen = DocumentationGenerator(GROQ_API_KEY)
    gen = DocumentationGenerator()
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


# ============================================================================
# REPOSITORY PROCESSING
# ============================================================================

def process_repository(repo_path: str, repo_name: str = None, metadata_file="repo_doc_metadata.json"):
    """Process repository with enhanced production-level documentation"""
    print(f"\n{'='*70}")
    print(f"🔹 PROCESSING REPOSITORY: {repo_path}")
    print(f"{'='*70}")

    if repo_name is None:
        repo_name = Path(repo_path).name

    metadata = {}
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except:
            metadata = {}

    # gen = DocumentationGenerator(GROQ_API_KEY)
    gen = DocumentationGenerator()

    print(f"📂 Reading repository files...")
    file_contents = gen.read_repository_files(repo_path)
    
    if not file_contents:
        print(f"⚠️ No supported files found in {repo_name}")
        return f"Failed: no files in {repo_name}"

    current_hash = calculate_repo_hash(file_contents)

    # Check if documentation file exists
    docs_dir = Path("repos_docs2")
    doc_file = docs_dir / f"{repo_name}_documentation.md"
    
    if doc_file.exists() and repo_name in metadata and metadata[repo_name].get("hash") == current_hash:
        print(f"⏩ Skipping {repo_name}: no changes detected and docs exist")
        return f"Skipped: no changes in {repo_name}"
    
    if not doc_file.exists():
        print(f"📝 Documentation file missing for {repo_name}, generating...")

    print(f"🚀 Starting enhanced documentation workflow...")
    workflow = create_documentation_workflow()
    
    state = DocumentationState(
        repo_path=repo_path,
        repo_name=repo_name,
        file_contents=file_contents,
        file_structure={},
        code_analysis={},
        project_type="",
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
            "last_updated": datetime.now().isoformat(),
            "files_analyzed": len(file_contents),
            "functions_found": len(final_state.get('code_analysis', {}).get('all_functions', [])),
            "classes_found": len(final_state.get('code_analysis', {}).get('all_classes', [])),
            "project_type": final_state.get('project_type', 'Unknown')
        }
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n{'='*70}")
        print(f"✅ SUCCESS: Production documentation generated for {repo_name}")
        print(f"🎯 Project Type: {final_state.get('project_type', 'Unknown')}")
        print(f"{'='*70}\n")
        return f"Success: {final_state.get('project_type', 'Unknown')} docs for {repo_name}"
    else:
        error_msg = final_state.get('error_message', 'unknown error')
        print(f"\n{'='*70}")
        print(f"❌ FAILED: {repo_name}")
        print(f"Error: {error_msg}")
        print(f"{'='*70}\n")
        return f"Failed: {error_msg}"


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def process_all_repositories(base_path="data/github_repos"):
    """Process all repositories with enhanced documentation"""
    print("\n" + "="*70)
    print("🚀 ENHANCED DOCUMENTATION GENERATOR v3.0")
    print("✨ With Architecture Diagrams & Improved Prompts")
    print("="*70 + "\n")
    
    base = Path(base_path)
    
    if not base.exists():
        print(f"⚠️ Directory {base} does not exist. Creating...")
        base.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created folder '{base}'")
        print("⚠️ No repositories to process.")
        return
    
    repos = [d for d in base.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    if not repos:
        print(f"⚠️ No repositories found in {base_path}")
        return
    
    print(f"📦 Found {len(repos)} repositories:\n")
    for i, repo in enumerate(repos, 1):
        print(f"   {i}. {repo.name}")
    print()
    
    results = []
    start_time = time.time()
    
    for i, repo in enumerate(repos, 1):
        print(f"\n{'▼'*70}")
        print(f"📍 Processing {i}/{len(repos)}: {repo.name}")
        print(f"{'▼'*70}")
        
        result = process_repository(str(repo), repo.name)
        results.append((repo.name, result))
        time.sleep(2)
    
    elapsed = time.time() - start_time
    print("\n" + "="*70)
    print("📊 DOCUMENTATION GENERATION SUMMARY")
    print("="*70)
    print(f"⏱️  Total time: {elapsed:.2f} seconds ({elapsed/60:.1f} minutes)\n")
    
    success_count = sum(1 for _, r in results if "Success" in r)
    skip_count = sum(1 for _, r in results if "Skipped" in r)
    fail_count = sum(1 for _, r in results if "Failed" in r)
    
    # Group by project type
    project_types = {}
    for repo_name, result in results:
        if "Success" in result:
            ptype = result.split("docs for")[0].replace("Success: ", "").strip()
            project_types[ptype] = project_types.get(ptype, 0) + 1
    
    print("📈 Results by Status:")
    for repo_name, result in results:
        status = "✅" if "Success" in result else ("⏩" if "Skipped" in result else "❌")
        print(f"{status} {repo_name}: {result}")
    
    if project_types:
        print(f"\n📊 Project Types Detected:")
        for ptype, count in sorted(project_types.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {ptype}: {count} project(s)")
    
    print(f"\n📈 Summary: {success_count} successful, {skip_count} skipped, {fail_count} failed")
    print("="*70 + "\n")


# ============================================================================
# SINGLE REPOSITORY PROCESSING (for testing)
# ============================================================================

def process_single_repo(repo_path: str):
    """Process a single repository - useful for testing"""
    return process_repository(repo_path)


if __name__ == "__main__":
    print("=" * 70)
    print("📚 Enhanced Documentation Generator v3.0")
    print("=" * 70)
    print("\n🎯 Features:")
    print("   ✅ Intelligent project type detection")
    print("   ✅ Project-specific documentation templates")
    print("   ✅ Real code extraction and examples")
    print("   ✅ Architecture & flow diagrams (Mermaid)")
    print("   ✅ Enhanced prompts for better accuracy")
    print("   ✅ Detailed code structure sections")
    print("   ✅ ML, API, CLI, Data Analysis support")
    print("\n📖 Usage:")
    print("   from utils.doc_utils import process_all_repositories")
    print("   process_all_repositories('data/github_repos')")
    print("\n   OR for single repo:")
    print("   from utils.doc_utils import process_single_repo")
    print("   process_single_repo('path/to/repo')")
    print("=" * 70)