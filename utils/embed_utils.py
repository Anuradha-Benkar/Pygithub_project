# import os
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_chroma import Chroma

# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import TextLoader
# from langgraph.graph import StateGraph, START, END
# from config import DOCS_DIR, EMBED_DIR, HF_EMBED_MODEL

# def run_embedding_pipeline():
#     os.makedirs(EMBED_DIR, exist_ok=True)
#     embedding_model = HuggingFaceEmbeddings(model_name=HF_EMBED_MODEL)

#     class DocState(dict): pass

#     def load_file(state: DocState) -> DocState:
#         loader = TextLoader(state["file_path"], encoding="utf-8")
#         state["documents"] = loader.load()
#         return state

#     def split_text(state: DocState) -> DocState:
#         splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#         state["splits"] = splitter.split_documents(state["documents"])
#         return state

#     def embed_and_store(state: DocState) -> DocState:
#         file_name = os.path.basename(state["file_path"]).replace(".md", "")
#         db_path = os.path.join(EMBED_DIR, file_name)
#         vectordb = Chroma.from_documents(state["splits"], embedding_model, persist_directory=db_path)
#         vectordb.persist()
#         state["db_path"] = db_path
#         return state

#     graph = StateGraph(DocState)
#     graph.add_node("load_file", load_file)
#     graph.add_node("split_text", split_text)
#     graph.add_node("embed_and_store", embed_and_store)
#     graph.add_edge(START, "load_file")
#     graph.add_edge("load_file", "split_text")
#     graph.add_edge("split_text", "embed_and_store")
#     graph.add_edge("embed_and_store", END)
#     workflow = graph.compile()

#     for filename in os.listdir(DOCS_DIR):
#         if filename.endswith(".md"):
#             file_path = os.path.join(DOCS_DIR, filename)
#             workflow.invoke({"file_path": file_path})

#     return {"status": "✅ Embeddings created"}



# # utils/embed_utils.py
# import os
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_chroma import Chroma
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import TextLoader
# from langgraph.graph import StateGraph, START, END

# DOCS_DIR = "repos_docs2"
# EMBED_DIR = os.path.join("data", "chromadb_embedding")
# HF_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# def run_embedding_pipeline():
#     os.makedirs(EMBED_DIR, exist_ok=True)
#     embedding_model = HuggingFaceEmbeddings(model_name=HF_EMBED_MODEL)

#     # ---- Define State ----
#     class DocState(dict):
#         """Shared state between graph nodes"""
#         file_path: str
#         documents: list
#         splits: list
#         db_path: str

#     # ---- Node Functions ----
#     def load_file(state: DocState) -> DocState:
#         loader = TextLoader(state["file_path"], encoding="utf-8")
#         state["documents"] = loader.load()
#         print(f"📂 Loaded file: {state['file_path']}")
#         return state

#     def split_text(state: DocState) -> DocState:
#         splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#         state["splits"] = splitter.split_documents(state["documents"])
#         print(f"✂️ Split into {len(state['splits'])} chunks")
#         return state

#     def embed_and_store(state: DocState) -> DocState:
#         file_name = os.path.basename(state["file_path"]).replace(".md", "")
#         db_path = os.path.join(EMBED_DIR, file_name)

#         vectordb = Chroma.from_documents(
#             documents=state["splits"],
#             embedding=embedding_model,
#             persist_directory=db_path,  # persistence handled here
#     )

#     # vectordb.persist()  ❌ not needed with langchain_chroma

#         state["db_path"] = db_path
#         print(f"💾 Stored embeddings at: {db_path}")
#         return state

#     # ---- Build Graph ----
#     graph = StateGraph(DocState)
#     graph.add_node("load_file", load_file)
#     graph.add_node("split_text", split_text)
#     graph.add_node("embed_and_store", embed_and_store)

#     graph.add_edge(START, "load_file")
#     graph.add_edge("load_file", "split_text")
#     graph.add_edge("split_text", "embed_and_store")
#     graph.add_edge("embed_and_store", END)

#     workflow = graph.compile()

#     # ---- Run for all docs ----
#     results = []
#     for filename in os.listdir(DOCS_DIR):
#         if filename.endswith(".md"):
#             file_path = os.path.join(DOCS_DIR, filename)
#             state = workflow.invoke({"file_path": file_path})
#             results.append(state)

#     return {
#         "status": "✅ Embeddings created",
#         "processed_files": [r["file_path"] for r in results],
#         "embed_dirs": [r["db_path"] for r in results],
#     }


# if __name__ == "__main__":
#     result = run_embedding_pipeline()
#     print(f"✅ Embedding complete: {result}")








# # utils/embed_utils.py
# import os
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_qdrant import QdrantVectorStore
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import TextLoader
# from langgraph.graph import StateGraph, START, END
# from qdrant_client import QdrantClient
# from qdrant_client.models import Distance, VectorParams
# from config import (
#     DOCS_DIR, 
#     QDRANT_URL, 
#     QDRANT_API_KEY, 
#     COLLECTION_NAME,
#     HF_EMBED_MODEL
# )

# def run_embedding_pipeline():
#     """
#     Run embedding pipeline with Qdrant Cloud storage
#     """
#     # Initialize Qdrant client
#     qdrant_client = QdrantClient(
#         url=QDRANT_URL,
#         api_key=QDRANT_API_KEY,
#     )
    
#     # Initialize embeddings
#     embedding_model = HuggingFaceEmbeddings(model_name=HF_EMBED_MODEL)
    
#     # Get embedding dimension (required for Qdrant)
#     sample_embedding = embedding_model.embed_query("test")
#     embedding_dim = len(sample_embedding)
    
#     print(f"🔢 Embedding dimension: {embedding_dim}")
    
#     # Check if collection exists, create if not
#     collections = qdrant_client.get_collections().collections
#     collection_names = [col.name for col in collections]
    
#     if COLLECTION_NAME not in collection_names:
#         print(f"📦 Creating new collection: {COLLECTION_NAME}")
#         qdrant_client.create_collection(
#             collection_name=COLLECTION_NAME,
#             vectors_config=VectorParams(
#                 size=embedding_dim,
#                 distance=Distance.COSINE
#             )
#         )
#     else:
#         print(f"✅ Using existing collection: {COLLECTION_NAME}")
#         # Optional: Uncomment below to delete and recreate each time
#         # print(f"🗑️ Deleting existing collection: {COLLECTION_NAME}")
#         # qdrant_client.delete_collection(collection_name=COLLECTION_NAME)
#         # print(f"📦 Creating collection: {COLLECTION_NAME}")
#         # qdrant_client.create_collection(
#         #     collection_name=COLLECTION_NAME,
#         #     vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE)
#         # )

#     # ---- Define State ----
#     class DocState(dict):
#         """Shared state between graph nodes"""
#         file_path: str
#         repo_name: str
#         documents: list
#         splits: list
#         processed: bool

#     # ---- Node Functions ----
#     def load_file(state: DocState) -> DocState:
#         try:
#             loader = TextLoader(state["file_path"], encoding="utf-8")
#             state["documents"] = loader.load()
#             print(f"📂 Loaded file: {os.path.basename(state['file_path'])}")
#         except Exception as e:
#             print(f"❌ Error loading {state['file_path']}: {e}")
#             state["documents"] = []
#         return state

#     def split_text(state: DocState) -> DocState:
#         if not state.get("documents"):
#             state["splits"] = []
#             return state
            
#         splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000, 
#             chunk_overlap=200
#         )
#         state["splits"] = splitter.split_documents(state["documents"])
        
#         # Add metadata with repo name
#         for doc in state["splits"]:
#             doc.metadata["repo_name"] = state["repo_name"]
#             doc.metadata["source_file"] = os.path.basename(state["file_path"])
        
#         print(f"✂️ Split into {len(state['splits'])} chunks")
#         return state

#     def embed_and_store(state: DocState) -> DocState:
#         if not state.get("splits"):
#             print("⚠️ No splits to embed")
#             state["processed"] = False
#             return state
            
#         try:
#             # Store in Qdrant
#             QdrantVectorStore.from_documents(
#                 documents=state["splits"],
#                 embedding=embedding_model,
#                 url=QDRANT_URL,
#                 api_key=QDRANT_API_KEY,
#                 collection_name=COLLECTION_NAME,
#             )
            
#             print(f"💾 Stored {len(state['splits'])} chunks in Qdrant collection '{COLLECTION_NAME}'")
#             state["processed"] = True
            
#         except Exception as e:
#             print(f"❌ Error storing embeddings: {e}")
#             state["processed"] = False
            
#         return state

#     # ---- Build Graph ----
#     graph = StateGraph(DocState)
#     graph.add_node("load_file", load_file)
#     graph.add_node("split_text", split_text)
#     graph.add_node("embed_and_store", embed_and_store)

#     graph.add_edge(START, "load_file")
#     graph.add_edge("load_file", "split_text")
#     graph.add_edge("split_text", "embed_and_store")
#     graph.add_edge("embed_and_store", END)

#     workflow = graph.compile()

#     # ---- Run for all docs ----
#     if not os.path.exists(DOCS_DIR):
#         print(f"❌ Docs directory not found: {DOCS_DIR}")
#         return {
#             "status": "❌ No docs directory found",
#             "processed_files": [],
#             "total_chunks": 0
#         }
    
#     results = []
#     total_chunks = 0
    
#     md_files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".md")]
    
#     if not md_files:
#         print(f"⚠️ No .md files found in {DOCS_DIR}")
#         return {
#             "status": "⚠️ No documentation files found",
#             "processed_files": [],
#             "total_chunks": 0
#         }
    
#     print(f"\n📚 Processing {len(md_files)} documentation files...\n")
    
#     for filename in md_files:
#         file_path = os.path.join(DOCS_DIR, filename)
#         # Extract repo name from filename (assumes format: reponame_documentation.md)
#         repo_name = filename.replace("_documentation.md", "")
        
#         print(f"\n{'='*50}")
#         print(f"Processing: {filename}")
#         print(f"Repo: {repo_name}")
#         print(f"{'='*50}")
        
#         state = workflow.invoke({
#             "file_path": file_path,
#             "repo_name": repo_name,
#             "processed": False
#         })
        
#         if state.get("processed"):
#             results.append(state)
#             total_chunks += len(state.get("splits", []))

#     # Get collection info
#     collection_info = qdrant_client.get_collection(collection_name=COLLECTION_NAME)
    
#     print(f"\n{'='*50}")
#     print(f"✅ Embedding Pipeline Complete")
#     print(f"{'='*50}")
#     print(f"📊 Total files processed: {len(results)}")
#     print(f"📦 Total chunks stored: {total_chunks}")
#     print(f"🔢 Vectors in collection: {collection_info.vectors_count}")
#     print(f"{'='*50}\n")

#     return {
#         "status": "✅ Embeddings created in Qdrant",
#         "processed_files": [r["file_path"] for r in results],
#         "total_chunks": total_chunks,
#         "collection_name": COLLECTION_NAME
#     }


# if __name__ == "__main__":
#     result = run_embedding_pipeline()
#     print(f"\n✅ Final Result: {result}")






# # utils/embed_utils.py
# import os
# import json
# from pathlib import Path
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_qdrant import QdrantVectorStore
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import TextLoader
# from qdrant_client import QdrantClient
# from qdrant_client.models import Distance, VectorParams
# from config import (
#     DOCS_DIR, 
#     QDRANT_URL, 
#     QDRANT_API_KEY, 
#     COLLECTION_NAME,
#     HF_EMBED_MODEL,
#     CHUNKS_DIR
# )


# def initialize_qdrant_collection(embedding_model):
#     """
#     Initialize Qdrant collection with proper configuration
#     """
#     print(f"\n{'='*60}")
#     print("🔧 Initializing Qdrant Collection")
#     print(f"{'='*60}")
    
#     try:
#         # Initialize Qdrant client
#         qdrant_client = QdrantClient(
#             url=QDRANT_URL,
#             api_key=QDRANT_API_KEY,
#         )
#         print(f"✅ Connected to Qdrant Cloud: {QDRANT_URL}")
        
#         # Get embedding dimension
#         sample_embedding = embedding_model.embed_query("test")
#         embedding_dim = len(sample_embedding)
#         print(f"📏 Embedding dimension: {embedding_dim}")
        
#         # Check if collection exists
#         collections = qdrant_client.get_collections().collections
#         collection_names = [col.name for col in collections]
        
#         if COLLECTION_NAME in collection_names:
#             print(f"📦 Collection '{COLLECTION_NAME}' already exists")
            
#             # Optional: Delete and recreate for fresh start
#             recreate = input("🔄 Recreate collection? (y/n): ").strip().lower()
#             if recreate == 'y':
#                 print(f"🗑️  Deleting existing collection...")
#                 qdrant_client.delete_collection(collection_name=COLLECTION_NAME)
#                 print(f"✅ Collection deleted")
                
#                 print(f"📦 Creating new collection...")
#                 qdrant_client.create_collection(
#                     collection_name=COLLECTION_NAME,
#                     vectors_config=VectorParams(
#                         size=embedding_dim,
#                         distance=Distance.COSINE
#                     )
#                 )
#                 print(f"✅ Collection '{COLLECTION_NAME}' created successfully")
#             else:
#                 print(f"⏩ Using existing collection")
#         else:
#             # Create new collection
#             print(f"📦 Creating collection: {COLLECTION_NAME}")
#             qdrant_client.create_collection(
#                 collection_name=COLLECTION_NAME,
#                 vectors_config=VectorParams(
#                     size=embedding_dim,
#                     distance=Distance.COSINE
#                 )
#             )
#             print(f"✅ Collection '{COLLECTION_NAME}' created successfully")
        
#         print(f"{'='*60}\n")
#         return qdrant_client
        
#     except Exception as e:
#         print(f"❌ Error initializing Qdrant collection: {e}")
#         raise


# def save_chunks_locally(chunks, repo_name):
#     """
#     Save text chunks locally for reference
#     """
#     chunks_file = os.path.join(CHUNKS_DIR, f"{repo_name}_chunks.json")
    
#     chunks_data = []
#     for i, chunk in enumerate(chunks):
#         chunks_data.append({
#             "chunk_id": i,
#             "content": chunk.page_content,
#             "metadata": chunk.metadata
#         })
    
#     with open(chunks_file, 'w', encoding='utf-8') as f:
#         json.dump(chunks_data, f, indent=2, ensure_ascii=False)
    
#     print(f"💾 Saved {len(chunks)} chunks to {chunks_file}")


# def run_embedding_pipeline():
#     """
#     Run embedding pipeline with Qdrant Cloud storage
#     """
#     print(f"\n{'='*60}")
#     print("🚀 Starting Embedding Pipeline")
#     print(f"{'='*60}\n")
    
#     # Initialize embeddings
#     print("🤖 Loading embedding model...")
#     embedding_model = HuggingFaceEmbeddings(model_name=HF_EMBED_MODEL)
#     print(f"✅ Model loaded: {HF_EMBED_MODEL}")
    
#     # Initialize Qdrant collection
#     qdrant_client = initialize_qdrant_collection(embedding_model)
    
#     # Check docs directory
#     if not os.path.exists(DOCS_DIR):
#         print(f"❌ Docs directory not found: {DOCS_DIR}")
#         return {
#             "status": "❌ No docs directory found",
#             "processed_files": [],
#             "total_chunks": 0
#         }
    
#     # Get markdown files
#     md_files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".md")]
    
#     if not md_files:
#         print(f"⚠️  No .md files found in {DOCS_DIR}")
#         return {
#             "status": "⚠️ No documentation files found",
#             "processed_files": [],
#             "total_chunks": 0
#         }
    
#     print(f"📚 Found {len(md_files)} documentation files\n")
    
#     # Process each file
#     processed_files = []
#     total_chunks = 0
    
#     # Text splitter
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200,
#         length_function=len,
#     )
    
#     for filename in md_files:
#         file_path = os.path.join(DOCS_DIR, filename)
#         repo_name = filename.replace("_documentation.md", "")
        
#         print(f"\n{'='*50}")
#         print(f"📄 Processing: {filename}")
#         print(f"📂 Repo: {repo_name}")
#         print(f"{'='*50}")
        
#         try:
#             # Load document
#             loader = TextLoader(file_path, encoding="utf-8")
#             documents = loader.load()
#             print(f"✅ Loaded document")
            
#             # Split into chunks
#             chunks = text_splitter.split_documents(documents)
#             print(f"✂️  Split into {len(chunks)} chunks")
            
#             # Add metadata
#             for chunk in chunks:
#                 chunk.metadata["repo_name"] = repo_name
#                 chunk.metadata["source_file"] = filename
            
#             # Save chunks locally
#             save_chunks_locally(chunks, repo_name)
            
#             # Store in Qdrant Cloud
#             print(f"☁️  Uploading to Qdrant Cloud...")
#             QdrantVectorStore.from_documents(
#                 documents=chunks,
#                 embedding=embedding_model,
#                 url=QDRANT_URL,
#                 api_key=QDRANT_API_KEY,
#                 collection_name=COLLECTION_NAME,
#             )
#             print(f"✅ Uploaded {len(chunks)} chunks to Qdrant")
            
#             processed_files.append(file_path)
#             total_chunks += len(chunks)
            
#         except Exception as e:
#             print(f"❌ Error processing {filename}: {e}")
#             import traceback
#             traceback.print_exc()
    
#     # Get final collection info
#     collection_info = qdrant_client.get_collection(collection_name=COLLECTION_NAME)
    
#     print(f"\n{'='*60}")
#     print("✅ Embedding Pipeline Complete")
#     print(f"{'='*60}")
#     print(f"📊 Files processed: {len(processed_files)}")
#     print(f"📦 Total chunks created: {total_chunks}")
#     #print(f"☁️  Vectors in Qdrant: {collection_info.vectors_count}")
#     # AFTER (CORRECT)
#     vectors_count = collection_info.points_count if hasattr(collection_info, 'points_count') else collection_info.vectors_count or 0
#     print(f"☁️  Vectors in Qdrant: {vectors_count}")
#     print(f"💾 Chunks saved locally: {CHUNKS_DIR}")
#     print(f"{'='*60}\n")
    
#     return {
#         "status": "✅ Embeddings created in Qdrant Cloud",
#         "processed_files": processed_files,
#         "total_chunks": total_chunks,
#         "collection_name": COLLECTION_NAME,
#         #"vectors_in_cloud": collection_info.vectors_count
#         "vectors_in_cloud": vectors_count
#     }


# if __name__ == "__main__":
#     result = run_embedding_pipeline()
#     print(f"\n✅ Final Result: {result}")







#################### test 3 #############################
# utils/embed_utils.py
import os
import json
import time
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from config import (
    DOCS_DIR, 
    QDRANT_URL, 
    QDRANT_API_KEY, 
    COLLECTION_NAME,
    HF_EMBED_MODEL,
    CHUNKS_DIR
)


# def initialize_qdrant_collection(embedding_model, force_recreate=False):
#     """
#     Initialize Qdrant collection - only creates if doesn't exist
#     """
#     print(f"\n{'='*60}")
#     print("🔧 Initializing Qdrant Collection")
#     print(f"{'='*60}")
    
#     try:
#         client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
#         print(f"✅ Connected to Qdrant: {QDRANT_URL}")
        
#         # Get embedding dimension
#         sample_embedding = embedding_model.embed_query("test")
#         embedding_dim = len(sample_embedding)
#         print(f"📏 Embedding dimension: {embedding_dim}")
        
#         # Check existing collections
#         collections = client.get_collections().collections
#         collection_names = [col.name for col in collections]
        
#         if COLLECTION_NAME in collection_names:
#             if force_recreate:
#                 print(f"🗑️  Deleting existing collection for fresh start...")
#                 client.delete_collection(collection_name=COLLECTION_NAME)
#                 print(f"✅ Collection deleted")
#             else:
#                 print(f"✅ Collection '{COLLECTION_NAME}' already exists")
#                 print(f"⏩ Skipping collection creation")
#                 print(f"{'='*60}\n")
#                 return client
        
#         # Create new collection
#         print(f"📦 Creating new collection: {COLLECTION_NAME}")
#         client.create_collection(
#             collection_name=COLLECTION_NAME,
#             vectors_config=VectorParams(
#                 size=embedding_dim,
#                 distance=Distance.COSINE
#             )
#         )
#         print(f"✅ Collection '{COLLECTION_NAME}' created successfully")
        
#         # ✅ CREATE PAYLOAD INDEX FOR FILTERING
#         print(f"🔑 Creating payload index for metadata.repo_name...")
#         from qdrant_client.models import PayloadSchemaType
        
#         client.create_payload_index(
#             collection_name=COLLECTION_NAME,
#             field_name="metadata.repo_name",
#             field_schema=PayloadSchemaType.KEYWORD
#         )
#         print(f"✅ Payload index created successfully")
        
#         print(f"{'='*60}\n")
        
#         return client
        
#     except Exception as e:
#         print(f"❌ Error initializing collection: {e}")
#         import traceback
#         traceback.print_exc()
#         raise

def initialize_qdrant_collection(embedding_model, force_recreate=False):
    """
    Initialize Qdrant collection - only creates if doesn't exist
    """
    print(f"\n{'='*60}")
    print("🔧 Initializing Qdrant Collection")
    print(f"{'='*60}")
    
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        print(f"✅ Connected to Qdrant: {QDRANT_URL}")
        
        # Get embedding dimension
        sample_embedding = embedding_model.embed_query("test")
        embedding_dim = len(sample_embedding)
        print(f"📏 Embedding dimension: {embedding_dim}")
        
        # Check existing collections
        collections = client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        if COLLECTION_NAME in collection_names:
            if force_recreate:
                print(f"🗑️  Deleting existing collection for fresh start...")
                client.delete_collection(collection_name=COLLECTION_NAME)
                print(f"✅ Collection deleted")
            else:
                print(f"✅ Collection '{COLLECTION_NAME}' already exists")
                print(f"⏩ Skipping collection creation")
                print(f"{'='*60}\n")
                return client
        
        # Create new collection
        print(f"📦 Creating new collection: {COLLECTION_NAME}")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=embedding_dim,
                distance=Distance.COSINE
            )
        )
        print(f"✅ Collection '{COLLECTION_NAME}' created successfully")
        
        # ✅ CREATE PAYLOAD INDEX FOR FILTERING
        print(f"🔑 Creating payload index for metadata.repo_name...")
        from qdrant_client.models import PayloadSchemaType
        
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="metadata.repo_name",
            field_schema=PayloadSchemaType.KEYWORD
        )
        print(f"✅ Payload index created successfully")
        
        print(f"{'='*60}\n")
        
        return client
        
    except Exception as e:
        print(f"❌ Error initializing collection: {e}")
        import traceback
        traceback.print_exc()
        raise


def save_chunks_locally(chunks, repo_name):
    """
    Save chunks to local JSON file
    """
    chunks_file = os.path.join(CHUNKS_DIR, f"{repo_name}_chunks.json")
    
    # Check if already exists
    if os.path.exists(chunks_file):
        print(f"⏩ Chunks file already exists: {chunks_file}")
        return
    
    chunks_data = []
    for i, chunk in enumerate(chunks):
        chunks_data.append({
            "chunk_id": i,
            "content": chunk.page_content,
            "metadata": chunk.metadata
        })
    
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump(chunks_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved {len(chunks)} chunks to: {chunks_file}")


def check_if_already_embedded(repo_name):
    """
    Check if repo is already embedded in Qdrant
    """
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
        # Try to scroll and find this repo
        records, _ = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=10,
            with_payload=True,
            with_vectors=False
        )
        
        for record in records:
            if record.payload and "metadata" in record.payload:
                if record.payload["metadata"].get("repo_name") == repo_name:
                    print(f"✅ Repo '{repo_name}' already embedded")
                    return True
        
        print(f"🆕 Repo '{repo_name}' not found in collection")
        return False
        
    except:
        return False


def run_embedding_pipeline(force_recreate=False):
    """
    Main embedding pipeline - creates embeddings and stores in Qdrant
    """
    print(f"\n{'='*60}")
    print("🚀 Starting Embedding Pipeline")
    print(f"{'='*60}\n")
    
    # Check docs directory
    if not os.path.exists(DOCS_DIR):
        print(f"❌ Docs directory not found: {DOCS_DIR}")
        return {
            "status": "❌ No docs directory",
            "processed_files": [],
            "total_chunks": 0
        }
    
    # Get markdown files
    md_files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".md")]
    
    if not md_files:
        print(f"⚠️  No .md files in {DOCS_DIR}")
        return {
            "status": "⚠️ No documentation files",
            "processed_files": [],
            "total_chunks": 0
        }
    
    print(f"📚 Found {len(md_files)} documentation files")
    
    # Initialize embedding model
    print(f"\n🤖 Loading embedding model: {HF_EMBED_MODEL}")
    embedding_model = HuggingFaceEmbeddings(model_name=HF_EMBED_MODEL)
    print(f"✅ Model loaded successfully")
    
    # Initialize collection
    qdrant_client = initialize_qdrant_collection(embedding_model, force_recreate)
    
    # Text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    processed_files = []
    total_chunks = 0
    skipped_repos = 0
    
    for filename in md_files:
        file_path = os.path.join(DOCS_DIR, filename)
        repo_name = filename.replace("_documentation.md", "")
        
        print(f"\n{'='*50}")
        print(f"📄 Processing: {filename}")
        print(f"📂 Repository: {repo_name}")
        print(f"{'='*50}")
        
        # Check if already embedded (unless force recreate)
        if not force_recreate and check_if_already_embedded(repo_name):
            skipped_repos += 1
            print(f"⏩ Skipping (already embedded)")
            continue
        
        try:
            # Load document
            print(f"📖 Loading document...")
            loader = TextLoader(file_path, encoding="utf-8")
            documents = loader.load()
            print(f"✅ Document loaded")
            
            # Split into chunks
            print(f"✂️  Splitting into chunks...")
            chunks = text_splitter.split_documents(documents)
            print(f"✅ Created {len(chunks)} chunks")
            
            # Add metadata
            for chunk in chunks:
                chunk.metadata["repo_name"] = repo_name
                chunk.metadata["source_file"] = filename
            
            # Save chunks locally
            print(f"💾 Saving chunks locally...")
            save_chunks_locally(chunks, repo_name)
            
            # Upload to Qdrant
            print(f"☁️  Uploading to Qdrant Cloud...")
            QdrantVectorStore.from_documents(
                documents=chunks,
                embedding=embedding_model,
                url=QDRANT_URL,
                api_key=QDRANT_API_KEY,
                collection_name=COLLECTION_NAME,
            )
            
            # Small delay to ensure indexing
            time.sleep(1)
            
            print(f"✅ Successfully uploaded {len(chunks)} chunks")
            
            processed_files.append(file_path)
            total_chunks += len(chunks)
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            import traceback
            traceback.print_exc()
    
    # Wait for final indexing
    print(f"\n⏳ Waiting for final indexing...")
    time.sleep(3)
    
    # Get final stats
    collection_info = qdrant_client.get_collection(collection_name=COLLECTION_NAME)
    vectors_count = collection_info.points_count if hasattr(collection_info, 'points_count') else 0
    
    print(f"\n{'='*60}")
    print("✅ Embedding Pipeline Complete")
    print(f"{'='*60}")
    print(f"📊 Files processed: {len(processed_files)}")
    print(f"⏩ Files skipped: {skipped_repos}")
    print(f"📦 Total chunks created: {total_chunks}")
    print(f"☁️  Vectors in Qdrant: {vectors_count}")
    print(f"💾 Chunks saved to: {CHUNKS_DIR}")
    print(f"{'='*60}\n")
    
    return {
        "status": "✅ Embeddings created successfully",
        "processed_files": processed_files,
        "skipped_files": skipped_repos,
        "total_chunks": total_chunks,
        "collection_name": COLLECTION_NAME,
        "vectors_in_cloud": vectors_count
    }