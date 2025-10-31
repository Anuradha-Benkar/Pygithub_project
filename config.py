# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # GitHub token
# GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# # Groq API key
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# # Qdrant Configuration
# QDRANT_URL = os.getenv("QDRANT_URL")
# QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
# COLLECTION_NAME = os.getenv("COLLECTION_NAME", "github_repos")

# # Paths
# BASE_PATH = "data"
# REPOS_DOWNLOAD_DIR = os.path.join(BASE_PATH, "github_repos")
# DOCS_DIR = "repos_docs2"
# EMBED_DIR = os.path.join(BASE_PATH, "qdrant_embeddings")  # Not used, kept for compatibility

# # Models
# HF_EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# # Validation
# if not GITHUB_TOKEN:
#     raise ValueError("❌ Missing GITHUB_TOKEN in .env file")

# if not GROQ_API_KEY:
#     raise ValueError("❌ Missing GROQ_API_KEY in .env file")

# if not QDRANT_URL or not QDRANT_API_KEY:
#     raise ValueError("❌ Missing QDRANT_URL or QDRANT_API_KEY in .env file")

# # Create necessary directories
# os.makedirs(REPOS_DOWNLOAD_DIR, exist_ok=True)
# os.makedirs(DOCS_DIR, exist_ok=True)



# # config.py
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # GitHub token
# GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# # Groq API key
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# # Qdrant Configuration
# QDRANT_URL = os.getenv("QDRANT_URL")
# QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
# COLLECTION_NAME = os.getenv("COLLECTION_NAME", "github_repos")

# # Paths
# BASE_PATH = "data"
# REPOS_DOWNLOAD_DIR = os.path.join(BASE_PATH, "github_repos")
# DOCS_DIR = "repos_docs2"
# CHUNKS_DIR = os.path.join(BASE_PATH, "chunks")  # Local chunks storage

# # Models
# HF_EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# # Validation
# if not GITHUB_TOKEN:
#     raise ValueError("❌ Missing GITHUB_TOKEN in .env file")

# if not GROQ_API_KEY:
#     raise ValueError("❌ Missing GROQ_API_KEY in .env file")

# if not QDRANT_URL or not QDRANT_API_KEY:
#     raise ValueError("❌ Missing QDRANT_URL or QDRANT_API_KEY in .env file")

# # Create necessary directories
# os.makedirs(REPOS_DOWNLOAD_DIR, exist_ok=True)
# os.makedirs(DOCS_DIR, exist_ok=True)
# os.makedirs(CHUNKS_DIR, exist_ok=True)

# print("✅ Configuration loaded successfully")
# print(f"📂 Repos dir: {REPOS_DOWNLOAD_DIR}")
# print(f"📄 Docs dir: {DOCS_DIR}")
# print(f"💾 Chunks dir: {CHUNKS_DIR}")
# print(f"☁️  Qdrant URL: {QDRANT_URL}")
# print(f"📦 Collection: {COLLECTION_NAME}")


# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPOS_DOWNLOAD_DIR = "data/github_repos"

# Documentation Configuration
DOCS_DIR = "repos_docs2"
CHUNKS_DIR = "data/chunks"
OUTPUT_LOG_DIR = "data/qa_logs"  # NEW: For storing Q&A logs

# Qdrant Configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "githup_repos")

# Model Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Create directories
os.makedirs(REPOS_DOWNLOAD_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(CHUNKS_DIR, exist_ok=True)
os.makedirs(OUTPUT_LOG_DIR, exist_ok=True)

print("✅ Configuration loaded successfully")
print(f"📂 Repos dir: {REPOS_DOWNLOAD_DIR}")
print(f"📄 Docs dir: {DOCS_DIR}")
print(f"💾 Chunks dir: {CHUNKS_DIR}")
print(f"📋 Logs dir: {OUTPUT_LOG_DIR}")
print(f"☁️  Qdrant URL: {QDRANT_URL}")
print(f"📦 Collection: {COLLECTION_NAME}")